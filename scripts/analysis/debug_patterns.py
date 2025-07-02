#!/usr/bin/env python3
"""Debug why no patterns are being detected"""

import asyncio
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.topstep_client import TopStepXClient
from src.core.base_bot import BaseGoldBot
from src.config import Config
from src.utils.logger_setup import logger


class PatternDebugger(BaseGoldBot):
    """Debug version with detailed pattern analysis"""
    
    async def connect(self):
        """Connect to API"""
        return True
        
    async def disconnect(self):
        """Disconnect"""
        pass
        
    async def get_candles(self, symbol, timeframe, limit):
        """Get candles from API"""
        data = await self.api_client.get_historical_data(symbol, timeframe, limit)
        if data:
            df = pd.DataFrame(data)
            # Ensure required columns exist
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    # Map potential column names
                    if col == 'timestamp' and 'time' in df.columns:
                        df['timestamp'] = df['time']
            return df
        return pd.DataFrame()
        
    async def place_order(self, order_data):
        """Mock order placement"""
        return {"success": True}
    
    async def execute_signal(self, signal, score, candles):
        """Override - just log, don't trade"""
        logger.info(f"Would execute: {signal}")
    
    async def debug_pattern_detection(self):
        """Analyze why patterns aren't being found"""
        print("\n=== PATTERN DETECTION DEBUGGER ===")
        print(f"Current time: {datetime.now()}")
        print(f"Min pattern score required: {Config.MIN_PATTERN_SCORE}/10")
        print("-" * 50)
        
        # Connect to API
        self.api_client = TopStepXClient()
        if not await self.api_client.connect():
            print("❌ Failed to connect to API")
            return
            
        # Get candles
        print("\n📊 Fetching candle data...")
        candles = await self.get_candles('MGC', '15m', 100)
        
        if candles.empty:
            print("❌ No candle data received")
            return
            
        print(f"✅ Got {len(candles)} candles")
        print(f"   Columns: {list(candles.columns)}")
        
        # Use the correct timestamp column name
        time_col = 'timestamp' if 'timestamp' in candles.columns else 'time'
        latest = candles.iloc[-1]
        print(f"   Latest: {latest.get(time_col, 'N/A')} - Close: ${latest.get('close', latest.get('c', 0)):.2f}")
        print(f"   Range: ${candles.get('low', candles.get('l', pd.Series([0]))).min():.2f} - ${candles.get('high', candles.get('h', pd.Series([0]))).max():.2f}")
        
        # Map column names
        open_col = 'open' if 'open' in candles.columns else 'o'
        high_col = 'high' if 'high' in candles.columns else 'h'
        low_col = 'low' if 'low' in candles.columns else 'l'
        close_col = 'close' if 'close' in candles.columns else 'c'
        
        # Calculate price movement
        price_range = candles[high_col].max() - candles[low_col].min()
        avg_candle_size = (candles[high_col] - candles[low_col]).mean()
        print(f"   Total range: ${price_range:.2f}")
        print(f"   Avg candle size: ${avg_candle_size:.2f}")
        
        # Debug order block detection
        print("\n🔍 Running pattern detection...")
        
        # Check basic requirements
        if len(candles) < 3:
            print("❌ Not enough candles (need at least 3)")
            return
            
        # Calculate candle properties
        candles['body_size'] = abs(candles[close_col] - candles[open_col])
        candles['is_bullish'] = candles[close_col] > candles[open_col]
        candles['body_ratio'] = candles['body_size'] / (candles[high_col] - candles[low_col] + 0.01)
        
        # Stats
        avg_body_size = candles['body_size'].mean()
        print(f"\n📊 Candle Statistics:")
        print(f"   Avg body size: ${avg_body_size:.2f}")
        print(f"   Avg body ratio: {candles['body_ratio'].mean():.2%}")
        
        # Find potential order blocks with relaxed criteria
        potential_obs = []
        
        for i in range(1, len(candles) - 2):
            prev_candle = candles.iloc[i-1]
            curr_candle = candles.iloc[i]
            next_candle = candles.iloc[i+1]
            
            # Bullish order block (bearish candle before bullish move)
            if (not curr_candle['is_bullish'] and  # Current is bearish
                next_candle['is_bullish'] and      # Next is bullish
                next_candle[close_col] > curr_candle[high_col]):  # Next breaks high
                
                displacement = next_candle[close_col] - curr_candle[high_col]
                displacement_ticks = displacement / Config.TICK_SIZE
                
                potential_obs.append({
                    'type': 'bullish',
                    'index': i,
                    'level': curr_candle[low_col],
                    'displacement_ticks': displacement_ticks,
                    'body_size': curr_candle['body_size'],
                    'body_ratio': curr_candle['body_ratio']
                })
                
            # Bearish order block
            elif (curr_candle['is_bullish'] and    # Current is bullish
                  not next_candle['is_bullish'] and  # Next is bearish
                  next_candle[close_col] < curr_candle[low_col]):  # Next breaks low
                
                displacement = curr_candle[low_col] - next_candle[close_col]
                displacement_ticks = displacement / Config.TICK_SIZE
                
                potential_obs.append({
                    'type': 'bearish',
                    'index': i,
                    'level': curr_candle[high_col],
                    'displacement_ticks': displacement_ticks,
                    'body_size': curr_candle['body_size'],
                    'body_ratio': curr_candle['body_ratio']
                })
        
        print(f"\n🎯 Found {len(potential_obs)} potential order blocks")
        
        if potential_obs:
            print("\n📋 Analyzing each potential OB:")
            for i, ob in enumerate(potential_obs):
                print(f"\n  OB #{i+1} ({ob['type']}):")
                print(f"    Level: ${ob['level']:.2f}")
                print(f"    Displacement: {ob['displacement_ticks']:.1f} ticks")
                print(f"    Body size: ${ob['body_size']:.2f}")
                print(f"    Body ratio: {ob['body_ratio']:.2%}")
                
                # Check why it might be filtered
                issues = []
                if ob['displacement_ticks'] < Config.MIN_OB_MOVE_TICKS:
                    issues.append(f"Displacement too small ({ob['displacement_ticks']:.1f} < {Config.MIN_OB_MOVE_TICKS} ticks)")
                if ob['body_size'] < avg_body_size:
                    issues.append(f"Body size below average (${ob['body_size']:.2f} < ${avg_body_size:.2f})")
                if ob['body_ratio'] < 0.5:
                    issues.append(f"Body ratio too small ({ob['body_ratio']:.2%} < 50%)")
                    
                if issues:
                    print("    ❌ Filtered because:")
                    for issue in issues:
                        print(f"       - {issue}")
                else:
                    print("    ✅ Passes basic criteria")
        
        # Now run actual detection
        print("\n🏃 Running actual bot detection...")
        order_blocks = self.find_order_blocks(candles)
        print(f"Bot found: {len(order_blocks)} order blocks")
        
        if len(order_blocks) == 0 and len(potential_obs) > 0:
            print("\n⚠️  Pattern detection is TOO STRICT!")
            print("   Potential patterns exist but are being filtered out")
            print(f"\n💡 Suggestions:")
            print(f"   1. Reduce MIN_OB_MOVE_TICKS from {Config.MIN_OB_MOVE_TICKS} to 10-15")
            print(f"   2. Lower MIN_PATTERN_SCORE from {Config.MIN_PATTERN_SCORE} to 5-6")
            print(f"   3. Check if market is ranging (no clear directional moves)")
        elif len(order_blocks) == 0 and len(potential_obs) == 0:
            print("\n📊 Market Analysis:")
            print("   No clear order blocks in current market structure")
            print("   This could be due to:")
            print("   - Ranging/consolidating market")
            print("   - Lack of institutional activity")
            print("   - Need to wait for clearer price action")
            
        # Disconnect
        await self.api_client.disconnect()


async def main():
    debugger = PatternDebugger()
    await debugger.debug_pattern_detection()


if __name__ == "__main__":
    asyncio.run(main())