#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
"""Check bot status from JSON files"""
import json
import os
from datetime import datetime
from pathlib import Path

def check_status():
    """Display bot status from JSON files"""
    
    # Check if status file exists
    status_file = Path('logs/status.json')
    if not status_file.exists():
        print("❌ Bot not running (no status file found)")
        return
    
    try:
        # Read status
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        # Display status
        print("=" * 50)
        print("🤖 GOLD TRADING BOT STATUS")
        print("=" * 50)
        
        # Basic info
        timestamp = datetime.fromisoformat(status['timestamp'].replace('Z', '+00:00'))
        age = (datetime.now() - timestamp.replace(tzinfo=None)).total_seconds()
        
        if age > 120:  # More than 2 minutes old
            print(f"⚠️  Status is {int(age/60)} minutes old")
        else:
            print(f"✅ Bot is alive (updated {int(age)} seconds ago)")
        
        if 'mode' in status and status['mode'] == 'MOCK':
            print("🧪 Running in MOCK mode")
        
        # Account info
        account = status.get('account', {})
        print(f"\n💰 ACCOUNT:")
        print(f"   Balance: ${account.get('balance', 0):,.2f}")
        print(f"   Daily P&L: ${account.get('daily_pnl', 0):+,.2f}")
        print(f"   Open Positions: {account.get('open_positions', 0)}")
        print(f"   Consecutive Losses: {account.get('consecutive_losses', 0)}")
        print(f"   Total Trades: {account.get('total_trades', 0)}")
        
        # Trading info
        trading = status.get('trading', {})
        print(f"\n📊 TRADING:")
        print(f"   Can Trade: {'✅ Yes' if trading.get('can_trade') else '❌ No'}")
        print(f"   Current Stage: {trading.get('current_stage', 'Unknown')}")
        if 'current_price' in trading:
            print(f"   Gold Price: ${trading['current_price']:.2f}")
        
        # Risk info
        risk = status.get('risk', {})
        print(f"\n⚠️  RISK:")
        print(f"   Daily Loss Remaining: ${risk.get('daily_loss_remaining', 0):,.2f}")
        print(f"   Position Size: {risk.get('position_size', 0)} MGC")
        
        # Performance
        perf = status.get('performance', {})
        if perf.get('total_trades', 0) > 0:
            print(f"\n📈 PERFORMANCE:")
            print(f"   Total Trades: {perf['total_trades']}")
            print(f"   Winners: {perf.get('winners', 0)}")
            print(f"   Losers: {perf.get('losers', 0)}")
            print(f"   Win Rate: {perf.get('win_rate', 0):.1f}%")
        
        # Check today's trades
        trades_file = Path('logs/trades_today.json')
        if trades_file.exists():
            with open(trades_file, 'r') as f:
                trades_data = json.load(f)
            
            summary = trades_data.get('summary', {})
            if summary.get('total', 0) > 0:
                print(f"\n📅 TODAY'S TRADES:")
                print(f"   Trades: {summary['total']}")
                print(f"   P&L: ${summary.get('pnl', 0):+,.2f}")
                print(f"   Win Rate: {summary.get('win_rate', 0):.1f}%")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"❌ Error reading status: {e}")

if __name__ == "__main__":
    check_status()