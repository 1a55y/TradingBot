#!/bin/bash
# Restart the bot with fixed monitoring

echo "=== Restarting T-BOT with monitoring fix ==="

# Kill existing bot process
echo "Stopping existing bot..."
pkill -f "main.py --live"
sleep 2

# Clear old status file to see fresh data
echo "Clearing old status file..."
rm -f logs/status.json

echo "Bot stopped. Now restart with:"
echo "python main.py --live"