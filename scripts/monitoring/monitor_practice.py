#!/usr/bin/env python3
"""Monitor trading bot performance on practice account"""

import json
import sys
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))



def display_status():
    """Display current bot status"""
    try:
        # Read status file
        status_file = Path("logs/status.json")
        if not status_file.exists():
            print("⚠️  No status file found. Bot may not be running.")
            return
            
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        # Clear screen
        print("\033[2J\033[H")  # Clear screen and move cursor to top
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           T-BOT MONITOR - Practice Account                   ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        # Bot status
        is_alive = status.get('is_alive', False)
        if is_alive:
            print(f"🟢 Bot Status: RUNNING")
        else:
            print(f"🔴 Bot Status: STOPPED")
        
        print(f"📅 Last Update: {status.get('timestamp', 'Unknown')}")
        print()
        
        # Account info
        account = status.get('account', {})
        print("💰 Account Information:")
        print(f"   Balance: ${account.get('balance', 0):,.2f}")
        print(f"   Daily P&L: ${account.get('daily_pnl', 0):,.2f}")
        print(f"   Open Positions: {account.get('open_positions', 0)}")
        print()
        
        # Trading info
        trading = status.get('trading', {})
        print("📊 Trading Status:")
        print(f"   Can Trade: {'✅ Yes' if trading.get('can_trade') else '❌ No'}")
        print(f"   Stage: {trading.get('current_stage', 'Unknown')}")
        print()
        
        # Pattern analysis
        patterns = status.get('patterns', {})
        print("🎯 Pattern Analysis:")
        print(f"   Found: {patterns.get('found', 0)}")
        print(f"   High Quality: {patterns.get('high_quality', 0)}")
        print()
        
        # Today's trades
        trades_file = Path("logs/trades_today.json")
        if trades_file.exists():
            with open(trades_file, 'r') as f:
                trades_data = json.load(f)
                trades = trades_data.get('trades', [])
                summary = trades_data.get('summary', {})
                
                print("📈 Today's Performance:")
                print(f"   Total Trades: {summary.get('total', 0)}")
                print(f"   P&L: ${summary.get('pnl', 0):,.2f}")
                print(f"   Win Rate: {summary.get('win_rate', 0):.1f}%")
                
                if trades:
                    print(f"\n   Recent Trades:")
                    for trade in trades[-3:]:  # Show last 3 trades
                        print(f"   • {trade.get('time', 'N/A')} - {trade.get('side', 'N/A')} - P&L: ${trade.get('pnl', 0):.2f}")
        
        print("\n" + "─"*64)
        print("Press Ctrl+C to exit monitor")
        
    except Exception as e:
        print(f"Error reading status: {e}")


def main():
    """Main monitoring loop"""
    print("Starting T-BOT Monitor...")
    print("This will display the bot's status every 5 seconds.")
    print()
    
    try:
        while True:
            display_status()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")


if __name__ == "__main__":
    main()