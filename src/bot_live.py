"""Gold Futures Trading Bot - Live Mode with TopStepX API"""
import asyncio
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from src.core.base_bot import BaseGoldBot
from src.api.topstep_client import TopStepXClient
from src.api.mock_topstep_client import MockTopStepXClient
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
        
        # Tasks for concurrent operations
        self.market_data_task = None
        self.trading_events_task = None
        
        logger.info("Live Gold Bot initialized")
        logger.info(f"Trading Symbol: {self.config.SYMBOL}")
        logger.info(f"Market: {self.config.TOPSTEP_MARKET}")
    
    async def connect(self) -> bool:
        """Connect to TopStepX API"""
        try:
            if await self.api_client.connect():
                self.is_running = True
                
                # Start background tasks
                self.market_data_task = asyncio.create_task(self._process_market_data())
                self.trading_events_task = asyncio.create_task(self._process_trading_events())
                
                # Get initial account info
                account_info = await self.api_client.get_account_info()
                if account_info:
                    logger.info(f"Connected to account: {account_info.get('username')}")
                    logger.info(f"Account balance: ${account_info.get('balance', 0):.2f}")
                
                return True
            else:
                logger.error("Failed to connect to TopStepX API")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from TopStepX API"""
        try:
            self.is_running = False
            
            # Cancel background tasks
            if self.market_data_task:
                self.market_data_task.cancel()
            if self.trading_events_task:
                self.trading_events_task.cancel()
            
            # Disconnect API client
            await self.api_client.disconnect()
            
            logger.info("Disconnected from live trading")
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    async def _process_market_data(self) -> None:
        """Process incoming market data stream"""
        try:
            async for data in self.api_client.handle_market_data_stream():
                if not self.is_running:
                    break
                
                # Update current price
                if 'bid' in data and 'ask' in data:
                    self.current_price = (data['bid'] + data['ask']) / 2
                    self.market_data_buffer.append({
                        'timestamp': datetime.now(timezone.utc),
                        'price': self.current_price,
                        'bid': data['bid'],
                        'ask': data['ask'],
                        'bid_size': data.get('bid_size', 0),
                        'ask_size': data.get('ask_size', 0)
                    })
                    
                    # Keep buffer size manageable
                    if len(self.market_data_buffer) > 1000:
                        self.market_data_buffer = self.market_data_buffer[-1000:]
                        
        except asyncio.CancelledError:
            logger.info("Market data task cancelled")
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
    
    async def _process_trading_events(self) -> None:
        """Process trading events (fills, rejects, etc.)"""
        try:
            async for event in self.api_client.handle_trading_events():
                if not self.is_running:
                    break
                
                event_type = event.get('type')
                
                if event_type == 'fill':
                    await self._handle_fill(event)
                elif event_type == 'reject':
                    await self._handle_reject(event)
                elif event_type == 'position_update':
                    await self._handle_position_update(event)
                    
        except asyncio.CancelledError:
            logger.info("Trading events task cancelled")
        except Exception as e:
            logger.error(f"Error processing trading events: {e}")
    
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
        """Get historical candles from API"""
        try:
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
            # Get current market price
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