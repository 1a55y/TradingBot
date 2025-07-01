"""Main entry point for Gold Trading Bot"""
import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.bot import GoldBot
from src.bot_mock import MockGoldBot
from src.bot_live import LiveGoldBot
from src.config import Config
from src.utils.logger_setup import logger

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gold Futures Trading Bot")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    parser.add_argument("--live", action="store_true", help="Run with live API connection")
    parser.add_argument("--live-mock", action="store_true", help="Run live bot with mock API")
    parser.add_argument("--test", action="store_true", help="Run test mode (30 seconds)")
    args = parser.parse_args()
    
    if args.mock:
        logger.info("Starting in MOCK mode...")
        bot = MockGoldBot()
    elif args.live_mock:
        logger.info("Starting LIVE bot with MOCK API...")
        logger.info(f"Paper Trading: {Config.PAPER_TRADING}")
        bot = LiveGoldBot(use_mock_api=True)
    elif args.live:
        logger.info("Starting in LIVE mode with TopStepX API...")
        logger.info(f"Paper Trading: {Config.PAPER_TRADING}")
        bot = LiveGoldBot()
    else:
        # Default to mock mode for safety
        logger.info("Starting in MOCK mode (default)...")
        bot = MockGoldBot()
    
    if args.test:
        # Test mode - run for 30 seconds
        async def test_run():
            bot_task = asyncio.create_task(bot.run())
            await asyncio.sleep(30)
            bot.is_running = False
            await asyncio.sleep(2)
            bot_task.cancel()
            logger.info("Test run complete")
        
        asyncio.run(test_run())
    else:
        # Normal mode
        asyncio.run(bot.run())

if __name__ == "__main__":
    main()
