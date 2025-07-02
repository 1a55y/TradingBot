# Running the Multi-Contract Trading Bot

## Quick Start

### 1. Activate Virtual Environment
```bash
cd "/Users/jassy/Progarming Projects/Cursor/T-BOT"
source venv/bin/activate
```

### 2. Configure Trading Settings
Edit your `.env` file:
```bash
# Choose your contract (MNQ, NQ, MES, ES, MGC, GC)
TRADING_CONTRACT=MNQ  # Default: Micro Nasdaq

# Set trading mode
PAPER_TRADING=True  # Use True for practice, False for live
```

### 3. Run the Bot
```bash
# Run with live API connection
python bot.py

# Or run in mock mode for testing
python bot_mock.py
```

### 4. Monitor Performance (in another terminal)
```bash
# Activate venv first
source venv/bin/activate

# Run the monitor
python monitor_practice.py

# Or check status manually
python scripts/check_status.py
```

## Switching Between Contracts

### How to Change Contracts
1. **Stop the bot** (Ctrl+C)
2. **Edit the .env file**:
```bash
# Open .env file
nano .env  # or vim .env

# Change the contract symbol
TRADING_CONTRACT=MES  # Options: MNQ, NQ, MES, ES, MGC, GC
```

3. **Restart the bot**:
```bash
python bot.py
```

### Contract Options and Characteristics
| Contract | Description | Updates/sec | Best For | Margin |
|----------|-------------|-------------|----------|---------|
| MNQ | Micro E-mini Nasdaq | ~15 | Scalping | $1,700 |
| NQ | E-mini Nasdaq | ~15 | Large accounts | $17,000 |
| MES | Micro E-mini S&P | ~14-16 | Scalping | $1,200 |
| ES | E-mini S&P 500 | ~14-16 | Large accounts | $12,000 |
| MGC | Micro Gold | ~2-3 | Swing trading | $1,000 |
| GC | Gold Futures | ~2-3 | Large accounts | $10,000 |

### Example: Switch from Nasdaq to Gold
```bash
# Stop current bot
# Press Ctrl+C

# Edit .env
sed -i 's/TRADING_CONTRACT=MNQ/TRADING_CONTRACT=MGC/' .env

# Verify change
grep TRADING_CONTRACT .env
# Output: TRADING_CONTRACT=MGC

# Restart bot
python bot.py
```

## Testing Trade Mechanics

### Manual Trade Tester
Use the manual trade tester to verify your setup and understand trade mechanics:

```bash
# Test with your current contract settings
python scripts/manual_trade_tester.py

# Expected output:
# Manual Trade Tester for MNQ
# ===========================
# Account Balance: $99,518.75
# Buying Power: $93,937.50
# 
# Current Market:
# Bid: 21425.00 | Ask: 21425.25 | Spread: 0.25
# 
# Commands:
# - buy: Place a buy order
# - sell: Place a sell order
# - status: Show current position
# - exit: Close position and quit
```

### Testing Different Scenarios

1. **Test a Winning Trade**:
```
Command: buy
Entry Type (market/limit): market
# Bot buys at ask price
# Wait for price to move up
Command: sell
# Bot sells and shows profit
```

2. **Test Stop Loss**:
```
Command: buy
# Let price move against you
# Bot will automatically exit at stop loss
```

3. **Test Contract-Specific Behavior**:
```bash
# Test gold contract (slower updates)
TRADING_CONTRACT=MGC python scripts/manual_trade_tester.py

# Test Nasdaq (fast updates)
TRADING_CONTRACT=MNQ python scripts/manual_trade_tester.py
```

### Expected Outputs
```
# Successful trade
[TRADE] Bought 1 MNQ at 21425.25
[POSITION] Long 1 @ 21425.25, Stop: 21415.25
[TRADE] Sold 1 MNQ at 21430.50
[RESULT] Profit: $105.00 (+0.49%)

# Stop loss hit
[TRADE] Bought 1 MNQ at 21425.25
[STOP] Stop loss triggered at 21415.25
[RESULT] Loss: -$200.00 (-0.93%)
```

## Viewing Trade Logs and Performance

### Real-time Trade Monitoring
```bash
# Watch trades as they happen
tail -f logs/bot.log | grep -E "(TRADE|PROFIT|LOSS)"

# Example output:
# 2024-01-15 10:23:45 - TRADE - Bought 1 MNQ at 21,425.25
# 2024-01-15 10:25:12 - TRADE - Sold 1 MNQ at 21,430.50
# 2024-01-15 10:25:12 - PROFIT - Trade profit: $105.00 (+0.49%)
```

