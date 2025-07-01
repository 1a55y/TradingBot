# Gold Futures Bot Monitoring System - Aligned with 10-Week Plan 🚀

Based on our practical implementation plan, here's the UPDATED monitoring approach focusing on simplicity and reliability.

## 1. 🥇 **JSON File Monitoring** (PRIMARY APPROACH - WEEKS 1-10)

Our main monitoring system - simple, bulletproof, and works from Day 1:

```python
# monitoring.py - Progressive implementation
import json
import os
from datetime import datetime, timedelta
import sqlite3  # Added later for better reliability

class MonitoringSystem:
    def __init__(self):
        os.makedirs('logs', exist_ok=True)
        
    def update_status(self, bot):
        """Write status every 30 seconds - overwrites file to prevent growth"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "is_alive": True,
            "account": {
                "balance": bot.broker.balance,
                "daily_pnl": bot.risk_manager.daily_pnl,
                "open_positions": len(bot.positions),
                "daily_trades": bot.risk_manager.daily_trades
            },
            "risk": {
                "can_trade": bot.risk_manager.can_trade(),
                "consecutive_losses": bot.risk_manager.consecutive_losses,
                "daily_loss_remaining": 800 + bot.risk_manager.daily_pnl,
                "emergency_stop": os.path.exists('EMERGENCY_STOP.txt')
            },
            "active_positions": [
                {
                    "symbol": p.symbol,
                    "side": p.side,
                    "quantity": p.quantity,
                    "entry": p.entry_price,
                    "unrealized_pnl": p.unrealized_pnl,
                    "stop": p.stop_loss,
                    "target": p.take_profit
                }
                for p in bot.positions
            ],
            "last_signal": {
                "time": bot.last_signal_time,
                "pattern": bot.last_signal_pattern,
                "score": bot.last_signal_score,
                "executed": bot.last_signal_executed
            },
            "learning": {
                "patterns_enabled": bot.learning_system.enabled_patterns if hasattr(bot, 'learning_system') else ["order_blocks"],
                "current_position_size": bot.learning_system.current_size if hasattr(bot, 'learning_system') else 5,
                "win_rate_last_20": bot.learning_system.recent_win_rate if hasattr(bot, 'learning_system') else 0.0,
                "total_trades": bot.learning_system.total_trades if hasattr(bot, 'learning_system') else 0
            },
            "errors": bot.recent_errors[-5:] if hasattr(bot, 'recent_errors') else [],
            "next_update": (datetime.now() + timedelta(seconds=30)).isoformat()
        }
        
        # Atomic write to prevent corruption
        with open('logs/status.json.tmp', 'w') as f:
            json.dump(status, f, indent=2)
        os.replace('logs/status.json.tmp', 'logs/status.json')
```

**Check Status Commands:**
```bash
# Quick status check
cat logs/status.json | jq .account

# Is bot alive?
cat logs/status.json | jq .is_alive

# Watch live updates
watch -n 5 'cat logs/status.json | jq "{alive: .is_alive, pnl: .account.daily_pnl, positions: .account.open_positions}"'

# Check if can trade
cat logs/status.json | jq .risk.can_trade

# View active positions
cat logs/status.json | jq .active_positions
```

## 2. 📊 **Trade & Signal Logging** (ESSENTIAL FROM WEEK 1)

Track every trade and signal for the learning system:

```python
# monitoring.py continued
def log_trade(self, trade_data):
    """Log trades for analysis and learning"""
    trade_record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "pattern": trade_data.pattern,
        "pattern_score": trade_data.score,
        "side": trade_data.side,
        "entry": trade_data.entry_price,
        "stop": trade_data.stop_loss,
        "target": trade_data.take_profit,
        "size": trade_data.quantity,
        "risk_amount": trade_data.quantity * abs(trade_data.entry_price - trade_data.stop_loss),
        "market_conditions": {
            "session": "NY" if self.is_ny_session() else "OTHER",
            "dxy_correlation": trade_data.dxy_corr,
            "volume_ratio": trade_data.volume_ratio,
            "atr": trade_data.atr,
            "time_of_day": datetime.now().strftime("%H:%M")
        },
        "outcome": None,  # Updated when trade closes
        "pnl": None,      # Updated when trade closes
        "exit_reason": None,  # stop/target/manual/emergency
        "hold_time": None  # Minutes in trade
    }
    
    # Today's trades file (resets daily)
    trades_file = 'logs/trades_today.json'
    
    if os.path.exists(trades_file):
        with open(trades_file, 'r') as f:
            trades = json.load(f)
    else:
        trades = {"trades": [], "summary": {}}
    
    trades["trades"].append(trade_record)
    
    # Update summary
    trades["summary"] = {
        "total_trades": len(trades["trades"]),
        "total_pnl": sum(t.get("pnl", 0) for t in trades["trades"] if t.get("pnl")),
        "open_trades": len([t for t in trades["trades"] if t["outcome"] is None]),
        "win_rate": self._calculate_win_rate(trades["trades"])
    }
    
    with open(trades_file, 'w') as f:
        json.dump(trades, f, indent=2)
    
    # Also append to permanent log
    with open('logs/all_trades.jsonl', 'a') as f:
        f.write(json.dumps(trade_record) + '\n')
    
    return trade_record["id"]

def log_signal(self, signal_data, executed=False):
    """Log ALL signals for analysis - not just executed ones"""
    with open('logs/signals.log', 'a') as f:
        f.write(f"{datetime.now().isoformat()} | "
                f"Pattern: {signal_data.pattern} | "
                f"Score: {signal_data.score} | "
                f"Executed: {executed} | "
                f"Reason: {signal_data.skip_reason if not executed else 'traded'}\n")
```

## 3. 🧠 **Learning System Data** (WEEKS 5-6+)

Self-learning system that improves over time:

```python
# learning_system.py integration with monitoring
class LearningSystem:
    def __init__(self):
        self.learning_file = 'logs/bot_learning.json'
        self.load_or_initialize()
        
    def update_pattern_performance(self, pattern, outcome, pnl, conditions):
        """Track pattern performance for adaptation"""
        if pattern not in self.pattern_stats:
            self.pattern_stats[pattern] = {
                "trades": 0,
                "wins": 0,
                "total_pnl": 0,
                "conditions_correlation": {}
            }
        
        stats = self.pattern_stats[pattern]
        stats["trades"] += 1
        if pnl > 0:
            stats["wins"] += 1
        stats["total_pnl"] += pnl
        stats["win_rate"] = stats["wins"] / stats["trades"]
        
        # Track condition correlations
        for condition, value in conditions.items():
            if condition not in stats["conditions_correlation"]:
                stats["conditions_correlation"][condition] = {"wins": 0, "total": 0}
            stats["conditions_correlation"][condition]["total"] += 1
            if pnl > 0:
                stats["conditions_correlation"][condition]["wins"] += 1
        
        # Save learning data
        self.save_learning_data()
        
        # Disable patterns with poor performance
        if stats["trades"] >= 20 and stats["win_rate"] < 0.4:
            self.enabled_patterns.remove(pattern)
            print(f"🚫 Disabling {pattern} - Win rate: {stats['win_rate']:.1%}")
```

## 4. 🚨 **Emergency Control System** (CRITICAL)

Simple file-based emergency controls:

```python
# Emergency controls via file system
def check_emergency_controls(self):
    """Check for emergency control files"""
    
    # EMERGENCY STOP - Flattens all and exits
    if os.path.exists('EMERGENCY_STOP.txt'):
        self.emergency_shutdown()
        return False
        
    # PAUSE TRADING - Stops new trades but keeps positions
    if os.path.exists('PAUSE_TRADING.txt'):
        self.trading_enabled = False
        
    # FLATTEN ALL - Closes positions but keeps running
    if os.path.exists('FLATTEN_ALL.txt'):
        self.broker.flatten_all()
        os.remove('FLATTEN_ALL.txt')
        
    # ADJUST RISK - Change position sizing
    if os.path.exists('ADJUST_RISK.txt'):
        with open('ADJUST_RISK.txt', 'r') as f:
            new_size = int(f.read().strip())
            self.risk_manager.default_size = new_size
        os.remove('ADJUST_RISK.txt')
    
    return True

# Claude can control bot with:
# echo "STOP" > EMERGENCY_STOP.txt
# echo "10" > ADJUST_RISK.txt
# touch PAUSE_TRADING.txt
```

