"""Gold Futures Trading Bot - Mock Mode (Refactored)"""
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Dict
from src.core.base_bot import BaseGoldBot
from src.utils.logger_setup import logger
from src.utils.data_validator import DataValidationError

class MockGoldBot(BaseGoldBot):
    """Mock Gold Trading Bot for testing without real API"""
    
    def __init__(self):
        super().__init__()
        self.current_price = 2050.0  # Starting price
        self.price_history = []
        self.last_update = datetime.now(timezone.utc)
        
        logger.info(f"Starting price: ${self.current_price:.2f}")
    
    async def connect(self) -> bool:
        """Mock connection - always succeeds"""
        self.is_running = True
        return True
    
    async def disconnect(self) -> None:
        """Mock disconnect"""
        self.is_running = False
    
    def generate_mock_price(self) -> float:
        """Generate realistic gold price movements"""
        # Use config values instead of magic numbers
        volatility = self.config.MOCK_VOLATILITY
        trend = self.config.MOCK_TREND
        
        change = np.random.normal(trend, volatility)
        self.current_price *= (1 + change)
        
        # Keep price in realistic range
        self.current_price = max(
            self.config.MOCK_PRICE_RANGE_MIN,
            min(self.config.MOCK_PRICE_RANGE_MAX, self.current_price)
        )
        
        return self.current_price
    
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Generate mock historical candles"""
        try:
            logger.debug(f"Generating {limit} mock {timeframe} candles")
            
            # Generate timestamps
            freq_map = {'15m': '15min', '5m': '5min', '1h': '1h'}
            freq = freq_map.get(timeframe, '15min')
            
            timestamps = pd.date_range(end=datetime.now(timezone.utc), periods=limit, freq=freq)
            
            # Generate realistic OHLCV data
            candles = []
            base_price = self.current_price - (limit * 0.1)
            
            for i, ts in enumerate(timestamps):
                # Random but realistic price movement
                open_price = base_price + np.random.uniform(-5, 5)
                close_price = open_price + np.random.uniform(-10, 10)
                high_price = max(open_price, close_price) + np.random.uniform(0, 5)
                low_price = min(open_price, close_price) - np.random.uniform(0, 5)
                volume = np.random.uniform(1000, 5000)
                
                # Trend component
                base_price += np.random.uniform(-2, 3)
                
                candles.append({
                    'timestamp': ts,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })
            
            df = pd.DataFrame(candles)
            
            # Add some patterns for testing
            self._inject_test_patterns(df)
            
            # Validate the generated data
            df = self.validator.validate_candles_df(df)
            
            return df
            
        except DataValidationError as e:
            logger.error(f"Generated invalid mock data: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error generating mock candles: {e}")
            return pd.DataFrame()
    
    def _inject_test_patterns(self, df: pd.DataFrame) -> None:
        """Inject some order blocks for testing"""
        if len(df) < 50:
            return
        
        # Inject a bullish order block around 30 candles ago
        idx = len(df) - 30
        if idx >= 0 and idx < len(df):
            df.loc[idx, 'open'] = df.loc[idx, 'close'] + 15
            df.loc[idx, 'high'] = df.loc[idx, 'open'] + 2
            df.loc[idx, 'low'] = df.loc[idx, 'close'] - 1
            df.loc[idx, 'volume'] = df['volume'].mean() * 2.5
            
            # Strong move after
            if idx + 1 < len(df):
                df.loc[idx + 1, 'close'] = df.loc[idx, 'high'] + 10
                df.loc[idx + 1, 'high'] = df.loc[idx + 1, 'close'] + 3
        
        # Inject a bearish order block around 15 candles ago
        idx = len(df) - 15
        if idx >= 0 and idx < len(df):
            df.loc[idx, 'close'] = df.loc[idx, 'open'] + 12
            df.loc[idx, 'high'] = df.loc[idx, 'close'] + 2
            df.loc[idx, 'low'] = df.loc[idx, 'open'] - 1
            df.loc[idx, 'volume'] = df['volume'].mean() * 2.2
            
            # Strong move after
            if idx + 1 < len(df):
                df.loc[idx + 1, 'close'] = df.loc[idx, 'low'] - 8
                df.loc[idx + 1, 'low'] = df.loc[idx + 1, 'close'] - 3
    
    async def place_order(self, side: str, quantity: int, stop_price: float, target_price: float) -> bool:
        """Simulate order placement and execution"""
        try:
            # Validate order parameters
            self.validator.validate_order_params(
                side, quantity, stop_price, target_price, self.current_price
            )
            
            logger.info(f"MOCK: Placing {side} order @ ${self.current_price:.2f}")
            logger.info(f"Stop: ${stop_price:.2f}, Target: ${target_price:.2f}")
            
            # Simulate order execution
            trade_result = await self._simulate_trade_outcome(
                side, self.current_price, stop_price, target_price
            )
            
            return True
            
        except DataValidationError as e:
            logger.error(f"Invalid order parameters: {e}")
            return False
        except Exception as e:
            logger.error(f"Error simulating order: {e}")
            return False
    
    async def _simulate_trade_outcome(self, side: str, entry: float, stop: float, target: float) -> Dict:
        """Simulate a trade outcome for testing"""
        # Use config win probability
        win_probability = self.config.MOCK_BASE_WIN_PROBABILITY
        
        # Simulate execution delay
        await asyncio.sleep(1)
        
        if np.random.random() < win_probability:
            # Winner
            exit_price = target
            if side == 'BUY':
                pnl = (exit_price - entry) * self.config.DEFAULT_POSITION_MGC * self.config.TICK_VALUE / self.config.TICK_SIZE
            else:  # SELL
                pnl = (entry - exit_price) * self.config.DEFAULT_POSITION_MGC * self.config.TICK_VALUE / self.config.TICK_SIZE
            result = 'WIN'
        else:
            # Loser
            exit_price = stop
            pnl = -abs(stop - entry) * self.config.DEFAULT_POSITION_MGC * self.config.TICK_VALUE / self.config.TICK_SIZE
            result = 'LOSS'
            self.consecutive_losses += 1
        
        # Update daily P&L
        self.daily_pnl += pnl
        
        trade_result = {
            'timestamp': datetime.now(timezone.utc),
            'side': side,
            'entry': entry,
            'exit': exit_price,
            'stop': stop,
            'target': target,
            'pnl': pnl,
            'result': result,
            'size': self.config.DEFAULT_POSITION_MGC
        }
        
        self.trade_history.append(trade_result)
        
        logger.info(f"MOCK Trade {result}: {side} @ ${entry:.2f} -> ${exit_price:.2f}, P&L: ${pnl:+.2f}")
        
        if result == 'WIN':
            self.consecutive_losses = 0
        
        return trade_result
    
    async def trading_loop(self):
        """Main trading loop with price generation"""
        logger.info("Starting mock trading loop...")
        
        while self.is_running:
            try:
                # Update price
                self.generate_mock_price()
                
                # Use parent's trading loop logic
                await super().trading_loop()
                
            except Exception as e:
                logger.error(f"Error in mock trading loop: {e}")
                await asyncio.sleep(10)

async def main():
    """Entry point for mock bot"""
    bot = MockGoldBot()
    await bot.run()

if __name__ == "__main__":
    logger.info("Starting Gold Trading Bot in MOCK mode...")
    logger.info("Press Ctrl+C to stop")
    asyncio.run(main())