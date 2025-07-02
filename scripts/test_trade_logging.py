#!/usr/bin/env python3
"""Test enhanced trade logging in paper trading mode"""
# Standard library imports
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from src.bot_live import LiveGoldBot
from src.utils.logger_setup import logger

async def test_trade_logging():
    """Test the enhanced trade logging functionality"""
    logger.info("Testing enhanced trade logging...")
    
    # Create bot instance in paper trading mode
    bot = LiveGoldBot(use_mock_api=True)
    
    try:
        # Connect to API
        connected = await bot.connect()
        if not connected:
            logger.error("Failed to connect")
            return
        
        # Simulate placing a trade
        logger.info("\n" + "="*60)
        logger.info("SIMULATING TRADE PLACEMENT")
        logger.info("="*60)
        
        # Test parameters
        side = "BUY"
        quantity = 2
        current_price = 20150.50  # Simulated MNQ price
        stop_price = 20120.00  # 30.5 points stop
        target_price = 20181.00  # 30.5 points target (1:1 RR)
        
        # Place order (will be paper trade)
        success = await bot.place_order(side, quantity, stop_price, target_price)
        
        if success:
            logger.success("Trade logged successfully!")
            
            # Generate daily summary
            logger.info("\n" + "="*60)
            logger.info("GENERATING DAILY SUMMARY")
            logger.info("="*60)
            bot.generate_daily_summary()
            
        else:
            logger.error("Failed to place order")
            
    except Exception as e:
        logger.error(f"Test error: {e}")
    finally:
        await bot.disconnect()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_trade_logging())