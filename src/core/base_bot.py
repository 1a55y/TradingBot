"""Base bot class to eliminate code duplication - CRITICAL FIX #5"""
from abc import ABC, abstractmethod
import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import asyncio
from src.utils.logger_setup import logger
from src.config import Config
from src.utils.data_validator import DataValidator, DataValidationError
from src.utils.file_operations import create_safe_file_operations, safe_update_monitoring

class BaseGoldBot(ABC):
    """Base class for Gold Trading Bot - shared functionality"""
    
    def __init__(self):
        self.config = Config
        self.is_running = False
        self.current_price = 0.0
        self.positions = {}
        self.daily_pnl = 0.0
        self.consecutive_losses = 0
        self.last_signal_time = None
        self.trade_history = []
        
        # Data validation
        self.validator = DataValidator(self.config)
        
        # File operations
        self.file_ops = create_safe_file_operations()
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        logger.info(f"{self.__class__.__name__} initialized")
        logger.info(f"Paper Trading: {self.config.PAPER_TRADING}")
        logger.info(f"Default Position Size: {self.config.DEFAULT_POSITION_MGC} MGC")
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to data source - implement in subclass"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from data source - implement in subclass"""
        pass
    
    @abstractmethod
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Get candle data - implement in subclass"""
        pass
    
    @abstractmethod
    async def place_order(self, side: str, quantity: int, stop_price: float, target_price: float) -> bool:
        """Place order - implement in subclass"""
        pass
    
    def find_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """SMC Order block detection - shared implementation"""
        order_blocks = []
        
        if len(df) < 3:
            return order_blocks
        
        try:
            # Validate data first
            df = self.validator.validate_candles_df(df)
            
            # Calculate candle properties
            df['body_size'] = abs(df['close'] - df['open'])
            df['avg_body'] = df['body_size'].rolling(20).mean()
            
            # Pattern age limit - from config
            max_age = getattr(self.config, 'MAX_PATTERN_AGE_CANDLES', 50)
            start_index = max(0, len(df) - max_age)
            
            # Basic order block detection
            for i in range(start_index, len(df) - 1):
                current = df.iloc[i]
                next_candle = df.iloc[i + 1]
                
                # Skip if we don't have average body size yet
                if pd.isna(current['avg_body']) or current['avg_body'] <= 0:
                    continue
                
                # Calculate strength (capped at 3.0)
                strength = min(current['body_size'] / current['avg_body'], 3.0)
                
                # Bullish Order Block
                if (current['close'] < current['open'] and  # Red candle
                    current['body_size'] > current['avg_body'] * 1.5 and  # Large body
                    next_candle['close'] > current['high'] and  # Next breaks high
                    next_candle['close'] > next_candle['open']):  # Next is green
                    
                    order_blocks.append({
                        'type': 'bullish',
                        'level': current['low'],
                        'top': current['high'],
                        'index': i,
                        'timestamp': current['timestamp'],
                        'strength': strength
                    })
                    logger.debug(f"Found bullish OB at index {i}, level: ${current['low']:.2f}")
                
                # Bearish Order Block
                elif (current['close'] > current['open'] and  # Green candle
                      current['body_size'] > current['avg_body'] * 1.5 and  # Large body
                      next_candle['close'] < current['low'] and  # Next breaks low
                      next_candle['close'] < next_candle['open']):  # Next is red
                    
                    order_blocks.append({
                        'type': 'bearish',
                        'level': current['high'],
                        'bottom': current['low'],
                        'index': i,
                        'timestamp': current['timestamp'],
                        'strength': strength
                    })
                    logger.debug(f"Found bearish OB at index {i}, level: ${current['high']:.2f}")
            
            logger.info(f"Found {len(order_blocks)} order blocks")
            return order_blocks
            
        except DataValidationError as e:
            logger.error(f"Data validation error in pattern detection: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in order block detection: {e}")
            return []
    
    def calculate_pattern_score(self, pattern: Dict, df: pd.DataFrame) -> float:
        """Calculate quality score for a pattern (1-10) - shared implementation"""
        score = 0.0
        
        try:
            # Validate pattern first
            pattern = self.validator.validate_pattern(pattern)
            
            # Base score for pattern strength (capped)
            score += min(pattern.get('strength', 1.0) * 2, 3)  # Max 3 points
            
            # Volume confirmation
            pattern_idx = pattern['index']
            if pattern_idx < len(df):
                candle = df.iloc[pattern_idx]
                avg_volume = df['volume'].rolling(20).mean().iloc[pattern_idx]
                if not pd.isna(avg_volume) and avg_volume > 0 and candle['volume'] > avg_volume * 1.5:
                    score += 2  # Volume spike bonus
            
            # Recency bonus
            age = len(df) - pattern['index']
            if age < 10:
                score += 2
            elif age < 25:
                score += 1
            
            # Clean move bonus
            tolerance = getattr(self.config, 'PATTERN_VIOLATION_TOLERANCE', 0.002)
            
            if pattern['type'] == 'bullish':
                recent_low = df['low'].iloc[pattern['index']:].min()
                if recent_low > pattern['level'] * (1 - tolerance):  # Not violated
                    score += 2
            else:  # bearish
                recent_high = df['high'].iloc[pattern['index']:].max()
                if recent_high < pattern['level'] * (1 + tolerance):  # Not violated
                    score += 2
            
            # Cap score at 10
            score = min(score, 10)
            
            logger.debug(f"Pattern score: {score:.1f}")
            return score
            
        except DataValidationError as e:
            logger.error(f"Pattern validation error: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating pattern score: {e}")
            return 0.0
    
    def can_trade(self) -> bool:
        """Check if we can place new trades - shared implementation"""
        # Check daily loss limit
        if self.daily_pnl <= -self.config.DAILY_LOSS_LIMIT:
            logger.warning(f"Daily loss limit reached: ${self.daily_pnl}")
            return False
        
        # Check consecutive losses
        if self.consecutive_losses >= self.config.MAX_CONSECUTIVE_LOSSES:
            logger.warning(f"Max consecutive losses reached: {self.consecutive_losses}")
            return False
        
        # Check trading hours
        current_time = datetime.now().time()
        if not (self.config.SESSION_START <= current_time <= self.config.SESSION_END):
            logger.debug("Outside trading hours")
            return False
        
        # Check news blackout
        if current_time >= self.config.NEWS_BLACKOUT_START:
            logger.debug("In news blackout period")
            return False
        
        return True
    
    def calculate_position_size(self, stop_distance_ticks: int) -> int:
        """Calculate position size based on risk - shared implementation"""
        # Phase 1: Use fixed conservative size
        size = self.config.DEFAULT_POSITION_MGC
        
        # Reduce size after losses
        if self.consecutive_losses >= 1:
            size = max(self.config.MIN_POSITION_MGC, size // 2)
        
        # Ensure within limits
        size = max(self.config.MIN_POSITION_MGC, min(size, self.config.MAX_POSITION_MGC))
        
        logger.info(f"Position size: {size} MGC")
        return size
    
    async def update_monitoring(self) -> None:
        """Update monitoring using safe file operations"""
        safe_update_monitoring(self, self.file_ops)
    
    async def execute_signal(self, best_signal: Dict, best_score: float, candles: pd.DataFrame) -> None:
        """Execute a trading signal - shared logic"""
        logger.info(f"High quality {best_signal['type']} signal found! Score: {best_score:.1f}")
        
        # Get current price from latest candle
        current_price = candles.iloc[-1]['close']
        
        # Validate prices before proceeding
        try:
            current_price = self.validator.validate_price(current_price, "current_price")
        except DataValidationError as e:
            logger.error(f"Invalid current price: {e}")
            return
        
        # Calculate stops and targets
        if best_signal['type'] == 'bullish':
            # For bullish: stop below entry, target above
            stop_price = current_price - (self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE)
            target_price = current_price + (self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE * self.config.TP1_RATIO)
            side = 'BUY'
            
            # Validate pattern is below current price (valid support)
            if best_signal['level'] > current_price:
                logger.debug(f"Skipping bullish signal - level ${best_signal['level']:.2f} above current ${current_price:.2f}")
                return
        else:
            # For bearish: stop above entry, target below
            stop_price = current_price + (self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE)
            target_price = current_price - (self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE * self.config.TP1_RATIO)
            side = 'SELL'
            
            # Validate pattern is above current price (valid resistance)
            if best_signal['level'] < current_price:
                logger.debug(f"Skipping bearish signal - level ${best_signal['level']:.2f} below current ${current_price:.2f}")
                return
        
        # Calculate position size
        stop_distance_ticks = int(abs(current_price - stop_price) / self.config.TICK_SIZE)
        position_size = self.calculate_position_size(stop_distance_ticks)
        
        # Validate order parameters
        try:
            self.validator.validate_order_params(side, position_size, stop_price, target_price, current_price)
        except DataValidationError as e:
            logger.error(f"Invalid order parameters: {e}")
            return
        
        # Place order
        success = await self.place_order(side, position_size, stop_price, target_price)
        
        if success:
            self.last_signal_time = datetime.now()
            logger.success(f"Order placed successfully!")
    
    async def trading_loop(self):
        """Main trading loop - shared implementation"""
        logger.info("Starting trading loop...")
        
        signal_cooldown = getattr(self.config, 'SIGNAL_COOLDOWN_SECONDS', 300)
        main_loop_delay = getattr(self.config, 'MAIN_LOOP_DELAY_SECONDS', 30)
        
        while self.is_running:
            try:
                # Check if we can trade
                if not self.can_trade():
                    await asyncio.sleep(60)
                    continue
                
                # Get market data
                candles = await self.get_candles(
                    self.config.get_active_contract(),
                    self.config.PRIMARY_TIMEFRAME,
                    self.config.LOOKBACK_CANDLES
                )
                
                if candles.empty:
                    logger.warning("No candle data received")
                    await asyncio.sleep(30)
                    continue
                
                # Find patterns
                order_blocks = self.find_order_blocks(candles)
                
                # Score and filter patterns
                best_signal = None
                best_score = 0
                
                for pattern in order_blocks:
                    score = self.calculate_pattern_score(pattern, candles)
                    if score >= self.config.MIN_PATTERN_SCORE and score > best_score:
                        best_signal = pattern
                        best_score = score
                
                # Execute best signal if found
                if best_signal:
                    await self.execute_signal(best_signal, best_score, candles)
                    
                    # Wait before looking for next signal
                    await asyncio.sleep(signal_cooldown)
                
                # Update monitoring
                await self.update_monitoring()
                
                # Wait before next iteration
                await asyncio.sleep(main_loop_delay)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        """Main bot execution - can be overridden but usually shared"""
        try:
            # Connect to data source
            connected = await self.connect()
            if not connected:
                logger.error("Failed to connect")
                return
            
            logger.success("Bot started successfully!")
            
            # Create concurrent tasks
            tasks = [
                asyncio.create_task(self.trading_loop()),
                # TODO: Add position monitoring task
                # TODO: Add dedicated status updater task
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