## 5. 📈 **Performance Dashboard** (WEEK 7+ ENHANCEMENT)

Simple terminal dashboard using rich (optional enhancement):

```python
# terminal_dashboard.py - Future enhancement after JSON works
from rich.console import Console
from rich.table import Table
from rich.live import Live
import json

def display_bot_status():
    """Simple terminal dashboard reading JSON files"""
    console = Console()
    
    with open('logs/status.json', 'r') as f:
        status = json.load(f)
    
    with open('logs/trades_today.json', 'r') as f:
        trades = json.load(f)
    
    # Create status table
    table = Table(title="Gold Bot Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Status", "🟢 ALIVE" if status["is_alive"] else "🔴 DEAD")
    table.add_row("Daily P&L", f"${status['account']['daily_pnl']:+.2f}")
    table.add_row("Positions", str(status['account']['open_positions']))
    table.add_row("Can Trade", "YES" if status['risk']['can_trade'] else "NO")
    table.add_row("Win Rate", f"{trades['summary'].get('win_rate', 0):.1%}")
    
    console.print(table)

# Run with: watch -n 5 python terminal_dashboard.py
```

## 6. 🗄️ **SQLite Migration** (BETTER THAN JSON)

After Week 4, consider migrating to SQLite for better reliability:

```python
# Better than JSON - no corruption, better queries
class SQLiteMonitoring:
    def __init__(self):
        self.db = sqlite3.connect('logs/bot_data.db')
        self.init_tables()
        
    def init_tables(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS status (
                timestamp DATETIME PRIMARY KEY,
                is_alive BOOLEAN,
                balance REAL,
                daily_pnl REAL,
                positions INTEGER,
                can_trade BOOLEAN,
                data JSON
            )
        ''')
        
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                pattern TEXT,
                score REAL,
                side TEXT,
                entry REAL,
                stop REAL,
                target REAL,
                size INTEGER,
                outcome TEXT,
                pnl REAL,
                conditions JSON
            )
        ''')
```

## 🎯 **Implementation Timeline**

### Week 1-2: Basic JSON Status
- Just `status.json` with basic info
- Manual trade logging to `trades.log`

### Week 3-4: Add Trade Tracking
- Implement `trades_today.json`
- Add signal logging
- Basic win/loss tracking

### Week 5-6: Learning Integration
- Add `bot_learning.json`
- Pattern performance tracking
- Condition correlation analysis

### Week 7-8: Enhancements
- Consider SQLite migration
- Add terminal dashboard
- Implement emergency controls

### Week 9-10: Production Ready
- Full monitoring suite
- All safety controls tested
- Performance analytics working

## 🚀 **Key Commands for Monitoring**

```bash
# Create monitoring script: check_bot.sh
#!/bin/bash
echo "=== Gold Bot Status ==="
echo "Alive: $(jq .is_alive logs/status.json)"
echo "P&L: $(jq .account.daily_pnl logs/status.json)"
echo "Positions: $(jq '.active_positions | length' logs/status.json)"
echo "Can Trade: $(jq .risk.can_trade logs/status.json)"
echo ""
echo "=== Today's Performance ==="
jq .summary logs/trades_today.json
echo ""
echo "=== Recent Errors ==="
jq .errors logs/status.json

# Make executable: chmod +x check_bot.sh
# Run: ./check_bot.sh
```

**Remember**: Start with simple JSON files. They work, they're reliable, and Claude can read them easily. Fancy dashboards come AFTER the bot is profitable!