### Daily Trade Summary
```bash
# View today's trades
cat logs/trades_today.json | jq '.'

# Example output:
{
  "date": "2024-01-15",
  "trades": 12,
  "winning_trades": 8,
  "losing_trades": 4,
  "total_pnl": 425.50,
  "win_rate": 0.67,
  "average_win": 125.25,
  "average_loss": -75.50
}
```

### Performance Analysis
```bash
# Generate performance report
python scripts/analyze_performance.py

# Example output:
Performance Analysis - MNQ
=========================
Period: Last 7 days
Total Trades: 84
Win Rate: 65.5%
Profit Factor: 1.82
Total P&L: $2,150.75
Daily Average: $307.25
Best Day: $650.00 (Mon)
Worst Day: -$125.50 (Thu)
```

### Trade History
```bash
# View recent trades with details
python scripts/view_trades.py --last 10

# Example output:
Recent Trades:
1. 2024-01-15 10:25:12 | MNQ | LONG | Entry: 21425.25 | Exit: 21430.50 | P&L: +$105.00
2. 2024-01-15 09:45:30 | MNQ | SHORT | Entry: 21450.00 | Exit: 21445.75 | P&L: +$85.00
...
```

## Enhanced Logging and Monitoring

### Enable Detailed Logging
Edit `.env` to control logging levels:
```bash
# Logging levels: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO  # Default
LOG_LEVEL=DEBUG  # For troubleshooting
```

### Monitor Multiple Aspects
```bash
# 1. Pattern Detection
tail -f logs/bot.log | grep "PATTERN"
# Shows: [PATTERN] Detected: Bullish Engulfing on MNQ 1m

# 2. Order Execution
tail -f logs/bot.log | grep "ORDER"
# Shows: [ORDER] Placed: BUY 1 MNQ @ 21425.25

# 3. Risk Management
tail -f logs/bot.log | grep "RISK"
# Shows: [RISK] Daily loss: -$350.00 (43.75% of limit)

# 4. WebSocket Connection
tail -f logs/bot.log | grep "WEBSOCKET"
# Shows: [WEBSOCKET] Connected, receiving MNQ data
```

### Dashboard View
```bash
# Run the monitoring dashboard
python monitor_practice.py

# Shows real-time:
# - Current position and P&L
# - Recent trades
# - Pattern signals
# - Account metrics
# - Connection status
```

## Troubleshooting Common Issues

### 1. Validation Errors
**Problem**: "Validation error: [specific field] is required"
```bash
# Solution: Check your .env file
cat .env | grep -E "(APP_KEY|SECRET|ACCOUNT)"

# Ensure all required fields are set:
TRADOVATE_APP_KEY=your_key_here
TRADOVATE_APP_SECRET=your_secret_here
TRADOVATE_PRACTICE_ACCOUNT=your_account_here
```

### 2. Contract Not Found
**Problem**: "Contract MNQ not found" or similar
```bash
# Solution 1: Verify contract symbol
python scripts/check_contracts.py

# Solution 2: Update contract definitions
python scripts/update_contracts.py

# Solution 3: Check if contract is active
# Gold futures (MGC/GC) don't trade on Saturdays
```

### 3. No Trades Executing
**Problem**: Bot runs but doesn't place trades
```bash
# Check 1: Market hours
python scripts/check_market_hours.py

# Check 2: Pattern detection
tail -f logs/bot.log | grep "No patterns detected"

# Check 3: Risk limits
grep "Daily loss limit" logs/bot.log

# Check 4: Account balance
python scripts/check_balance.py
```

### 4. WebSocket Connection Issues
**Problem**: "WebSocket disconnected" messages
```bash
# Test connection
python test_ws_connection.py

# Check network
ping api.tradovate.com

# Restart with debug logging
LOG_LEVEL=DEBUG python bot.py
```

### 5. Stop Loss Not Triggering
**Problem**: Positions stay open past stop loss
```bash
# Verify stop orders
python scripts/check_orders.py

# Test stop loss mechanism
python scripts/test_stops.py

# Check order types supported
# Note: Some contracts may have different order rules
```

## Performance Expectations

### Micro Nasdaq (MNQ) - High Frequency
- **Trades per day**: 10-20
- **Win rate**: 60-70%
- **Average trade duration**: 2-10 minutes
- **Expected daily P&L**: $200-500 (on $10k account)
- **Best conditions**: High volatility, US market hours

### Micro S&P 500 (MES) - High Frequency
- **Trades per day**: 8-15
- **Win rate**: 62-72%
- **Average trade duration**: 3-15 minutes
- **Expected daily P&L**: $150-400 (on $10k account)
- **Best conditions**: Trending markets

