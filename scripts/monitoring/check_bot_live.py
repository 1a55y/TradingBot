#!/usr/bin/env python3
"""Quick check of live bot status"""

import json
import os
from datetime import datetime
from pathlib import Path

print("=== T-BOT Live Status Check ===")
print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Check if bot process is running
import subprocess
try:
    result = subprocess.run(['pgrep', '-f', 'main.py --live'], capture_output=True, text=True)
    if result.stdout.strip():
        print("✅ Bot process is running (PID: {})".format(result.stdout.strip()))
    else:
        print("❌ Bot process not found")
except:
    print("⚠️  Could not check process status")

print()

# Check log files
log_dir = Path("logs")
if log_dir.exists():
    # Find most recent log file
    log_files = list(log_dir.glob("bot_*.log"))
    if log_files:
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        print(f"📄 Latest log: {latest_log.name}")
        
        # Show last 10 lines
        print("\n--- Last 10 log entries ---")
        with open(latest_log, 'r') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(line.strip())
    else:
        print("❌ No log files found")
        
    # Check status.json
    status_file = log_dir / "status.json"
    if status_file.exists():
        print(f"\n📊 Status file last modified: {datetime.fromtimestamp(status_file.stat().st_mtime)}")
        with open(status_file, 'r') as f:
            status = json.load(f)
            print(f"Bot alive: {status.get('is_alive', False)}")
            print(f"Balance: ${status.get('account', {}).get('balance', 0):,.2f}")
    else:
        print("\n❌ No status.json file found")
else:
    print("❌ No logs directory found")

# Check for today's bot.log
today_log = log_dir / "bot.log"
if today_log.exists():
    print(f"\n📝 bot.log exists (size: {today_log.stat().st_size} bytes)")
    print("--- Last 5 lines from bot.log ---")
    with open(today_log, 'r') as f:
        lines = f.readlines()
        for line in lines[-5:]:
            print(line.strip())