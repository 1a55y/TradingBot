"""Gold Futures Trading Bot - Live Mode with TopStepX API"""
import asyncio
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from src.core.base_bot import BaseGoldBot
from src.api.topstep_client import TopStepXClient
from src.api.mock_topstep_client import MockTopStepXClient
from src.api.topstep_websocket_client import TopStepXWebSocketClient
from src.utils.logger_setup import logger
from src.utils.data_validator import DataValidationError


class LiveGoldBot(BaseGoldBot):
    """Live Gold Trading Bot using TopStepX API"""
    
    def __init__(self, use_mock_api=False):
        super().__init__()
        
        # Use mock API for testing
        if use_mock_api:
            logger.info("Using MOCK API client for testing")
            self.api_client = MockTopStepXClient()
        else:
            self.api_client = TopStepXClient()
            
        self.market_data_buffer = []
        self.last_candle_update = None
        self.candle_cache = {}
        
        # WebSocket client for real-time data
        self.ws_client = None
        self.mgc_contract_id = None
        
        # Real-time price monitoring
        self.last_tick_time = None
        self.tick_count = 0
        
        logger.info("Live Gold Bot initialized with WebSocket support")
        logger.info(f"Trading Symbol: {self.config.SYMBOL}")
        logger.info(f"Market: {self.config.TOPSTEP_MARKET}")
    
    async def connect(self) -> bool:
        """Connect to TopStepX API and WebSocket"""
        try:
            # Connect to REST API first
            if not await self.api_client.connect():
                logger.error("Failed to connect to TopStepX API")
                return False
            
            self.is_running = True
            
            # Get MGC contract ID
            contract = await self.api_client._get_contract_by_symbol("MGC")
            if contract:
                self.mgc_contract_id = contract.get("id")
                logger.info(f"Found MGC contract: {self.mgc_contract_id}")
            else:
                logger.error("Could not find MGC contract")
            
            # Get initial account info
            account_info = await self.api_client.get_account_info()
            if account_info:
                logger.info(f"Connected to account: {account_info.get('username')}")
                logger.info(f"Account balance: ${account_info.get('balance', 0):.2f}")
            
            # Connect WebSocket for real-time data
            if self.mgc_contract_id and not isinstance(self.api_client, MockTopStepXClient):
                logger.info("Connecting to WebSocket for real-time data...")
                self.ws_client = TopStepXWebSocketClient(self.api_client.session_token)
                
                # Register callbacks
                self.ws_client.on_quote(self._handle_quote_update)
                self.ws_client.on_trade(self._handle_trade_update)
                
                if await self.ws_client.connect():
                    # Subscribe to MGC quotes
                    await self.ws_client.subscribe_quotes(self.mgc_contract_id)
                    await self.ws_client.subscribe_trades(self.mgc_contract_id)
                    logger.info("✅ WebSocket connected - receiving real-time data!")
                else:
                    logger.warning("WebSocket connection failed, falling back to REST API")
            
            return True
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from TopStepX API and WebSocket"""
        try:
            self.is_running = False
            
            # Disconnect WebSocket
            if self.ws_client:
                await self.ws_client.disconnect()
            
            # Disconnect API client
            await self.api_client.disconnect()
            
            logger.info("Disconnected from live trading")
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    def _handle_quote_update(self, contract_id: str, quote_data: dict):
        """Handle real-time quote updates from WebSocket"""
        try:
            # Update current price
            bid = quote_data.get('bestBid', 0)
            ask = quote_data.get('bestAsk', 0)
            
            if bid > 0 and ask > 0:
                self.current_price = (bid + ask) / 2
                self.last_tick_time = datetime.now(timezone.utc)
                self.tick_count += 1
                
                # Store tick data for analysis
                self.market_data_buffer.append({
                    'timestamp': self.last_tick_time,
                    'price': self.current_price,
                    'bid': bid,
                    'ask': ask,
                    'bid_size': quote_data.get('bestBidSize', 0),
                    'ask_size': quote_data.get('bestAskSize', 0)
                })
                
                # Keep buffer size manageable
                if len(self.market_data_buffer) > 1000:
                    self.market_data_buffer = self.market_data_buffer[-1000:]
                    
                # Log every 100th tick
                if self.tick_count % 100 == 0:
                    logger.info(f"📊 Real-time Price: ${self.current_price:.2f} | Bid: ${bid:.2f} | Ask: ${ask:.2f} | Ticks: {self.tick_count}")
                    
        except Exception as e:
            logger.error(f"Error handling quote update: {e}")
    
    def _handle_trade_update(self, contract_id: str, trades: list):
        """Handle real-time trade updates from WebSocket"""
        try:
            for trade in trades:
                price = trade.get('price', 0)
                volume = trade.get('volume', 0)
                trade_type = "BUY" if trade.get('type') == 0 else "SELL"
                
                # Log significant trades
                if volume > 10:  # Log larger trades
                    logger.debug(f"Trade: {trade_type} {volume} @ ${price:.2f}")
                    
        except Exception as e:
            logger.error(f"Error handling trade update: {e}")
    
    async def _handle_fill(self, event: Dict) -> None:
        """Handle order fill event"""
        order_id = event.get('order_id')
        fill_price = event.get('fill_price')
        quantity = event.get('quantity')
        side = event.get('side')
        
        logger.info(f"Order filled: {order_id} - {side} {quantity} @ ${fill_price}")
        
        # Update positions
        if order_id in self.positions:
            self.positions[order_id]['status'] = 'filled'
            self.positions[order_id]['fill_price'] = fill_price
    
    async def _handle_reject(self, event: Dict) -> None:
        """Handle order rejection"""
        order_id = event.get('order_id')
        reason = event.get('reason', 'Unknown')
        
        logger.error(f"Order rejected: {order_id} - Reason: {reason}")
        
        # Remove from positions
        if order_id in self.positions:
            del self.positions[order_id]
    
    async def _handle_position_update(self, event: Dict) -> None:
        """Handle position update event"""
        position_data = event.get('position', {})
        pnl = position_data.get('unrealized_pnl', 0)
        
        # Update daily P&L
        self.daily_pnl = pnl
        
        # Check risk limits
        if self.daily_pnl <= -self.config.DAILY_LOSS_LIMIT:
            logger.critical(f"Daily loss limit reached: ${self.daily_pnl:.2f}")
            await self.flatten_all_positions()
    
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Get official exchange candles from REST API for pattern detection"""
        try:
            # Always use REST API for accurate exchange candles
            # WebSocket is only for real-time price monitoring, not candle building
            
            # Check cache first
            cache_key = f"{symbol}_{timeframe}_{limit}"
            now = datetime.now(timezone.utc)
            
            if cache_key in self.candle_cache:
                cached_data, cache_time = self.candle_cache[cache_key]
                if (now - cache_time).seconds < 60:  # 1 minute cache
                    return cached_data
            
            # Fetch from API
            candles_data = await self.api_client.get_historical_data(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            
            if not candles_data:
                logger.error("No candle data received")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(candles_data)
            
            # Rename columns to match expected format
            column_mapping = {
                't': 'timestamp',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            }
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert timestamp (already in ISO format from API)
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            
            # Validate data
            df = self.validator.validate_candles_df(df)
            
            # Cache the result
            self.candle_cache[cache_key] = (df, now)
            
            return df
            
        except DataValidationError as e:
            logger.error(f"Invalid candle data: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting candles: {e}")
            return pd.DataFrame()
    
    async def place_order(self, side: str, quantity: int, stop_price: float, target_price: float) -> bool:
        """Place order via API"""
        try:
            # Use real-time price if available, otherwise get from API
            if self.current_price > 0:
                current_price = self.current_price
                logger.info(f"Using real-time WebSocket price: ${current_price:.2f}")
            else:
                # Fallback to REST API
                market_data = await self.api_client.get_market_data(self.config.SYMBOL)
                if not market_data:
                    logger.error("Cannot get current market price")
                    return False
                current_price = (market_data['bid'] + market_data['ask']) / 2
            
            # Prepare order data
            order_data = {
                "symbol": self.config.SYMBOL,
                "side": side.upper(),
                "quantity": quantity,
                "order_type": "MARKET",
                "time_in_force": "GTC",
                "account_id": self.config.TOPSTEP_ACCOUNT_ID,
                "stop_loss": stop_price,
                "take_profit": target_price
            }
            
            # Calculate risk
            risk = abs(current_price - stop_price) * quantity * self.config.TICK_VALUE
            
            # Risk check
            if risk > self.config.MAX_RISK_PER_TRADE:
                logger.error(f"Risk too high: ${risk:.2f} > ${self.config.MAX_RISK_PER_TRADE}")
                return False
            
            # Paper trading check
            if self.config.PAPER_TRADING:
                logger.info(f"PAPER TRADE: {side} {quantity} MGC @ ${current_price:.2f}")
                logger.info(f"Stop: ${stop_price:.2f}, Target: ${target_price:.2f}, Risk: ${risk:.2f}")
                
                # Simulate order in paper trading
                order_id = f"PAPER_{datetime.now().timestamp()}"
                self.positions[order_id] = {
                    'side': side,
                    'quantity': quantity,
                    'entry_price': current_price,
                    'stop_price': stop_price,
                    'target_price': target_price,
                    'timestamp': datetime.now(timezone.utc),
                    'status': 'filled',
                    'risk': risk
                }
                return True
            
            # Live order
            result = await self.api_client.place_order(order_data)
            if result:
                order_id = result.get('order_id')
                self.positions[order_id] = {
                    'side': side,
                    'quantity': quantity,
                    'entry_price': current_price,
                    'stop_price': stop_price,
                    'target_price': target_price,
                    'timestamp': datetime.now(timezone.utc),
                    'status': 'pending',
                    'risk': risk
                }
                
                logger.info(f"Order placed: {order_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False
    
    async def flatten_all_positions(self) -> None:
        """Emergency flatten all positions"""
        try:
            logger.warning("Flattening all positions")
            
            positions = await self.api_client.get_positions()
            
            for position in positions:
                if position['symbol'] == self.config.SYMBOL:
                    # Place opposite order to close
                    close_side = 'SELL' if position['side'] == 'BUY' else 'BUY'
                    close_order = {
                        "symbol": self.config.SYMBOL,
                        "side": close_side,
                        "quantity": abs(position['quantity']),
                        "order_type": "MARKET",
                        "time_in_force": "IOC",
                        "account_id": self.config.TOPSTEP_ACCOUNT_ID
                    }
                    
                    result = await self.api_client.place_order(close_order)
                    if result:
                        logger.info(f"Closed position: {position['position_id']}")
                    else:
                        logger.error(f"Failed to close position: {position['position_id']}")
                        
        except Exception as e:
            logger.error(f"Error flattening positions: {e}")
    
    async def update_monitoring(self) -> None:
        """Update monitoring files with live data"""
        try:
            # Get current positions
            positions = await self.api_client.get_positions()
            
            # Get account info
            account_info = await self.api_client.get_account_info()
            
            status_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bot_status": "running" if self.is_running else "stopped",
                "current_price": self.current_price,
                "daily_pnl": self.daily_pnl,
                "account_balance": account_info.get('balance', 0) if account_info else 0,
                "open_positions": len(positions),
                "consecutive_losses": self.consecutive_losses,
                "api_connected": self.api_client.is_connected,
                "paper_trading": self.config.PAPER_TRADING
            }
            
            await safe_update_monitoring(self.file_ops, 'status.json', status_data)
            
        except Exception as e:
            logger.error(f"Error updating monitoring: {e}")