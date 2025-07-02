"""Gold Futures Trading Bot - Live Mode with TopStepX API"""
# Standard library imports
import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

# Third-party imports
import pandas as pd

# Local imports
from src.api.mock_topstep_client import MockTopStepXClient
from src.api.topstep_client import TopStepXClient
from src.api.topstep_websocket_client import TopStepXWebSocketClient
from src.core.base_bot import BaseGoldBot
from src.utils.data_validator import DataValidationError
from src.utils.logger_setup import logger


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
        self.contract_id = None  # Dynamic contract ID
        
        # Multi-timeframe analysis cache
        self.mtf_cache = {}
        self.mtf_patterns = {}
        
        # Real-time price monitoring
        self.last_tick_time = None
        self.tick_count = 0
        
        # Initialize tracking variables for monitoring
        self.total_trades = 0
        self.patterns_found_today = 0
        self.high_quality_patterns_today = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.trade_history = []  # Store all trade executions
        
        # Account balance cache
        self._account_balance = None
        self._balance_last_fetched = None
        
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
            
            # Get contract ID based on configuration
            contract_symbol = self.config.SYMBOL  # This will be 'MNQ' or 'NQ'
            contract = await self.api_client._get_contract_by_symbol(contract_symbol)
            if contract:
                self.contract_id = contract.get("id")
                logger.info(f"Found {contract_symbol} contract: {self.contract_id}")
            else:
                logger.error(f"Could not find {contract_symbol} contract")
            
            # Get initial account info
            account_info = await self.api_client.get_account_info()
            if account_info:
                logger.info(f"Connected to account: {account_info.get('username')}")
                logger.info(f"Account balance: ${account_info.get('balance', 0):.2f}")
            
            # Fetch initial account balance
            account_info = await self.api_client.get_account_info()
            if account_info:
                self._account_balance = account_info.get('balance', self.config.DEFAULT_ACCOUNT_SIZE)
                self._balance_last_fetched = datetime.now()
            
            # Connect WebSocket for real-time data
            if self.contract_id and not isinstance(self.api_client, MockTopStepXClient):
                logger.info("Connecting to WebSocket for real-time data...")
                self.ws_client = TopStepXWebSocketClient(self.api_client.session_token)
                
                # Register callbacks
                self.ws_client.on_quote(self._handle_quote_update)
                self.ws_client.on_trade(self._handle_trade_update)
                
                if await self.ws_client.connect():
                    # Subscribe to contract quotes
                    await self.ws_client.subscribe_quotes(self.contract_id)
                    await self.ws_client.subscribe_trades(self.contract_id)
                    logger.info(f"✅ WebSocket connected - receiving real-time data for {contract_symbol}!")
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
            
            # Generate final daily summary
            self.generate_daily_summary()
            
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
        """Handle order fill event with comprehensive logging"""
        order_id = event.get('order_id')
        fill_price = event.get('fill_price')
        quantity = event.get('quantity')
        side = event.get('side')
        fill_timestamp = datetime.now(timezone.utc)
        
        logger.info("=" * 60)
        logger.info("✅ ORDER FILLED")
        logger.info("=" * 60)
        logger.info(f"Order ID: {order_id}")
        logger.info(f"Side: {side}")
        logger.info(f"Quantity: {quantity}")
        logger.info(f"Fill Price: ${fill_price:.2f}")
        logger.info(f"Fill Time: {fill_timestamp.isoformat()}")
        
        # Update positions with fill details
        if order_id in self.positions:
            position = self.positions[order_id]
            expected_price = position.get('expected_entry', position.get('entry_price'))
            actual_slippage = fill_price - expected_price if side == 'BUY' else expected_price - fill_price
            slippage_cost = abs(actual_slippage) * quantity * self.config.TICK_VALUE / self.config.TICK_SIZE
            
            # Update position with fill data
            position['status'] = 'filled'
            position['fill_price'] = fill_price
            position['fill_timestamp'] = fill_timestamp
            position['actual_slippage'] = actual_slippage
            position['actual_slippage_cost'] = slippage_cost
            
            # Recalculate risk with actual fill price
            actual_stop_distance = abs(fill_price - position['stop_price'])
            actual_risk = actual_stop_distance * quantity * self.config.TICK_VALUE / self.config.TICK_SIZE
            position['actual_risk'] = actual_risk
            
            logger.info("-" * 60)
            logger.info("FILL ANALYSIS:")
            logger.info(f"Expected Price: ${expected_price:.2f}")
            logger.info(f"Actual Slippage: ${actual_slippage:.2f} ({actual_slippage/self.config.TICK_SIZE:.1f} ticks)")
            logger.info(f"Slippage Cost: ${slippage_cost:.2f}")
            logger.info(f"Actual Risk: ${actual_risk:.2f} (vs planned ${position['risk_amount']:.2f})")
            logger.info("=" * 60)
            
            # Update trade log
            self._log_trade_execution(position)
    
    async def _handle_reject(self, event: Dict) -> None:
        """Handle order rejection"""
        order_id = event.get('order_id')
        reason = event.get('reason', 'Unknown')
        
        logger.error(f"Order rejected: {order_id} - Reason: {reason}")
        
        # Remove from positions
        if order_id in self.positions:
            del self.positions[order_id]
    
    async def _handle_position_update(self, event: Dict) -> None:
        """Handle position update event with P&L tracking"""
        position_data = event.get('position', {})
        position_id = position_data.get('position_id')
        symbol = position_data.get('symbol')
        side = position_data.get('side')
        quantity = position_data.get('quantity', 0)
        entry_price = position_data.get('entry_price', 0)
        current_price = position_data.get('current_price', 0)
        unrealized_pnl = position_data.get('unrealized_pnl', 0)
        realized_pnl = position_data.get('realized_pnl', 0)
        
        # Log position update
        if quantity != 0:
            logger.info(f"Position Update: {symbol} {side} {quantity} @ ${entry_price:.2f}")
            logger.info(f"Current Price: ${current_price:.2f}, Unrealized P&L: ${unrealized_pnl:.2f}")
        
        # Handle position closure
        if quantity == 0 and position_id in self.positions:
            position = self.positions[position_id]
            close_timestamp = datetime.now(timezone.utc)
            
            logger.info("=" * 60)
            logger.info("📊 POSITION CLOSED")
            logger.info("=" * 60)
            logger.info(f"Position ID: {position_id}")
            logger.info(f"Side: {position.get('side')}")
            logger.info(f"Entry Price: ${position.get('fill_price', position.get('entry_price')):.2f}")
            logger.info(f"Exit Price: ${current_price:.2f}")
            logger.info(f"P&L: ${realized_pnl:.2f}")
            
            # Calculate R-Multiple
            risk = position.get('actual_risk', position.get('risk_amount', 0))
            r_multiple = realized_pnl / risk if risk > 0 else 0
            
            logger.info(f"R-Multiple: {r_multiple:.2f}R")
            logger.info(f"Duration: {(close_timestamp - position.get('entry_timestamp')).total_seconds() / 60:.1f} minutes")
            logger.info("=" * 60)
            
            # Update trade tracking
            if realized_pnl > 0:
                self.winning_trades += 1
                self.consecutive_losses = 0
            else:
                self.losing_trades += 1
                self.consecutive_losses += 1
            
            # Update position record
            position['exit_price'] = current_price
            position['exit_timestamp'] = close_timestamp
            position['realized_pnl'] = realized_pnl
            position['r_multiple'] = r_multiple
            position['status'] = 'closed'
            
            # Log to trade history
            self._log_trade_execution(position)
        
        # Update daily P&L
        self.daily_pnl = unrealized_pnl + realized_pnl
        
        # Check risk limits
        if self.daily_pnl <= -self.config.DAILY_LOSS_LIMIT:
            logger.critical(f"Daily loss limit reached: ${self.daily_pnl:.2f}")
            await self.flatten_all_positions()
    
    async def get_multi_timeframe_candles(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get candles for all analysis timeframes"""
        mtf_data = {}
        
        # Use 400 candles for all timeframes for better pattern detection
        timeframe_limits = {
            '1m': 400,   # 6.7 hours of data
            '5m': 400,   # 33.3 hours of data
            '15m': 400,  # 100 hours (4.2 days) of data
            '30m': 400,  # 200 hours (8.3 days) of data
            '1h': 400    # 400 hours (16.7 days) of data
        }
        
        for tf in self.config.ANALYSIS_TIMEFRAMES:
            limit = timeframe_limits.get(tf, self.config.LOOKBACK_CANDLES)
            candles = await self.get_candles(symbol, tf, limit)
            if not candles.empty:
                mtf_data[tf] = candles
                logger.debug(f"Loaded {len(candles)} candles for {tf} timeframe")
            else:
                logger.warning(f"No data received for {tf} timeframe")
        
        return mtf_data
    
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
            # TopStep API returns 't', 'o', 'h', 'l', 'c', 'v'
            column_mapping = {
                't': 'timestamp',
                'o': 'open',  
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            }
            
            # Apply the mapping
            df = df.rename(columns=column_mapping)
            
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
        """Place order via API with comprehensive trade logging"""
        try:
            # Timestamp for trade entry
            entry_timestamp = datetime.now(timezone.utc)
            
            # Use real-time price if available, otherwise get from API
            if self.current_price > 0:
                current_price = self.current_price
                price_source = "WebSocket"
                logger.info(f"Using real-time WebSocket price: ${current_price:.2f}")
            else:
                # Fallback to REST API
                market_data = await self.api_client.get_market_data(self.config.SYMBOL)
                if not market_data:
                    logger.error("Cannot get current market price")
                    return False
                bid_price = market_data['bid']
                ask_price = market_data['ask']
                current_price = (bid_price + ask_price) / 2
                spread = ask_price - bid_price
                price_source = "REST API"
                logger.info(f"Market prices - Bid: ${bid_price:.2f}, Ask: ${ask_price:.2f}, Spread: ${spread:.2f}")
            
            # Calculate all trade metrics
            stop_distance = abs(current_price - stop_price)
            stop_distance_ticks = stop_distance / self.config.TICK_SIZE
            target_distance = abs(target_price - current_price)
            target_distance_ticks = target_distance / self.config.TICK_SIZE
            
            # Risk calculations
            risk_per_contract = stop_distance_ticks * self.config.TICK_VALUE
            total_risk = risk_per_contract * quantity
            
            # Reward calculations
            reward_per_contract = target_distance_ticks * self.config.TICK_VALUE
            total_reward = reward_per_contract * quantity
            
            # Risk:Reward ratio
            risk_reward_ratio = target_distance / stop_distance if stop_distance > 0 else 0
            
            # Expected entry price (for market orders, expect some slippage)
            expected_entry = current_price
            if side.upper() == 'BUY':
                expected_entry = ask_price if 'ask_price' in locals() else current_price
            else:
                expected_entry = bid_price if 'bid_price' in locals() else current_price
            
            # Log comprehensive trade details
            logger.info("=" * 60)
            logger.info("📊 TRADE EXECUTION DETAILS")
            logger.info("=" * 60)
            logger.info(f"🕐 Entry Timestamp: {entry_timestamp.isoformat()}")
            logger.info(f"📈 Trade Direction: {side.upper()}")
            logger.info(f"🎯 Symbol: {self.config.SYMBOL} ({self.config.get_active_contract()})")
            logger.info(f"📊 Position Size: {quantity} contracts")
            logger.info("-" * 60)
            logger.info("💰 PRICE LEVELS:")
            logger.info(f"   Entry Price: ${expected_entry:.2f} (Source: {price_source})")
            logger.info(f"   Stop Loss: ${stop_price:.2f} ({stop_distance_ticks:.1f} ticks)")
            logger.info(f"   Take Profit: ${target_price:.2f} ({target_distance_ticks:.1f} ticks)")
            logger.info("-" * 60)
            logger.info("📊 RISK MANAGEMENT:")
            logger.info(f"   Risk per Contract: ${risk_per_contract:.2f}")
            logger.info(f"   Total Risk: ${total_risk:.2f}")
            logger.info(f"   Reward per Contract: ${reward_per_contract:.2f}")
            logger.info(f"   Total Reward: ${total_reward:.2f}")
            logger.info(f"   Risk:Reward Ratio: 1:{risk_reward_ratio:.2f}")
            logger.info(f"   Risk % of Daily Limit: {(total_risk/self.config.DAILY_LOSS_LIMIT)*100:.1f}%")
            logger.info("-" * 60)
            logger.info("📈 POSITION SIZING:")
            logger.info(f"   Account Balance: ${await self.get_account_balance():.2f}")
            logger.info(f"   Risk per Trade: ${self.config.MAX_RISK_PER_TRADE:.2f}")
            logger.info(f"   Notional Value: ${expected_entry * quantity:.2f}")
            logger.info("=" * 60)
            
            # Get contract ID for current symbol
            contract_id = None
            if hasattr(self, 'contract_id') and self.contract_id:
                contract_id = self.contract_id  # Use the contract ID we got during connection
            else:
                # Fallback: get contract ID if we don't have it
                contract = await self.api_client._get_contract_by_symbol(self.config.SYMBOL)
                if contract:
                    contract_id = contract.get('id')
                    self.contract_id = contract_id  # Store for future use
            
            if not contract_id:
                logger.error(f"Cannot find contract ID for {self.config.SYMBOL}")
                return False
            
            # Prepare order data
            order_data = {
                "symbol": self.config.SYMBOL,
                "contractId": contract_id,
                "side": side.capitalize(),  # "Buy" or "Sell"
                "quantity": quantity,
                "orderType": "Market",  # TopStep expects capitalized
                "time_in_force": "GTC",
                "account_id": self.config.TOPSTEP_ACCOUNT_ID,
                "stop_loss": stop_price,
                "take_profit": target_price
            }
            
            # Risk check
            if total_risk > self.config.MAX_RISK_PER_TRADE:
                logger.error(f"❌ TRADE REJECTED: Risk too high: ${total_risk:.2f} > ${self.config.MAX_RISK_PER_TRADE}")
                return False
            
            # Determine which account to use
            if self.config.PAPER_TRADING:
                logger.info("📋 PLACING ORDER TO PRACTICE ACCOUNT")
                account_mode = "PRACTICE"
                # Use practice account ID explicitly
                order_data['account_id'] = self.config.PRACTICE_ACCOUNT_ID
            else:
                logger.info("💹 PLACING ORDER TO EVALUATION ACCOUNT")
                account_mode = "EVALUATION"
                # Use step1 account ID
                order_data['account_id'] = self.config.STEP1_ACCOUNT_ID
            
            # Submit order to TopStep API
            logger.info(f"📤 SUBMITTING ORDER TO TOPSTEP ({account_mode} ACCOUNT)")
            order_start_time = datetime.now(timezone.utc)
            
            result = await self.api_client.place_order(order_data)
            
            order_end_time = datetime.now(timezone.utc)
            execution_time = (order_end_time - order_start_time).total_seconds()
            
            if result:
                order_id = result.get('order_id')
                fill_price = result.get('fill_price', expected_entry)
                slippage = fill_price - expected_entry
                
                # Create detailed position record
                position_data = {
                    'order_id': order_id,
                    'side': side,
                    'quantity': quantity,
                    'entry_price': fill_price,
                    'expected_entry': expected_entry,
                    'stop_price': stop_price,
                    'target_price': target_price,
                    'entry_timestamp': entry_timestamp,
                    'fill_timestamp': order_end_time,
                    'execution_time_seconds': execution_time,
                    'status': 'pending',
                    'risk_amount': total_risk,
                    'reward_amount': total_reward,
                    'risk_reward_ratio': risk_reward_ratio,
                    'stop_distance_ticks': stop_distance_ticks,
                    'target_distance_ticks': target_distance_ticks,
                    'price_source': price_source,
                    'slippage': slippage,
                    'slippage_cost': abs(slippage) * quantity * self.config.TICK_VALUE / self.config.TICK_SIZE
                }
                
                self.positions[order_id] = position_data
                
                # Log execution details
                logger.info("-" * 60)
                logger.info(f"✅ ORDER FILLED ON {account_mode} ACCOUNT:")
                logger.info(f"   Order ID: {order_id}")
                logger.info(f"   Fill Price: ${fill_price:.2f}")
                logger.info(f"   Slippage: ${slippage:.2f} ({slippage/self.config.TICK_SIZE:.1f} ticks)")
                logger.info(f"   Slippage Cost: ${position_data['slippage_cost']:.2f}")
                logger.info(f"   Execution Time: {execution_time:.3f} seconds")
                logger.info("=" * 60)
                
                # Log to trade history
                self._log_trade_execution(position_data)
                
                # Update trade counter
                self.total_trades += 1
                
                return True
            else:
                logger.error(f"❌ Order submission failed on {account_mode} account - no result from API")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            return False
    
    def _log_trade_execution(self, trade_data: dict) -> None:
        """Log trade execution details to file for analysis"""
        try:
            # Add to trade history
            self.trade_history.append(trade_data)
            
            # Write to trade log file
            trade_log_file = 'logs/trade_executions.json'
            
            # Read existing trades if file exists
            existing_trades = []
            if os.path.exists(trade_log_file):
                with open(trade_log_file, 'r') as f:
                    try:
                        existing_trades = json.load(f)
                    except:
                        existing_trades = []
            
            # Append new trade
            existing_trades.append({
                **trade_data,
                'entry_timestamp': trade_data['entry_timestamp'].isoformat() if isinstance(trade_data['entry_timestamp'], datetime) else trade_data['entry_timestamp'],
                'fill_timestamp': trade_data.get('fill_timestamp').isoformat() if trade_data.get('fill_timestamp') and isinstance(trade_data.get('fill_timestamp'), datetime) else trade_data.get('fill_timestamp')
            })
            
            # Write back to file
            with open(trade_log_file, 'w') as f:
                json.dump(existing_trades, f, indent=2)
                
            logger.debug(f"Trade logged to {trade_log_file}")
            
        except Exception as e:
            logger.error(f"Error logging trade execution: {e}")
    
    def generate_daily_summary(self) -> None:
        """Generate daily trading summary with detailed metrics"""
        try:
            logger.info("=" * 80)
            logger.info("📊 DAILY TRADING SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Date: {datetime.now(timezone.utc).date()}")
            logger.info(f"Trading Mode: {'PAPER' if self.config.PAPER_TRADING else 'LIVE'}")
            logger.info(f"Contract: {self.config.SYMBOL} ({self.config.get_active_contract()})")
            logger.info("-" * 80)
            
            # Performance metrics
            total_trades = self.total_trades
            winners = getattr(self, 'winning_trades', 0)
            losers = getattr(self, 'losing_trades', 0)
            win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
            
            logger.info("PERFORMANCE METRICS:")
            logger.info(f"   Total Trades: {total_trades}")
            logger.info(f"   Winners: {winners}")
            logger.info(f"   Losers: {losers}")
            logger.info(f"   Win Rate: {win_rate:.1f}%")
            logger.info(f"   Daily P&L: ${self.daily_pnl:.2f}")
            logger.info(f"   Consecutive Losses: {self.consecutive_losses}")
            logger.info("-" * 80)
            
            # Pattern analysis
            logger.info("PATTERN ANALYSIS:")
            logger.info(f"   Patterns Found: {getattr(self, 'patterns_found_today', 0)}")
            logger.info(f"   High Quality Patterns: {getattr(self, 'high_quality_patterns_today', 0)}")
            logger.info("-" * 80)
            
            # Risk metrics
            remaining_risk = self.config.DAILY_LOSS_LIMIT + self.daily_pnl
            logger.info("RISK METRICS:")
            logger.info(f"   Daily Loss Limit: ${self.config.DAILY_LOSS_LIMIT:.2f}")
            logger.info(f"   Remaining Risk: ${remaining_risk:.2f}")
            logger.info(f"   Risk Used: {(-self.daily_pnl/self.config.DAILY_LOSS_LIMIT*100):.1f}%" if self.daily_pnl < 0 else "   Risk Used: 0.0%")
            logger.info("-" * 80)
            
            # Trade history analysis
            if hasattr(self, 'trade_history') and self.trade_history:
                # Calculate average metrics
                total_risk = sum(t.get('risk_amount', 0) for t in self.trade_history)
                total_slippage = sum(abs(t.get('slippage', 0)) for t in self.trade_history if t.get('status') == 'filled')
                avg_risk = total_risk / len(self.trade_history) if self.trade_history else 0
                avg_slippage = total_slippage / len([t for t in self.trade_history if t.get('status') == 'filled']) if any(t.get('status') == 'filled' for t in self.trade_history) else 0
                
                # R-Multiple analysis for closed trades
                closed_trades = [t for t in self.trade_history if t.get('status') == 'closed']
                if closed_trades:
                    r_multiples = [t.get('r_multiple', 0) for t in closed_trades]
                    avg_r = sum(r_multiples) / len(r_multiples) if r_multiples else 0
                    max_r = max(r_multiples) if r_multiples else 0
                    min_r = min(r_multiples) if r_multiples else 0
                    
                    logger.info("TRADE STATISTICS:")
                    logger.info(f"   Average Risk per Trade: ${avg_risk:.2f}")
                    logger.info(f"   Average Slippage: ${avg_slippage:.2f}")
                    logger.info(f"   Average R-Multiple: {avg_r:.2f}R")
                    logger.info(f"   Best Trade: {max_r:.2f}R")
                    logger.info(f"   Worst Trade: {min_r:.2f}R")
                    logger.info("-" * 80)
            
            # Market conditions
            if hasattr(self, 'tick_count') and self.tick_count > 0:
                logger.info("MARKET CONDITIONS:")
                logger.info(f"   WebSocket Ticks Received: {self.tick_count}")
                logger.info(f"   Current Price: ${self.current_price:.2f}")
                if hasattr(self, 'last_tick_time') and self.last_tick_time:
                    logger.info(f"   Last Tick: {self.last_tick_time.isoformat()}")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
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
    
    def find_mtf_order_blocks(self, mtf_data: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
        """Find order blocks across multiple timeframes"""
        mtf_patterns = {}
        
        for timeframe, candles in mtf_data.items():
            patterns = self.find_order_blocks(candles)
            mtf_patterns[timeframe] = patterns
            logger.debug(f"Found {len(patterns)} patterns on {timeframe}")
        
        return mtf_patterns
    
    def calculate_mtf_pattern_score(self, pattern: Dict, timeframe: str, mtf_data: Dict[str, pd.DataFrame], mtf_patterns: Dict[str, List[Dict]]) -> float:
        """Calculate multi-timeframe pattern score"""
        # Get base score from primary timeframe
        base_score = self.calculate_pattern_score(pattern, mtf_data[timeframe])
        
        # Multi-timeframe confluence bonus
        mtf_bonus = 0
        timeframe_weights = {
            '1m': 0.2,   # Entry timeframe
            '5m': 0.5,   # Primary timeframe  
            '15m': 0.3   # Higher timeframe
        }
        
        # Check for confluence on other timeframes
        pattern_type = pattern['type']
        pattern_level = pattern['level']
        
        for tf, patterns in mtf_patterns.items():
            if tf == timeframe:
                continue
                
            # Look for similar patterns on other timeframes
            for other_pattern in patterns:
                if other_pattern['type'] == pattern_type:
                    # Check if levels are close (within 0.5%)
                    level_diff = abs(other_pattern['level'] - pattern_level) / pattern_level
                    if level_diff < 0.005:
                        weight = timeframe_weights.get(tf, 0.2)
                        mtf_bonus += 2 * weight
                        logger.debug(f"Found confluence on {tf} timeframe, bonus: {2 * weight}")
        
        # Trend alignment bonus
        trend_bonus = self.calculate_trend_alignment(pattern, mtf_data)
        
        # Combined score
        total_score = base_score + mtf_bonus + trend_bonus
        
        # Cap at 10
        return min(total_score, 10)
    
    def calculate_trend_alignment(self, pattern: Dict, mtf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate trend alignment across timeframes"""
        trend_scores = []
        
        for timeframe, candles in mtf_data.items():
            if len(candles) < 20:
                continue
                
            # Simple trend detection using EMAs
            ema_fast = candles['close'].ewm(span=8, adjust=False).mean()
            ema_slow = candles['close'].ewm(span=21, adjust=False).mean()
            
            current_trend = 'bullish' if ema_fast.iloc[-1] > ema_slow.iloc[-1] else 'bearish'
            
            # Check if pattern aligns with trend
            if pattern['type'] == current_trend:
                weight = {'1m': 0.3, '5m': 0.5, '15m': 0.7}.get(timeframe, 0.3)
                trend_scores.append(weight)
        
        return sum(trend_scores)
    
    async def trading_loop(self):
        """Override trading loop with multi-timeframe analysis"""
        logger.info("Starting multi-timeframe trading loop...")
        
        signal_cooldown = getattr(self.config, 'SIGNAL_COOLDOWN_SECONDS', 300)
        main_loop_delay = getattr(self.config, 'MAIN_LOOP_DELAY_SECONDS', 30)
        
        while self.is_running:
            try:
                # Check if we can trade
                if not self.can_trade():
                    await asyncio.sleep(60)
                    continue
                
                # Get multi-timeframe market data
                mtf_data = await self.get_multi_timeframe_candles(
                    self.config.get_active_contract()
                )
                
                if not mtf_data or self.config.PRIMARY_TIMEFRAME not in mtf_data:
                    logger.warning("No multi-timeframe data received")
                    await asyncio.sleep(30)
                    continue
                
                # Find patterns across all timeframes
                mtf_patterns = self.find_mtf_order_blocks(mtf_data)
                
                # Count total patterns
                total_patterns = sum(len(patterns) for patterns in mtf_patterns.values())
                self.patterns_found_today = total_patterns
                
                # Score patterns with multi-timeframe analysis
                best_signal = None
                best_score = 0
                best_timeframe = None
                high_quality_count = 0
                
                # Analyze patterns from all timeframes
                for timeframe, patterns in mtf_patterns.items():
                    for pattern in patterns:
                        score = self.calculate_mtf_pattern_score(pattern, timeframe, mtf_data, mtf_patterns)
                        
                        if score >= self.config.MIN_PATTERN_SCORE:
                            high_quality_count += 1
                            if score > best_score:
                                best_signal = pattern
                                best_score = score
                                best_timeframe = timeframe
                
                # Update high quality pattern count
                self.high_quality_patterns_today = high_quality_count
                
                # Execute best signal if found
                if best_signal:
                    logger.info(f"Best signal found on {best_timeframe} timeframe with score {best_score:.1f}")
                    self.last_signal_time = datetime.now(timezone.utc)
                    
                    # Use primary timeframe candles for execution
                    primary_candles = mtf_data[self.config.PRIMARY_TIMEFRAME]
                    await self.execute_signal(best_signal, best_score, primary_candles)
                    
                    # Wait before looking for next signal
                    await asyncio.sleep(signal_cooldown)
                
                # Update monitoring
                await self.update_monitoring()
                
                # Wait before next iteration
                await asyncio.sleep(main_loop_delay)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(60)
    
    async def get_account_balance(self) -> float:
        """Get current account balance, with caching"""
        try:
            # Check if we need to refresh the balance (every 5 minutes)
            if self._balance_last_fetched is None or \
               (datetime.now() - self._balance_last_fetched).seconds > 300:
                
                account_info = await self.api_client.get_account_info()
                if account_info and 'balance' in account_info:
                    self._account_balance = account_info['balance']
                    self._balance_last_fetched = datetime.now()
                    logger.info(f"Updated account balance: ${self._account_balance:.2f}")
                else:
                    # If we can't get balance, use cached or default
                    if self._account_balance is None:
                        self._account_balance = self.config.DEFAULT_ACCOUNT_SIZE
                        logger.warning(f"Using default account size: ${self._account_balance:.2f}")
            
            return self._account_balance
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            # Return cached balance or default
            return self._account_balance or self.config.DEFAULT_ACCOUNT_SIZE
    
    def calculate_position_size(self, stop_distance_ticks: int) -> int:
        """Calculate position size based on dynamic account balance and risk"""
        try:
            # Get account balance synchronously (use cached value)
            account_balance = self._account_balance or self.config.DEFAULT_ACCOUNT_SIZE
            
            # Use the dynamic position size calculation from config
            size = self.config.calculate_dynamic_position_size(account_balance)
            
            # Reduce size after losses
            if self.consecutive_losses >= 1:
                size = max(self.config.MIN_POSITION, size // 2)
                logger.info(f"Reducing position size due to {self.consecutive_losses} consecutive losses")
            
            # Ensure within limits
            size = max(self.config.MIN_POSITION, min(size, self.config.MAX_POSITION))
            
            logger.info(f"Position size: {size} {self.config.SYMBOL} (Account: ${account_balance:.2f})")
            return size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            # Fallback to minimum position
            return self.config.MIN_POSITION
    
    async def update_monitoring(self) -> None:
        """Update monitoring files with live data"""
        try:
            # Get current positions
            positions = await self.api_client.get_positions()
            # Make sure positions is a list, not None
            if positions is None:
                positions = []
            
            # Get account info
            account_info = await self.api_client.get_account_info()
            
            # Format status data to match monitor expectations
            status_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_alive": self.is_running,
                "mode": "PRACTICE" if self.config.PAPER_TRADING else "LIVE",
                "account": {
                    "balance": account_info.get('balance', 0) if account_info else 0,
                    "daily_pnl": self.daily_pnl,
                    "open_positions": len(positions),
                    "consecutive_losses": self.consecutive_losses,
                    "total_trades": self.total_trades
                },
                "trading": {
                    "can_trade": self.can_trade(),
                    "last_signal": self.last_signal_time.isoformat() if hasattr(self, 'last_signal_time') and self.last_signal_time else None,
                    "current_stage": self.config.TRADING_STAGE
                },
                "risk": {
                    "daily_loss_remaining": self.config.DAILY_LOSS_LIMIT + self.daily_pnl,
                    "position_size": self.config.DEFAULT_POSITION,
                    "max_risk_per_trade": self.config.MAX_RISK_PER_TRADE
                },
                "patterns": {
                    "found": getattr(self, 'patterns_found_today', 0),
                    "high_quality": getattr(self, 'high_quality_patterns_today', 0)
                },
                "performance": {
                    "total_trades": self.total_trades,
                    "winners": getattr(self, 'winning_trades', 0),
                    "losers": getattr(self, 'losing_trades', 0),
                    "win_rate": (getattr(self, 'winning_trades', 0) / self.total_trades * 100) if self.total_trades > 0 else 0
                },
                "current_price": self.current_price,
                "next_update": (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat()
            }
            
            # Write status to file (write_json is synchronous, not async)
            import json
            from pathlib import Path
            status_file = Path('logs/status.json')
            status_file.parent.mkdir(exist_ok=True)
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error updating monitoring: {e}")