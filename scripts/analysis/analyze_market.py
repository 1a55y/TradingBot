#!/usr/bin/env python3
"""Analyze current market conditions to understand why no patterns"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.topstep_client import TopStepXClient
from src.config import Config
from src.utils.logger_setup import logger


async def analyze_market():
    """Deep dive into current market conditions"""
    print("\n=== MARKET CONDITION ANALYZER ===")
    print(f"Time: {datetime.now()}")
    print(f"Settings: MIN_OB_MOVE_TICKS={Config.MIN_OB_MOVE_TICKS}, MIN_PATTERN_SCORE={Config.MIN_PATTERN_SCORE}")
    print("-" * 50)
    
    # Connect to API
    client = TopStepXClient()
    if not await client.connect():
        print("❌ Failed to connect")
        return
        
    # Get different timeframes
    timeframes = ['5m', '15m', '30m', '1h']
    
    for tf in timeframes:
        print(f"\n📊 {tf} Timeframe Analysis:")
        candles_data = await client.get_historical_data('MGC', tf, 50)
        
        if not candles_data:
            print(f"   ❌ No data for {tf}")
            continue
            
        df = pd.DataFrame(candles_data)
        
        # Map columns
        df = df.rename(columns={
            't': 'timestamp',
            'o': 'open',
            'h': 'high', 
            'l': 'low',
            'c': 'close',
            'v': 'volume'
        })
        
        # Basic stats
        price_range = df['high'].max() - df['low'].min()
        avg_range = (df['high'] - df['low']).mean()
        avg_body = abs(df['close'] - df['open']).mean()
        volatility = df['close'].pct_change().std() * 100
        
        print(f"   Price range: ${price_range:.2f}")
        print(f"   Avg candle range: ${avg_range:.2f} ({avg_range/Config.TICK_SIZE:.1f} ticks)")
        print(f"   Avg body size: ${avg_body:.2f}")
        print(f"   Volatility: {volatility:.2f}%")
        
        # Look for potential patterns
        bullish_moves = 0
        bearish_moves = 0
        ranging = 0
        
        for i in range(1, len(df)-1):
            curr = df.iloc[i]
            next_c = df.iloc[i+1]
            
            # Check for moves
            if next_c['close'] > curr['high'] + (Config.MIN_OB_MOVE_TICKS * Config.TICK_SIZE):
                bullish_moves += 1
            elif next_c['close'] < curr['low'] - (Config.MIN_OB_MOVE_TICKS * Config.TICK_SIZE):
                bearish_moves += 1
            else:
                ranging += 1
                
        print(f"   Bullish breaks: {bullish_moves}")
        print(f"   Bearish breaks: {bearish_moves}")
        print(f"   Ranging candles: {ranging}")
        
        # Market structure
        trend = "BULLISH" if df.iloc[-1]['close'] > df.iloc[0]['close'] else "BEARISH"
        trend_strength = abs(df.iloc[-1]['close'] - df.iloc[0]['close']) / df.iloc[0]['close'] * 100
        print(f"   Overall trend: {trend} ({trend_strength:.2f}%)")
    
    # Check last 10 15m candles in detail
    print("\n🔍 Last 10 candles (15m) detailed:")
    candles_data = await client.get_historical_data('MGC', '15m', 10)
    if candles_data:
        df = pd.DataFrame(candles_data)
        df = df.rename(columns={'t': 'time', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
        
        for i, row in df.iterrows():
            body = abs(row['close'] - row['open'])
            range_size = row['high'] - row['low']
            direction = "🟢" if row['close'] > row['open'] else "🔴"
            print(f"   {i}: {direction} O:{row['open']:.2f} H:{row['high']:.2f} L:{row['low']:.2f} C:{row['close']:.2f} | Body:${body:.2f} Range:${range_size:.2f}")
    
    print("\n💡 Analysis Summary:")
    print("   - If mostly ranging: Market is consolidating, fewer patterns")
    print("   - If low volatility: Not enough movement for patterns")
    print("   - If no breaks > 10 ticks: Patterns exist but too small")
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(analyze_market())