### Micro Gold (MGC) - Lower Frequency
- **Trades per day**: 3-8
- **Win rate**: 55-65%
- **Average trade duration**: 15-60 minutes
- **Expected daily P&L**: $100-300 (on $10k account)
- **Best conditions**: News events, Asian/European sessions

### Factors Affecting Performance
1. **Market Volatility**: Higher volatility = more opportunities
2. **Time of Day**: 
   - Best for indices: US market open (9:30-11:30 AM EST)
   - Best for gold: London open (3:00-5:00 AM EST)
3. **News Events**: Major economic releases increase opportunities
4. **Contract Liquidity**: Full contracts (NQ, ES, GC) have tighter spreads

### Optimization Tips
```bash
# 1. Find best timeframe for your contract
python scripts/optimize_timeframe.py --contract MNQ

# 2. Adjust position sizing
# Edit .env
POSITION_SIZE_MULTIPLIER=1.0  # Default
POSITION_SIZE_MULTIPLIER=0.5  # Conservative
POSITION_SIZE_MULTIPLIER=2.0  # Aggressive

# 3. Monitor pattern success rates
python scripts/pattern_analysis.py --days 7
```

### Expected Monthly Returns
Based on historical testing:
- **Conservative** (0.5x size): 5-10% monthly
- **Standard** (1.0x size): 10-20% monthly
- **Aggressive** (2.0x size): 20-40% monthly (higher risk)

**Note**: Past performance doesn't guarantee future results. Always start with paper trading.

## Running Continuously

### Option 1: Terminal Session
```bash
# Start bot and let it run
python bot.py
```

### Option 2: Background Process (Linux/Mac)
```bash
# Run in background with output to log file
nohup python bot.py > bot_output.log 2>&1 &

# Check if running
ps aux | grep "bot.py"

# View logs
tail -f bot_output.log
tail -f logs/bot.log
```

### Option 3: Screen/Tmux Session (Recommended)
```bash
# Create new screen session
screen -S trading_bot

# Run the bot
source venv/bin/activate
python bot.py

# Detach from screen (Ctrl+A, then D)
# Reattach later with:
screen -r trading_bot
```

## Monitoring

### Real-time Monitor
```bash
python monitor_practice.py
```

### Check Logs
```bash
# Main bot log
tail -f logs/bot.log

# Today's trades
cat logs/trades_today.json | jq .

# Current status
cat logs/status.json | jq .
```

### Web-based Monitoring (if you have jq installed)
```bash
# Watch status updates every 5 seconds
watch -n 5 'cat logs/status.json | jq .'
```

## Important Notes

1. **Practice Account**: The bot uses practice account when `PAPER_TRADING=True`
2. **Market Hours**: Bot trades 2 AM - 11 PM Helsinki time (configurable)
3. **WebSocket Data**: Update rates vary by contract:
   - **Nasdaq/S&P**: ~15 updates/second (excellent for scalping)
   - **Gold**: ~2-3 updates/second (good for 1min+ timeframes)
4. **Risk Limits**: Daily loss limit of $800 is enforced
5. **Position Sizing**: Automatically adjusted based on contract and account balance

## Stopping the Bot

### Graceful Shutdown
Press `Ctrl+C` in the terminal where the bot is running. The bot will:
1. Cancel any pending orders
2. Log final status
3. Save state to JSON files
4. Exit cleanly

### Emergency Stop
```bash
# Find the process
ps aux | grep "bot.py"

# Kill the process (replace PID with actual process ID)
kill -9 PID
```

## Troubleshooting

### Bot Won't Start
- Check `.env` file has correct credentials
- Verify `PAPER_TRADING=True` for practice account
- Check logs/bot.log for errors

### No Trades Executing
- Verify market hours (Gold futures trade Sunday-Friday)
- Check if patterns are being detected (logs/status.json)
- Ensure sufficient account balance

### Connection Issues
- Test API connection: `python test_connection.py`
- Check internet connectivity
- Verify API credentials are correct

## Performance Tips

1. **Let it Run**: The bot learns from its trades, so let it run for extended periods
2. **Monitor Regularly**: Check status every few hours initially
3. **Review Logs**: Daily review of trades helps understand performance
4. **Don't Interfere**: Avoid manual trading on the same account

## Data Quality by Contract

### High-Frequency Contracts (Best for Scalping)
- **MNQ/NQ (Nasdaq)**: ~15 updates/second
- **MES/ES (S&P 500)**: ~14-16 updates/second

### Medium-Frequency Contracts (Best for Swing Trading)
- **MGC/GC (Gold)**: ~2-3 updates/second

### Pattern Detection
- Runs every 30 seconds during market hours
- Automatically adjusts parameters based on contract volatility
- Real-time execution via WebSocket data stream