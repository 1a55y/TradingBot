#!/usr/bin/env python3
"""Run the trading bot continuously on practice account with real-time data"""

import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.bot_live import LiveGoldBot
from src.api.topstep_websocket_client import TopStepXWebSocketClient
from src.config import Config
from src.utils.logger_setup import logger


async def run_practice_bot():
    """Run the bot on practice account with real-time data"""
    
    # Force practice account
    Config.PAPER_TRADING = True
    
    logger.info("="*60)
    logger.info("🤖 STARTING GOLD TRADING BOT - PRACTICE ACCOUNT")
    logger.info("="*60)
    logger.info(f"Account ID: {Config.PRACTICE_ACCOUNT_ID}")
    logger.info(f"Symbol: {Config.SYMBOL}")
    logger.info(f"Paper Trading: {Config.PAPER_TRADING}")
    logger.info(f"Time: {datetime.now()}")
    logger.info("="*60)
    
    # Create and run the bot
    bot = LiveGoldBot()
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n⚠️  Shutdown signal received, stopping bot...")
        bot.is_running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the bot
        await bot.run()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           T-BOT - Gold Trading Bot (Practice Mode)           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Trading: Micro Gold Futures (MGC)                          ║
║  Account: Practice Account                                   ║
║  Data: Real-time WebSocket                                   ║
║                                                              ║
║  Press Ctrl+C to stop the bot safely                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(run_practice_bot())