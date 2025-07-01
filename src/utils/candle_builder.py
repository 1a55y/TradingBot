"""Build candles from real-time tick data"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import pandas as pd
from collections import deque
from src.utils.logger_setup import logger


class CandleBuilder:
    """Builds OHLCV candles from real-time tick data"""
    
    def __init__(self, timeframe_minutes: int = 15):
        self.timeframe_minutes = timeframe_minutes
        self.current_candle = None
        self.completed_candles = deque(maxlen=200)  # Keep last 200 candles
        self.tick_buffer = deque(maxlen=10000)  # Raw ticks for building
        
    def add_tick(self, price: float, volume: float = 1, timestamp: Optional[datetime] = None):
        """Add a new tick and update candles"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
            
        tick = {
            'price': price,
            'volume': volume,
            'timestamp': timestamp
        }
        self.tick_buffer.append(tick)
        
        # Calculate candle period
        candle_start = self._get_candle_start(timestamp)
        
        # Initialize or update current candle
        if self.current_candle is None or self.current_candle['timestamp'] != candle_start:
            # Complete previous candle if exists
            if self.current_candle is not None:
                self.completed_candles.append(self.current_candle.copy())
                logger.debug(f"Completed candle: O={self.current_candle['open']:.2f} H={self.current_candle['high']:.2f} L={self.current_candle['low']:.2f} C={self.current_candle['close']:.2f}")
            
            # Start new candle
            self.current_candle = {
                'timestamp': candle_start,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': volume
            }
        else:
            # Update current candle
            self.current_candle['high'] = max(self.current_candle['high'], price)
            self.current_candle['low'] = min(self.current_candle['low'], price)
            self.current_candle['close'] = price
            self.current_candle['volume'] += volume
    
    def _get_candle_start(self, timestamp: datetime) -> datetime:
        """Get the start time of the candle period"""
        minutes = (timestamp.minute // self.timeframe_minutes) * self.timeframe_minutes
        return timestamp.replace(minute=minutes, second=0, microsecond=0)
    
    def get_candles_df(self, include_current: bool = False) -> pd.DataFrame:
        """Get completed candles as DataFrame"""
        candles = list(self.completed_candles)
        
        if include_current and self.current_candle:
            candles.append(self.current_candle.copy())
        
        if not candles:
            return pd.DataFrame()
        
        df = pd.DataFrame(candles)
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    def get_latest_candles(self, count: int = 100, include_current: bool = False) -> pd.DataFrame:
        """Get the latest N candles"""
        df = self.get_candles_df(include_current)
        if df.empty:
            return df
        return df.tail(count)