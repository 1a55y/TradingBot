#!/usr/bin/env python3
"""
Force a trade for testing purposes
This bypasses pattern detection and places a trade immediately
"""

# Standard library imports
import asyncio
import os
import sys
from datetime import datetime, timezone

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local imports
from src.bot_live import LiveGoldBot
from src.config import Config
from src.utils.logger_setup import logger

async def force_trade(direction='LONG', use_market_price=True, entry_price=None):
    """Force a trade without waiting for patterns"""
    
    logger.info(f"FORCING {direction} TRADE FOR TESTING")
    logger.info("=" * 60)
    
    # Initialize bot
    bot = LiveGoldBot(use_mock_api=False)
    
    try:
        # Connect to API
        if not await bot.connect():
            logger.error("Failed to connect to API")
            return
        
        # Wait for WebSocket to get real-time price
        await asyncio.sleep(2)
        
        # Get current market price
        if use_market_price and bot.current_price > 0:
            current_price = bot.current_price
            logger.info(f"Using WebSocket price: ${current_price:.2f}")
        elif entry_price:
            current_price = entry_price
            logger.info(f"Using specified price: ${current_price:.2f}")
        else:
            # Fallback to API
            market_data = await bot.api_client.get_market_data(Config.SYMBOL)
            if market_data:
                current_price = (market_data['bid'] + market_data['ask']) / 2
                logger.info(f"Using API price: ${current_price:.2f}")
            else:
                logger.error("Could not get market price")
                return
        
        # Calculate stop and target
        if direction == 'LONG':
            stop_price = current_price - (Config.DEFAULT_STOP_TICKS * Config.TICK_SIZE)
            target_price = current_price + (Config.DEFAULT_STOP_TICKS * Config.TICK_SIZE * Config.TP1_RATIO)
            side = 'BUY'
        else:  # SHORT
            stop_price = current_price + (Config.DEFAULT_STOP_TICKS * Config.TICK_SIZE)
            target_price = current_price - (Config.DEFAULT_STOP_TICKS * Config.TICK_SIZE * Config.TP1_RATIO)
            side = 'SELL'
        
        # Use default position size
        position_size = Config.DEFAULT_POSITION_MNQ
        
        # Log trade details
        logger.info(f"\n📊 FORCED TRADE DETAILS:")
        logger.info(f"   Direction: {side}")
        logger.info(f"   Entry: ${current_price:.2f}")
        logger.info(f"   Stop: ${stop_price:.2f} ({Config.DEFAULT_STOP_TICKS} ticks)")
        logger.info(f"   Target: ${target_price:.2f}")
        logger.info(f"   Position Size: {position_size} contracts")
        
        # Calculate risk
        risk = abs(current_price - stop_price) * position_size * Config.TICK_VALUE / Config.TICK_SIZE
        logger.info(f"   Risk: ${risk:.2f}")
        
        # Force the trade
        logger.info(f"\n🚀 PLACING {side} ORDER...")
        success = await bot.place_order(side, position_size, stop_price, target_price)
        
        if success:
            logger.success(f"✅ TRADE PLACED SUCCESSFULLY!")
            
            # Wait a moment for position update
            await asyncio.sleep(2)
            
            # Check positions
            positions = await bot.api_client.get_positions()
            if positions:
                logger.info(f"\n📋 OPEN POSITIONS:")
                for pos in positions:
                    logger.info(f"   {pos}")
        else:
            logger.error("❌ TRADE FAILED!")
        
        # Update monitoring
        await bot.update_monitoring()
        
    except Exception as e:
        logger.error(f"Error forcing trade: {e}")
    finally:
        await bot.disconnect()

def main():
    """Main entry point"""
    
    # Parse arguments
    direction = 'LONG'
    if len(sys.argv) > 1:
        direction = sys.argv[1].upper()
        if direction not in ['LONG', 'SHORT']:
            print("Usage: python force_trade.py [LONG|SHORT] [entry_price]")
            sys.exit(1)
    
    entry_price = None
    if len(sys.argv) > 2:
        try:
            entry_price = float(sys.argv[2])
        except ValueError:
            print("Invalid entry price")
            sys.exit(1)
    
    # Run the force trade
    asyncio.run(force_trade(direction, entry_price is None, entry_price))

if __name__ == "__main__":
    main()