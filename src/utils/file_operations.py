"""Atomic file operations to prevent corruption - CRITICAL FIX #2"""
# Standard library imports
import fcntl
import json
import os
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

# Local imports
from .logger_setup import logger

class FileOperationError(Exception):
    """Raised when file operations fail"""
    pass

class AtomicFileWriter:
    """Provides atomic file write operations to prevent corruption"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 0.1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def write_json(self, filepath: str, data: Dict[str, Any]) -> None:
        """
        Atomically write JSON data to file.
        
        This prevents partial writes and corruption from concurrent access.
        Uses write-to-temp-then-rename pattern for atomicity.
        """
        filepath = Path(filepath)
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Create temp file in same directory (for atomic rename)
        temp_fd, temp_path = tempfile.mkstemp(
            dir=filepath.parent,
            prefix=f".{filepath.stem}_",
            suffix=".tmp"
        )
        
        try:
            # Write to temp file
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomic rename (on same filesystem)
            os.replace(temp_path, filepath)
            
            logger.debug(f"Atomically wrote {filepath}")
            
        except Exception as e:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise FileOperationError(f"Failed to write {filepath}: {e}")
    
    def read_json(self, filepath: str) -> Dict[str, Any]:
        """
        Read JSON file with retry logic for concurrent access.
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileOperationError(f"File not found: {filepath}")
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with open(filepath, 'r') as f:
                    # Try to get shared lock (non-blocking)
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                    try:
                        data = json.load(f)
                        return data
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        
            except (IOError, OSError) as e:
                # File locked, retry
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
            except json.JSONDecodeError as e:
                # Corrupted file
                raise FileOperationError(f"Corrupted JSON in {filepath}: {e}")
        
        raise FileOperationError(
            f"Failed to read {filepath} after {self.max_retries} attempts: {last_error}"
        )
    
    def append_to_json_array(self, filepath: str, new_item: Any) -> None:
        """
        Atomically append an item to a JSON array file.
        """
        filepath = Path(filepath)
        
        # Read existing data
        if filepath.exists():
            data = self.read_json(filepath)
            if not isinstance(data, list):
                raise FileOperationError(f"Expected JSON array in {filepath}, got {type(data)}")
        else:
            data = []
        
        # Append new item
        data.append(new_item)
        
        # Write back atomically
        self.write_json(filepath, data)
    
    def update_json_field(self, filepath: str, updates: Dict[str, Any]) -> None:
        """
        Atomically update specific fields in a JSON object file.
        """
        filepath = Path(filepath)
        
        # Read existing data
        if filepath.exists():
            data = self.read_json(filepath)
            if not isinstance(data, dict):
                raise FileOperationError(f"Expected JSON object in {filepath}, got {type(data)}")
        else:
            data = {}
        
        # Update fields
        data.update(updates)
        
        # Write back atomically
        self.write_json(filepath, data)

class DayBoundaryHandler:
    """Handles day boundary transitions for daily files - CRITICAL FIX #3"""
    
    def __init__(self, archive_dir: str = "logs/archive"):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.file_writer = AtomicFileWriter()
        self._last_check_date = None
    
    def check_and_rotate_daily_files(self, current_time: datetime) -> bool:
        """
        Check if we've crossed a day boundary and rotate files if needed.
        Returns True if files were rotated.
        """
        current_date = current_time.date()
        
        # Skip if same day
        if self._last_check_date == current_date:
            return False
        
        # Check if trades_today.json exists and has yesterday's data
        trades_file = Path("logs/trades_today.json")
        
        if trades_file.exists():
            try:
                trades_data = self.file_writer.read_json(trades_file)
                
                # Check if data is from a previous day
                if trades_data.get('date') and trades_data['date'] != current_date.isoformat():
                    # Archive the old file
                    old_date = trades_data['date']
                    archive_path = self.archive_dir / f"trades_{old_date}.json"
                    
                    # Write to archive
                    self.file_writer.write_json(archive_path, trades_data)
                    
                    # Create new empty file for today
                    new_data = {
                        "date": current_date.isoformat(),
                        "trades": [],
                        "summary": {
                            "total": 0,
                            "pnl": 0.0,
                            "winners": 0,
                            "win_rate": 0.0
                        }
                    }
                    self.file_writer.write_json(trades_file, new_data)
                    
                    logger.info(f"Rotated daily trades file: {old_date} -> {current_date}")
                    
                    self._last_check_date = current_date
                    return True
                    
            except Exception as e:
                logger.error(f"Error rotating daily files: {e}")
        
        self._last_check_date = current_date
        return False
    
    def reset_daily_counters(self, bot) -> None:
        """Reset daily counters in bot instance"""
        if hasattr(bot, 'daily_pnl'):
            bot.daily_pnl = 0.0
            logger.info("Reset daily P&L to 0")
        
        if hasattr(bot, 'consecutive_losses'):
            # Don't reset consecutive losses - they span days
            pass
        
        if hasattr(bot, 'trade_history'):
            # Keep full history but could archive if needed
            pass

