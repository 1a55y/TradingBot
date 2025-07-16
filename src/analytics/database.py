"""
SQLite database interface for storing and retrieving trading analytics.
"""

import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AnalyticsDatabase:
    """Manages SQLite database for trade analytics storage."""
    
    def __init__(self, db_path: str = "data/analytics.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    contract TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    quantity INTEGER NOT NULL,
                    pnl REAL,
                    r_multiple REAL,
                    pattern_type TEXT,
                    pattern_score REAL,
                    timeframes_aligned TEXT,
                    max_adverse_excursion REAL,
                    max_favorable_excursion REAL,
                    duration_minutes REAL,
                    risk_amount REAL,
                    commission REAL DEFAULT 0,
                    slippage REAL DEFAULT 0,
                    notes TEXT
                )
            """)
            
            # Pattern performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pattern_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    timeframe TEXT,
                    total_trades INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    avg_r_multiple REAL DEFAULT 0,
                    profit_factor REAL DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pattern_type, timeframe)
                )
            """)
            
            # Daily metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    date DATE PRIMARY KEY,
                    total_trades INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    profit_factor REAL DEFAULT 0,
                    sharpe_ratio REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    expectancy REAL DEFAULT 0,
                    avg_r_multiple REAL DEFAULT 0,
                    best_trade REAL DEFAULT 0,
                    worst_trade REAL DEFAULT 0,
                    avg_win REAL DEFAULT 0,
                    avg_loss REAL DEFAULT 0,
                    equity_high REAL,
                    equity_low REAL,
                    ending_equity REAL
                )
            """)
            
            # Equity curve table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equity_curve (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    equity REAL NOT NULL,
                    drawdown_pct REAL DEFAULT 0,
                    daily_return REAL DEFAULT 0
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_pattern ON trades(pattern_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_equity_timestamp ON equity_curve(timestamp)")
            
            conn.commit()
            logger.info(f"Analytics database initialized at {self.db_path}")
    
    def insert_trade(self, trade: Dict[str, Any]) -> bool:
        """
        Insert a new trade record.
        
        Args:
            trade: Trade dictionary with required fields
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert lists to JSON strings
                timeframes = trade.get('timeframes_aligned', [])
                if isinstance(timeframes, list):
                    timeframes = json.dumps(timeframes)
                
                cursor.execute("""
                    INSERT INTO trades (
                        id, timestamp, contract, side, entry_price, exit_price,
                        quantity, pnl, r_multiple, pattern_type, pattern_score,
                        timeframes_aligned, max_adverse_excursion, max_favorable_excursion,
                        duration_minutes, risk_amount, commission, slippage, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade['id'],
                    trade['timestamp'],
                    trade['contract'],
                    trade['side'],
                    trade['entry_price'],
                    trade.get('exit_price'),
                    trade['quantity'],
                    trade.get('pnl', 0),
                    trade.get('r_multiple', 0),
                    trade.get('pattern_type'),
                    trade.get('pattern_score', 0),
                    timeframes,
                    trade.get('max_adverse_excursion', 0),
                    trade.get('max_favorable_excursion', 0),
                    trade.get('duration_minutes', 0),
                    trade.get('risk_amount', 0),
                    trade.get('commission', 0),
                    trade.get('slippage', 0),
                    trade.get('notes', '')
                ))
                
                conn.commit()
                logger.info(f"Trade {trade['id']} inserted into database")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error inserting trade: {e}")
            return False
    
    def update_trade_exit(self, trade_id: str, exit_data: Dict[str, Any]) -> bool:
        """
        Update trade with exit information.
        
        Args:
            trade_id: Trade ID to update
            exit_data: Dictionary with exit price, pnl, duration, etc.
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE trades
                    SET exit_price = ?, pnl = ?, r_multiple = ?, duration_minutes = ?,
                        max_adverse_excursion = ?, max_favorable_excursion = ?
                    WHERE id = ?
                """, (
                    exit_data['exit_price'],
                    exit_data['pnl'],
                    exit_data.get('r_multiple', 0),
                    exit_data.get('duration_minutes', 0),
                    exit_data.get('max_adverse_excursion', 0),
                    exit_data.get('max_favorable_excursion', 0),
                    trade_id
                ))
                
                conn.commit()
                logger.info(f"Trade {trade_id} updated with exit data")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error updating trade: {e}")
            return False
    
    def get_trades(self, start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None,
                   pattern_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve trades with optional filters.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            pattern_type: Pattern type filter
            
        Returns:
            List of trade dictionaries
        """
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            trades = []
            for row in cursor.fetchall():
                trade = dict(row)
                # Parse JSON fields
                if trade.get('timeframes_aligned'):
                    try:
                        trade['timeframes_aligned'] = json.loads(trade['timeframes_aligned'])
                    except:
                        trade['timeframes_aligned'] = []
                trades.append(trade)
            
            return trades
    
    def update_pattern_performance(self, pattern_type: str, metrics: Dict[str, Any]):
        """
        Update pattern performance metrics.
        
        Args:
            pattern_type: Pattern type to update
            metrics: Performance metrics dictionary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO pattern_performance
                    (pattern_type, total_trades, win_rate, avg_r_multiple, 
                     profit_factor, total_pnl, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    pattern_type,
                    metrics['total_trades'],
                    metrics['win_rate'],
                    metrics['avg_r_multiple'],
                    metrics['profit_factor'],
                    metrics['total_pnl']
                ))
                
                conn.commit()
                logger.info(f"Updated performance metrics for pattern {pattern_type}")
                
        except sqlite3.Error as e:
            logger.error(f"Error updating pattern performance: {e}")
    
    def get_pattern_performance(self) -> List[Dict]:
        """Get performance metrics for all patterns."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pattern_performance ORDER BY win_rate DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def insert_daily_metrics(self, metrics: Dict[str, Any]):
        """
        Insert or update daily performance metrics.
        
        Args:
            metrics: Daily metrics dictionary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_metrics
                    (date, total_trades, win_rate, profit_factor, sharpe_ratio,
                     max_drawdown, total_pnl, expectancy, avg_r_multiple,
                     best_trade, worst_trade, avg_win, avg_loss,
                     equity_high, equity_low, ending_equity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics['date'],
                    metrics['total_trades'],
                    metrics['win_rate'],
                    metrics['profit_factor'],
                    metrics.get('sharpe_ratio', 0),
                    metrics.get('max_drawdown', 0),
                    metrics['total_pnl'],
                    metrics.get('expectancy', 0),
                    metrics.get('avg_r_multiple', 0),
                    metrics.get('best_trade', 0),
                    metrics.get('worst_trade', 0),
                    metrics.get('avg_win', 0),
                    metrics.get('avg_loss', 0),
                    metrics.get('equity_high'),
                    metrics.get('equity_low'),
                    metrics.get('ending_equity')
                ))
                
                conn.commit()
                logger.info(f"Daily metrics inserted for {metrics['date']}")
                
        except sqlite3.Error as e:
            logger.error(f"Error inserting daily metrics: {e}")
    
    def get_daily_metrics(self, days: int = 30) -> List[Dict]:
        """Get daily metrics for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_metrics 
                ORDER BY date DESC 
                LIMIT ?
            """, (days,))
            return [dict(row) for row in cursor.fetchall()]
    
    def insert_equity_point(self, equity: float, timestamp: Optional[datetime] = None):
        """
        Insert equity curve data point.
        
        Args:
            equity: Current equity value
            timestamp: Timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get previous equity for return calculation
                cursor.execute("""
                    SELECT equity FROM equity_curve 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                prev_row = cursor.fetchone()
                
                daily_return = 0
                if prev_row:
                    prev_equity = prev_row[0]
                    if prev_equity > 0:
                        daily_return = ((equity - prev_equity) / prev_equity) * 100
                
                # Calculate drawdown
                cursor.execute("""
                    SELECT MAX(equity) FROM equity_curve
                """)
                max_equity_row = cursor.fetchone()
                max_equity = max_equity_row[0] if max_equity_row and max_equity_row[0] else equity
                
                drawdown_pct = 0
                if max_equity > 0:
                    drawdown_pct = ((equity - max_equity) / max_equity) * 100
                
                cursor.execute("""
                    INSERT INTO equity_curve (timestamp, equity, drawdown_pct, daily_return)
                    VALUES (?, ?, ?, ?)
                """, (timestamp.isoformat(), equity, drawdown_pct, daily_return))
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Error inserting equity point: {e}")
    
    def get_equity_curve(self, days: Optional[int] = None) -> List[Dict]:
        """Get equity curve data."""
        query = "SELECT * FROM equity_curve"
        params = []
        
        if days:
            query += " WHERE timestamp >= datetime('now', '-{} days')".format(days)
        
        query += " ORDER BY timestamp ASC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get overall performance summary statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total trades and P&L
            cursor.execute("""
                SELECT COUNT(*) as total_trades,
                       SUM(pnl) as total_pnl,
                       AVG(pnl) as avg_pnl
                FROM trades
                WHERE exit_price IS NOT NULL
            """)
            stats = dict(cursor.fetchone() or {})
            
            # Win rate
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN pnl > 0 THEN 1 END) as winners,
                    COUNT(CASE WHEN pnl < 0 THEN 1 END) as losers
                FROM trades
                WHERE exit_price IS NOT NULL
            """)
            win_loss = dict(cursor.fetchone() or {})
            
            total = win_loss.get('winners', 0) + win_loss.get('losers', 0)
            stats['win_rate'] = (win_loss.get('winners', 0) / total * 100) if total > 0 else 0
            
            # Recent performance (last 30 days)
            cursor.execute("""
                SELECT AVG(win_rate) as avg_win_rate_30d,
                       AVG(profit_factor) as avg_profit_factor_30d,
                       AVG(sharpe_ratio) as avg_sharpe_30d
                FROM daily_metrics
                WHERE date >= date('now', '-30 days')
            """)
            recent_stats = dict(cursor.fetchone() or {})
            stats.update(recent_stats)
            
            return stats