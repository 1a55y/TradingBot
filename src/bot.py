"""Gold Futures Trading Bot - Refactored with all fixes"""
import asyncio
from datetime import datetime
from typing import Optional
import pandas as pd
from src.core.base_bot import BaseGoldBot
from src.utils.logger_setup import logger
from src.utils.connection_manager import ConnectionManager, WebSocketReconnector
from src.utils.data_validator import DataValidationError

class GoldBot(BaseGoldBot):
    """Production Gold Futures Trading Bot"""
    
    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager()
        self.ws_data: Optional[WebSocketReconnector] = None
        self.ws_trading: Optional[WebSocketReconnector] = None
        
    async def connect(self) -> bool:
        """Connect to TopStepX WebSocket APIs with reconnection support"""
        try:
            # Validate configuration first
            self.config.validate_config()
            
            # Create data connection
            self.ws_data = self.connection_manager.add_connection(
                "data",
                self.config.WS_DATA_URL,
                on_message=self._handle_data_message,
                on_connect=self._on_data_connect,
                on_disconnect=self._on_data_disconnect,
                heartbeat_interval=self.config.WEBSOCKET_HEARTBEAT_INTERVAL,
                max_reconnect_delay=self.config.WEBSOCKET_MAX_RECONNECT_DELAY
            )
            
            # Create trading connection
            self.ws_trading = self.connection_manager.add_connection(
                "trading",
                self.config.WS_TRADING_URL,
                on_message=self._handle_trading_message,
                on_connect=self._on_trading_connect,
                on_disconnect=self._on_trading_disconnect,
                heartbeat_interval=self.config.WEBSOCKET_HEARTBEAT_INTERVAL,
                max_reconnect_delay=self.config.WEBSOCKET_MAX_RECONNECT_DELAY
            )
            
            # Connect all
            results = await self.connection_manager.connect_all()
            
            if all(results.values()):
                self.is_running = True
                return True
            else:
                logger.error(f"Some connections failed: {results}")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from WebSocket APIs"""
        self.is_running = False
        await self.connection_manager.stop_all()
        logger.info("Disconnected from all APIs")
    
    async def _handle_data_message(self, message: dict) -> None:
        """Handle incoming market data messages"""
        try:
            msg_type = message.get('type')
            
            if msg_type == 'price':
                symbol = message.get('symbol')
                price = message.get('price')
                
                if symbol == self.config.get_active_contract():
                    # Validate price before using
                    try:
                        self.current_price = self.validator.validate_price(price)
                    except DataValidationError as e:
                        logger.error(f"Invalid price received: {e}")
                        
            elif msg_type == 'candle':
                # Handle candle updates
                pass
                
        except Exception as e:
            logger.error(f"Error handling data message: {e}")
    
    async def _handle_trading_message(self, message: dict) -> None:
        """Handle trading messages (order updates, fills, etc.)"""
        try:
            msg_type = message.get('type')
            
            if msg_type == 'order_update':
                # Handle order status updates
                pass
            elif msg_type == 'fill':
                # Handle trade fills
                self._process_fill(message)
                
        except Exception as e:
            logger.error(f"Error handling trading message: {e}")
    
    async def _on_data_connect(self) -> None:
        """Called when data connection established"""
        logger.info("Data connection established")
        
        # Subscribe to market data
        await self.ws_data.send({
            "action": "subscribe",
            "symbols": [self.config.get_active_contract(), self.config.DXY_SYMBOL],
            "types": ["price", "candle"]
        })
    
    async def _on_trading_connect(self) -> None:
        """Called when trading connection established"""
        logger.info("Trading connection established")
        
        # Authenticate
        await self.ws_trading.send({
            "action": "auth",
            "api_key": self.config.TOPSTEP_API_KEY,
            "api_secret": self.config.TOPSTEP_API_SECRET
        })
    
    async def _on_data_disconnect(self) -> None:
        """Called when data connection lost"""
        logger.warning("Data connection lost")
    
    async def _on_trading_disconnect(self) -> None:
        """Called when trading connection lost"""
        logger.warning("Trading connection lost")
    
    def _process_fill(self, fill_message: dict) -> None:
        """Process trade fill and update tracking"""
        try:
            # Extract fill details
            side = fill_message.get('side')
            price = fill_message.get('price')
            quantity = fill_message.get('quantity')
            
            # Validate fill data
            price = self.validator.validate_price(price, "fill price")
            
            # Update position tracking
            # TODO: Implement position tracking
            
            logger.info(f"Fill received: {side} {quantity} @ ${price:.2f}")
            
        except DataValidationError as e:
            logger.error(f"Invalid fill data: {e}")
    
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Get historical candles via WebSocket API"""
        try:
            if not self.ws_data or not self.ws_data.is_connected:
                logger.error("Data connection not available")
                return pd.DataFrame()
            
            # Request historical data
            request_id = datetime.now().timestamp()
            await self.ws_data.send({
                "action": "get_candles",
                "symbol": symbol,
                "timeframe": timeframe,
                "limit": limit,
                "request_id": request_id
            })
            
            # TODO: Implement proper async response handling
            # For now, return empty DataFrame
            logger.warning("Candle fetching not fully implemented")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return pd.DataFrame()
    
    async def place_order(self, side: str, quantity: int, stop_price: float, target_price: float) -> bool:
        """Place a bracket order via WebSocket API"""
        try:
            if not self.ws_trading or not self.ws_trading.is_connected:
                logger.error("Trading connection not available")
                return False
            
            logger.info(f"Placing {side} order: {quantity} MGC @ market")
            logger.info(f"Stop: ${stop_price:.2f}, Target: ${target_price:.2f}")
            
            # Validate all parameters first
            self.validator.validate_order_params(
                side, quantity, stop_price, target_price, self.current_price
            )
            
            if self.config.PAPER_TRADING:
                order_request = {
                    "action": "place_order",
                    "account": "PAPER",
                    "symbol": self.config.get_active_contract(),
                    "side": side,
                    "quantity": quantity,
                    "order_type": "MARKET",
                    "bracket": {
                        "stop_loss": stop_price,
                        "take_profit": target_price
                    },
                    "request_id": datetime.now().timestamp()
                }
                
                success = await self.ws_trading.send(order_request)
                
                if success:
                    logger.info("Order sent to broker")
                    return True
                else:
                    logger.error("Failed to send order")
                    return False
            else:
                logger.warning("Live trading not enabled")
                return False
                
        except DataValidationError as e:
            logger.error(f"Invalid order parameters: {e}")
            return False
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False
    
    async def run(self):
        """Main bot execution with connection monitoring"""
        try:
            # Connect to APIs
            connected = await self.connect()
            if not connected:
                logger.error("Failed to connect to APIs")
                return
            
            logger.success("Bot started successfully!")
            
            # Create concurrent tasks
            tasks = [
                asyncio.create_task(self.trading_loop()),
                asyncio.create_task(self.connection_manager.start_all()),
                asyncio.create_task(self._monitor_account()),
            ]
            
            # Run all tasks
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            await self.disconnect()
            logger.info("Bot shutdown complete")
    
    async def _monitor_account(self):
        """Monitor account status and positions"""
        while self.is_running:
            try:
                if self.ws_trading and self.ws_trading.is_connected:
                    # Request account update
                    await self.ws_trading.send({
                        "action": "get_account",
                        "account": "PAPER" if self.config.PAPER_TRADING else "LIVE"
                    })
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Account monitor error: {e}")
                await asyncio.sleep(60)

async def main():
    """Entry point"""
    bot = GoldBot()
    await bot.run()

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())