# Integration helpers for the bot
def create_safe_file_operations():
    """Create file operation instances for bot use"""
    return {
        'writer': AtomicFileWriter(),
        'day_handler': DayBoundaryHandler()
    }

def safe_update_monitoring(bot, file_ops: Dict) -> None:
    """Safe replacement for bot's update_monitoring method"""
    try:
        writer = file_ops['writer']
        day_handler = file_ops['day_handler']
        
        current_time = datetime.now(timezone.utc)
        
        # Check day boundary
        if day_handler.check_and_rotate_daily_files(current_time):
            day_handler.reset_daily_counters(bot)
        
        # Create status update
        status = {
            "timestamp": current_time.isoformat(),
            "is_alive": bot.is_running,
            "mode": getattr(bot, 'mode', 'PRODUCTION'),
            "account": {
                "balance": bot.config.ACCOUNT_SIZE + bot.daily_pnl,
                "daily_pnl": bot.daily_pnl,
                "open_positions": len(bot.positions),
                "consecutive_losses": bot.consecutive_losses,
                "total_trades": len(bot.trade_history)
            },
            "trading": {
                "can_trade": bot.can_trade(),
                "last_signal": bot.last_signal_time.isoformat() if bot.last_signal_time else None,
                "current_stage": bot.config.TRADING_STAGE,
            },
            "risk": {
                "daily_loss_remaining": bot.config.DAILY_LOSS_LIMIT + bot.daily_pnl,
                "position_size": bot.config.DEFAULT_POSITION_MGC,
                "max_risk_per_trade": bot.config.MAX_RISK_PER_TRADE
            },
            "performance": {
                "total_trades": len(bot.trade_history),
                "winners": len([t for t in bot.trade_history if t['result'] == 'WIN']),
                "losers": len([t for t in bot.trade_history if t['result'] == 'LOSS']),
                "win_rate": len([t for t in bot.trade_history if t['result'] == 'WIN']) / len(bot.trade_history) * 100 if bot.trade_history else 0
            },
            "next_update": (current_time + timedelta(seconds=30)).isoformat()
        }
        
        # Write status atomically
        writer.write_json('logs/status.json', status)
        
        # Update today's trades
        today_trades = [t for t in bot.trade_history 
                       if t['timestamp'].date() == current_time.date()]
        
        if today_trades:
            trades_summary = {
                "date": current_time.date().isoformat(),
                "trades": today_trades,
                "summary": {
                    "total": len(today_trades),
                    "pnl": sum(t['pnl'] for t in today_trades),
                    "winners": len([t for t in today_trades if t['result'] == 'WIN']),
                    "win_rate": len([t for t in today_trades if t['result'] == 'WIN']) / len(today_trades) * 100
                }
            }
            
            writer.write_json('logs/trades_today.json', trades_summary)
        
        logger.debug("Monitoring files updated atomically")
        
    except Exception as e:
        logger.error(f"Error updating monitoring: {e}")