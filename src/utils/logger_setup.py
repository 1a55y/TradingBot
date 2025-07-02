"""Logger setup with fallback to standard logging if loguru not available"""
import logging
import sys
from pathlib import Path

try:
    from loguru import logger
    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    logger.add("logs/bot.log", rotation="1 day", retention="7 days", level="DEBUG")
    USING_LOGURU = True
except ImportError:
    # Fallback to standard logging
    USING_LOGURU = False
    
    # Create logger
    logger = logging.getLogger("Blue2.0")
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler
    Path("logs").mkdir(exist_ok=True)
    file_handler = logging.FileHandler("logs/bot.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Add convenience methods to match loguru
    logger.success = lambda msg: logger.info(f"✅ {msg}")
    logger.trace = logger.debug

# Export logger
__all__ = ['logger', 'USING_LOGURU']