"""Data validation for trading bot - CRITICAL FIX #1"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime
from .logger_setup import logger

class DataValidationError(Exception):
    """Raised when data validation fails"""
    pass

class DataValidator:
    """Validates all market data before use in trading decisions"""
    
    def __init__(self, config):
        self.config = config
        # Reasonable price ranges for gold
        # Accept wider range since TopStepX returns prices in different formats
        self.MIN_GOLD_PRICE = 100.0    # Minimum reasonable gold price
        self.MAX_GOLD_PRICE = 10000.0  # Maximum reasonable gold price
        self.MAX_PRICE_CHANGE_PCT = 0.05  # 5% max change per candle
        
    def validate_price(self, price: float, field_name: str = "price") -> float:
        """Validate a single price value"""
        # Check if price is a valid number
        if not isinstance(price, (int, float)):
            raise DataValidationError(f"{field_name} must be numeric, got {type(price)}")
        
        # Check for NaN
        if pd.isna(price) or np.isnan(price):
            raise DataValidationError(f"{field_name} is NaN")
        
        # Check for negative or zero
        if price <= 0:
            raise DataValidationError(f"{field_name} must be positive, got {price}")
        
        # Check reasonable range for gold
        if price < self.MIN_GOLD_PRICE or price > self.MAX_GOLD_PRICE:
            raise DataValidationError(
                f"{field_name} {price} outside reasonable range "
                f"[{self.MIN_GOLD_PRICE}, {self.MAX_GOLD_PRICE}]"
            )
        
        return float(price)
    
    def validate_candle(self, candle: Dict) -> Dict:
        """Validate a single OHLCV candle"""
        required_fields = ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        
        # Check all fields present
        for field in required_fields:
            if field not in candle:
                raise DataValidationError(f"Missing required field: {field}")
        
        # Validate prices
        o = self.validate_price(candle['open'], 'open')
        h = self.validate_price(candle['high'], 'high')
        l = self.validate_price(candle['low'], 'low')
        c = self.validate_price(candle['close'], 'close')
        
        # Validate OHLC relationships
        if h < max(o, c):
            raise DataValidationError(f"High {h} less than max(open {o}, close {c})")
        
        if l > min(o, c):
            raise DataValidationError(f"Low {l} greater than min(open {o}, close {c})")
        
        if h < l:
            raise DataValidationError(f"High {h} less than low {l}")
        
        # Validate volume
        volume = candle['volume']
        if not isinstance(volume, (int, float)) or volume < 0:
            raise DataValidationError(f"Invalid volume: {volume}")
        
        # Validate timestamp
        if not isinstance(candle['timestamp'], (datetime, pd.Timestamp)):
            raise DataValidationError(f"Invalid timestamp type: {type(candle['timestamp'])}")
        
        return candle
    
    def validate_candles_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate a DataFrame of candles"""
        if df.empty:
            raise DataValidationError("Empty candles DataFrame")
        
        if len(df) < 3:
            raise DataValidationError(f"Insufficient candles: {len(df)}, need at least 3")
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise DataValidationError(f"Missing columns: {missing_cols}")
        
        # Check for NaN values
        if df[required_columns].isna().any().any():
            nan_counts = df[required_columns].isna().sum()
            raise DataValidationError(f"NaN values found: {nan_counts[nan_counts > 0].to_dict()}")
        
        # Validate price ranges
        for col in ['open', 'high', 'low', 'close']:
            min_price = df[col].min()
            max_price = df[col].max()
            
            if min_price <= 0:
                raise DataValidationError(f"Negative/zero price in {col}: {min_price}")
            
            if min_price < self.MIN_GOLD_PRICE or max_price > self.MAX_GOLD_PRICE:
                raise DataValidationError(
                    f"{col} prices outside reasonable range: [{min_price}, {max_price}]"
                )
        
        # Validate OHLC relationships
        invalid_high = (df['high'] < df[['open', 'close']].max(axis=1)).sum()
        if invalid_high > 0:
            raise DataValidationError(f"{invalid_high} candles have high < max(open, close)")
        
        invalid_low = (df['low'] > df[['open', 'close']].min(axis=1)).sum()
        if invalid_low > 0:
            raise DataValidationError(f"{invalid_low} candles have low > min(open, close)")
        
        # Check for extreme price movements
        price_changes = df['close'].pct_change().abs()
        extreme_moves = price_changes[price_changes > self.MAX_PRICE_CHANGE_PCT]
        if len(extreme_moves) > 0:
            raise DataValidationError(
                f"Extreme price movements detected: {extreme_moves.max():.1%} "
                f"(max allowed: {self.MAX_PRICE_CHANGE_PCT:.1%})"
            )
        
        # Validate volume
        if (df['volume'] < 0).any():
            raise DataValidationError("Negative volume detected")
        
        logger.debug(f"Validated {len(df)} candles successfully")
        return df
    
    def validate_pattern(self, pattern: Dict) -> Dict:
        """Validate a detected pattern"""
        required_fields = ['type', 'level', 'index', 'timestamp']
        
        for field in required_fields:
            if field not in pattern:
                raise DataValidationError(f"Pattern missing required field: {field}")
        
        # Validate type
        if pattern['type'] not in ['bullish', 'bearish']:
            raise DataValidationError(f"Invalid pattern type: {pattern['type']}")
        
        # Validate level
        self.validate_price(pattern['level'], 'pattern level')
        
        # Validate index
        if not isinstance(pattern['index'], int) or pattern['index'] < 0:
            raise DataValidationError(f"Invalid pattern index: {pattern['index']}")
        
        return pattern
    
    def validate_order_params(self, side: str, quantity: int, stop: float, target: float, entry: float) -> None:
        """Validate order parameters before placing"""
        # Validate side
        if side not in ['BUY', 'SELL']:
            raise DataValidationError(f"Invalid order side: {side}")
        
        # Validate quantity
        if not isinstance(quantity, int) or quantity <= 0:
            raise DataValidationError(f"Invalid quantity: {quantity}")
        
        if quantity < self.config.MIN_POSITION_MGC or quantity > self.config.MAX_POSITION_MGC:
            raise DataValidationError(
                f"Quantity {quantity} outside allowed range "
                f"[{self.config.MIN_POSITION_MGC}, {self.config.MAX_POSITION_MGC}]"
            )
        
        # Validate prices
        self.validate_price(stop, 'stop price')
        self.validate_price(target, 'target price')
        self.validate_price(entry, 'entry price')
        
        # Validate stop loss distance
        stop_distance = abs(entry - stop)
        max_stop_distance = self.config.MAX_STOP_TICKS * self.config.TICK_SIZE
        
        if stop_distance > max_stop_distance:
            raise DataValidationError(
                f"Stop distance ${stop_distance:.2f} exceeds maximum "
                f"${max_stop_distance:.2f}"
            )
        
        # Validate logical relationships
        if side == 'BUY':
            if stop >= entry:
                raise DataValidationError(f"Buy stop {stop} must be below entry {entry}")
            if target <= entry:
                raise DataValidationError(f"Buy target {target} must be above entry {entry}")
        else:  # SELL
            if stop <= entry:
                raise DataValidationError(f"Sell stop {stop} must be above entry {entry}")
            if target >= entry:
                raise DataValidationError(f"Sell target {target} must be below entry {entry}")
        
        logger.debug(f"Validated {side} order: qty={quantity}, entry={entry:.2f}, stop={stop:.2f}, target={target:.2f}")

# Example usage wrapper for bot integration
def safe_get_candles(get_candles_func, validator: DataValidator, *args, **kwargs) -> pd.DataFrame:
    """Wrapper to validate candles data"""
    try:
        df = get_candles_func(*args, **kwargs)
        return validator.validate_candles_df(df)
    except DataValidationError as e:
        logger.error(f"Data validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error getting candles: {e}")
        raise DataValidationError(f"Failed to get valid candle data: {e}")