# Running the Trading Bot on Practice Account

## Quick Start

### 1. Activate Virtual Environment
```bash
cd "/Users/jassy/Progarming Projects/Cursor/T-BOT"
source venv/bin/activate
```

### 2. Ensure Practice Mode
The bot will automatically use your practice account when `PAPER_TRADING=True` in your `.env` file.

### 3. Run the Bot
```bash
# Run with live API connection on practice account
python main.py --live

# Or run the dedicated practice script
python run_practice_bot.py
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

## Running Continuously

### Option 1: Terminal Session
```bash
# Start bot and let it run
python main.py --live
```

### Option 2: Background Process (Linux/Mac)
```bash
# Run in background with output to log file
nohup python main.py --live > bot_output.log 2>&1 &

# Check if running
ps aux | grep "main.py"

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
python main.py --live

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
2. **Market Hours**: Bot only trades during configured hours (check Config)
3. **WebSocket Data**: Real-time data updates at ~2.5/second for Gold
4. **Risk Limits**: Daily loss limit of $800 is enforced
5. **Position Sizing**: Starts with 5 contracts, adjusts based on performance

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
ps aux | grep "main.py"

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

## Data Quality

- **Gold (MGC)**: 2.5 updates/second - Good for 1-minute+ strategies
- **Data is Real-time**: No delay on practice account with WebSocket
- **Pattern Detection**: Runs every 30 seconds during market hours