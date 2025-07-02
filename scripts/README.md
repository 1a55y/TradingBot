# Scripts Directory Structure

This directory contains utility scripts for the T-BOT trading system.

## Directory Structure

```
scripts/
├── __init__.py
├── README.md
├── analysis/               # Market analysis and debugging tools
│   ├── __init__.py
│   ├── analyze_market.py   # Analyze market conditions and patterns
│   ├── debug_patterns.py   # Debug pattern detection logic
│   └── view_trade_logs.py  # View and analyze trade history
├── monitoring/             # Bot monitoring utilities
│   ├── __init__.py
│   ├── check_bot_live.py   # Check if bot is running and healthy
│   └── monitor_practice.py # Monitor practice trading sessions
├── check_status.py         # General bot status checker
├── force_trade.py          # Force a manual trade execution
├── run_practice_bot.py     # Run bot in practice mode
├── test_manual_trade.py    # Test trade mechanics manually
└── test_trade_logging.py   # Test trade logging functionality
```

## Script Descriptions

### Analysis Scripts
- **analyze_market.py**: Analyzes current market conditions, patterns, and opportunities
- **debug_patterns.py**: Helps debug pattern detection algorithms and thresholds
- **view_trade_logs.py**: Displays historical trade data with filtering options

### Monitoring Scripts
- **check_bot_live.py**: Verifies bot is connected and operating correctly
- **monitor_practice.py**: Real-time monitoring of practice trading sessions

### Utility Scripts
- **check_status.py**: Quick status check of all bot components
- **force_trade.py**: Manually trigger a trade for testing purposes
- **run_practice_bot.py**: Launch the bot in practice/paper trading mode
- **test_manual_trade.py**: Interactive tool to test trade calculations and risk management
- **test_trade_logging.py**: Verify trade logging is working correctly

## Usage Examples

### Test a manual trade setup:
```bash
# Interactive mode
python scripts/test_manual_trade.py

# Command line mode
python scripts/test_manual_trade.py LONG 22850 15
```

### Check bot status:
```bash
python scripts/check_status.py
```

### Run practice bot:
```bash
python scripts/run_practice_bot.py
```

### Analyze market conditions:
```bash
python scripts/analysis/analyze_market.py
```

## Notes
- All scripts include proper path handling to import from the src/ directory
- Scripts are designed to be run from the project root directory
- Each script includes help text when run without arguments or with --help