"""Enhanced Gold Trading Bot with SignalR Real-time Data Integration"""
import asyncio
from datetime import datetime
from typing import Dict, Optional, List

from src.core.base_bot import BaseGoldBot
from src.api.topstep_client import TopStepXClient
from src.api.topstep_realtime_integration import TopStepXRealTimeDataManager, BotRealTimeIntegration
from src.utils.logger_setup import logger
from src.config import Config


class RealTimeGoldBot(BaseGoldBot):
    """Gold Trading Bot with Real-time SignalR data integration"""
    
    def __init__(self):
        super().__init__()
        self.client = TopStepXClient()
        self.realtime_manager = TopStepXRealTimeDataManager()
        self.rt_integration = None
        
        # Real-time data flags
        self.use_realtime_data = True
        self.realtime_connected = False
        
        # Contract tracking
        self.mgc_contract_id = None
        
        # Enhanced market state
        self.last_quote = None
        self.order_book_imbalance = 0.0
        self.recent_trade_momentum = 0.0
        
        logger.info("Real-time Gold Trading Bot initialized")
    
    async def connect(self) -> bool:
        """Connect to TopStepX API and SignalR"""
        try:
            # Connect to REST API first
            if not await self.client.connect():
                logger.error("Failed to connect to TopStepX API")
                return False
            
            # Get MGC contract ID
            contract = await self.client._get_contract_by_symbol("MGC")
            if contract:
                self.mgc_contract_id = contract.get("id")
                logger.info(f"Found MGC contract: {self.mgc_contract_id}")
            else:
                logger.error("Could not find MGC contract")
                return False
            
            # Initialize SignalR with JWT token
            if self.use_realtime_data and self.client.session_token:
                logger.info("Initializing real-time data connection...")
                
                self.realtime_connected = await self.realtime_manager.initialize(
                    self.client.session_token
                )
                
                if self.realtime_connected:
                    # Subscribe to MGC real-time data
                    await self.realtime_manager.subscribe_to_contracts([self.mgc_contract_id])
                    
                    # Setup integration
                    self.rt_integration = BotRealTimeIntegration(self.realtime_manager)
                    
                    # Register custom callbacks
                    self._setup_realtime_callbacks()
                    
                    logger.info("Real-time data connection established")
                else:
                    logger.warning("Failed to connect real-time data - falling back to REST API")
            
            # Load account info
            await self._update_account_info()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from all services"""
        try:
            if self.realtime_connected:
                await self.realtime_manager.disconnect()
            
            await self.client.disconnect()
            logger.info("Disconnected from all services")
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    def _setup_realtime_callbacks(self) -> None:
        """Setup custom real-time data callbacks"""
        
        def on_quote_update(contract_id: str, quote: Dict) -> None:
            """Handle real-time quote updates"""
            if contract_id == self.mgc_contract_id:
                self.last_quote = quote
                self.current_price = quote.get("last", 0)
                
                # Update spread monitoring
                bid = quote.get("bid", 0)
                ask = quote.get("ask", 0)
                if bid and ask:
                    spread = ask - bid
                    if spread <= 0.10:  # Tight spread
                        logger.debug(f"Tight spread: ${spread:.2f}")
        
        def on_trade_update(contract_id: str, trade: Dict) -> None:
            """Handle real-time trade updates"""
            if contract_id == self.mgc_contract_id:
                # Update trade momentum
                self._update_trade_momentum(trade)
        
        def on_depth_update(contract_id: str, depth: Dict) -> None:
            """Handle order book updates"""
            if contract_id == self.mgc_contract_id:
                self.order_book_imbalance = self.realtime_manager.get_order_book_imbalance(
                    contract_id
                )
        
        # Register callbacks
        self.realtime_manager.on_quote_update(on_quote_update)
        self.realtime_manager.on_trade_update(on_trade_update)
        self.realtime_manager.on_depth_update(on_depth_update)
    
    def _update_trade_momentum(self, trade: Dict) -> None:
        """Update recent trade momentum indicator"""
        # Simple momentum based on recent trades
        recent_trades = self.realtime_manager.get_recent_trades(self.mgc_contract_id, limit=20)
        
        if len(recent_trades) >= 5:
            buy_volume = sum(t.get("size", 0) for t in recent_trades if t.get("side") == "Buy")
            sell_volume = sum(t.get("size", 0) for t in recent_trades if t.get("side") == "Sell")
            
            total_volume = buy_volume + sell_volume
            if total_volume > 0:
                self.recent_trade_momentum = (buy_volume - sell_volume) / total_volume
    
    async def get_market_data(self) -> Optional[Dict]:
        """Get market data from real-time feed or REST API"""
        try:
            # Try real-time data first
            if self.realtime_connected and not self.realtime_manager.is_data_stale():
                quote = self.realtime_manager.get_latest_quote(self.mgc_contract_id)
                if quote:
                    return {
                        "symbol": "MGC",
                        "bid": quote.get("bid", 0),
                        "ask": quote.get("ask", 0),
                        "last": quote.get("last", 0),
                        "volume": quote.get("volume", 0),
                        "timestamp": quote.get("timestamp"),
                        "source": "realtime"
                    }
            
            # Fallback to REST API
            data = await self.client.get_market_data("MGC")
            if data:
                data["source"] = "rest"
            return data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
    
    async def calculate_indicators(self, candles: List[Dict]) -> Dict:
        """Calculate enhanced indicators using real-time data"""
        indicators = await super().calculate_indicators(candles)
        
        # Add real-time enhancements
        if self.realtime_connected:
            indicators["order_book_imbalance"] = self.order_book_imbalance
            indicators["trade_momentum"] = self.recent_trade_momentum
            
            # Volume profile analysis
            volume_profile = self.realtime_manager.get_volume_profile(
                self.mgc_contract_id, 
                minutes=15
            )
            
            if volume_profile:
                # Find high volume nodes (support/resistance)
                sorted_levels = sorted(
                    volume_profile.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                if sorted_levels:
                    indicators["high_volume_price"] = sorted_levels[0][0]
                    indicators["volume_node_strength"] = sorted_levels[0][1]
        
        return indicators
    
    async def generate_trading_signal(self, indicators: Dict) -> str:
        """Enhanced signal generation with real-time data"""
        signal = "HOLD"
        
        # Get base signal from parent class
        base_signal = await super().generate_trading_signal(indicators)
        
        # Enhance with real-time data
        if self.realtime_connected and base_signal != "HOLD":
            # Check order flow confirmation
            if base_signal == "BUY":
                # Confirm with positive order book and trade momentum
                if self.order_book_imbalance > 0.2 and self.recent_trade_momentum > 0.1:
                    signal = "BUY"
                    logger.info("BUY signal confirmed by real-time order flow")
                else:
                    logger.info("BUY signal NOT confirmed by order flow")
                    
            elif base_signal == "SELL":
                # Confirm with negative order book and trade momentum
                if self.order_book_imbalance < -0.2 and self.recent_trade_momentum < -0.1:
                    signal = "SELL"
                    logger.info("SELL signal confirmed by real-time order flow")
                else:
                    logger.info("SELL signal NOT confirmed by order flow")
        else:
            signal = base_signal
        
        return signal
    
    async def execute_trade(self, signal: str, indicators: Dict) -> bool:
        """Execute trade with real-time price improvement"""
        try:
            if signal == "HOLD":
                return True
            
            # Get real-time quote for best execution
            quote = None
            if self.realtime_connected:
                quote = self.realtime_manager.get_latest_quote(self.mgc_contract_id)
            
            # Prepare order with real-time prices
            if signal == "BUY":
                # Use real-time ask price if available
                limit_price = quote.get("ask") if quote else None
                
                order_data = {
                    "contractId": self.mgc_contract_id,
                    "side": "Buy",
                    "orderType": "Limit" if limit_price else "Market",
                    "quantity": self.config.DEFAULT_POSITION_MGC,
                    "limitPrice": limit_price
                }
                
            else:  # SELL
                # Use real-time bid price if available
                limit_price = quote.get("bid") if quote else None
                
                order_data = {
                    "contractId": self.mgc_contract_id,
                    "side": "Sell",
                    "orderType": "Limit" if limit_price else "Market",
                    "quantity": self.config.DEFAULT_POSITION_MGC,
                    "limitPrice": limit_price
                }
            
            # Place order
            result = await self.client.place_order(order_data)
            
            if result:
                logger.info(f"Order placed successfully: {result.get('orderId')}")
                return True
            else:
                logger.error("Failed to place order")
                return False
                
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False
    
    async def run(self) -> None:
        """Main bot loop with real-time data integration"""
        logger.info("Starting Real-time Gold Trading Bot...")
        self.is_running = True
        
        diagnostics_counter = 0
        
        while self.is_running:
            try:
                # Log diagnostics periodically
                diagnostics_counter += 1
                if diagnostics_counter % 10 == 0:
                    if self.realtime_connected:
                        diagnostics = self.realtime_manager.get_diagnostics()
                        logger.info(f"Real-time diagnostics: {diagnostics}")
                
                # Get candles for analysis
                candles = await self.client.get_historical_data(
                    symbol="MGC",
                    interval=self.config.ANALYSIS_TIMEFRAME,
                    limit=100
                )
                
                if not candles:
                    logger.warning("No historical data available")
                    await asyncio.sleep(30)
                    continue
                
                # Calculate indicators with real-time enhancements
                indicators = await self.calculate_indicators(candles)
                
                # Generate signal with real-time confirmation
                signal = await self.generate_trading_signal(indicators)
                
                # Execute if needed
                if signal != "HOLD":
                    await self.execute_trade(signal, indicators)
                
                # Update monitoring
                await self.update_monitoring_status({
                    "realtime_connected": self.realtime_connected,
                    "order_book_imbalance": self.order_book_imbalance,
                    "trade_momentum": self.recent_trade_momentum
                })
                
                # Sleep based on real-time data availability
                if self.realtime_connected:
                    await asyncio.sleep(5)  # Faster updates with real-time
                else:
                    await asyncio.sleep(30)  # Standard polling
                    
            except Exception as e:
                logger.error(f"Bot loop error: {e}")
                await asyncio.sleep(30)


async def main():
    """Main entry point for real-time bot"""
    bot = RealTimeGoldBot()
    
    try:
        # Connect to services
        if await bot.connect():
            logger.info("Bot connected successfully")
            
            # Run the bot
            await bot.run()
        else:
            logger.error("Failed to connect bot")
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.disconnect()


if __name__ == "__main__":
    asyncio.run(main())