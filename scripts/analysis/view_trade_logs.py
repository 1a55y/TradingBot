#!/usr/bin/env python3
"""View and analyze trade execution logs"""
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

def view_trade_logs():
    """View and analyze trade execution logs"""
    trade_log_file = Path('logs/trade_executions.json')
    
    if not trade_log_file.exists():
        print("No trade logs found yet.")
        return
    
    try:
        with open(trade_log_file, 'r') as f:
            trades = json.load(f)
        
        if not trades:
            print("No trades recorded yet.")
            return
        
        print("=" * 100)
        print("TRADE EXECUTION LOG ANALYSIS")
        print("=" * 100)
        print(f"Total Trades: {len(trades)}")
        print("-" * 100)
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(trades)
        
        # Display each trade
        for i, trade in enumerate(trades, 1):
            print(f"\nTrade #{i}")
            print("-" * 50)
            print(f"Order ID: {trade.get('order_id')}")
            print(f"Timestamp: {trade.get('entry_timestamp')}")
            print(f"Side: {trade.get('side')}")
            print(f"Quantity: {trade.get('quantity')}")
            print(f"Entry Price: ${trade.get('entry_price', 0):.2f}")
            print(f"Stop Loss: ${trade.get('stop_price', 0):.2f}")
            print(f"Take Profit: ${trade.get('target_price', 0):.2f}")
            print(f"Risk Amount: ${trade.get('risk_amount', 0):.2f}")
            print(f"R:R Ratio: 1:{trade.get('risk_reward_ratio', 0):.2f}")
            print(f"Status: {trade.get('status')}")
            
            if trade.get('status') == 'filled':
                print(f"Fill Price: ${trade.get('fill_price', trade.get('entry_price', 0)):.2f}")
                print(f"Slippage: ${trade.get('slippage', 0):.2f}")
                print(f"Slippage Cost: ${trade.get('slippage_cost', 0):.2f}")
            
            if trade.get('status') == 'closed':
                print(f"Exit Price: ${trade.get('exit_price', 0):.2f}")
                print(f"P&L: ${trade.get('realized_pnl', 0):.2f}")
                print(f"R-Multiple: {trade.get('r_multiple', 0):.2f}R")
        
        # Summary statistics
        print("\n" + "=" * 100)
        print("SUMMARY STATISTICS")
        print("=" * 100)
        
        # Risk analysis
        if 'risk_amount' in df.columns:
            avg_risk = df['risk_amount'].mean()
            total_risk = df['risk_amount'].sum()
            print(f"Average Risk per Trade: ${avg_risk:.2f}")
            print(f"Total Risk Taken: ${total_risk:.2f}")
        
        # R:R analysis
        if 'risk_reward_ratio' in df.columns:
            avg_rr = df['risk_reward_ratio'].mean()
            print(f"Average R:R Ratio: 1:{avg_rr:.2f}")
        
        # Slippage analysis for filled trades
        filled_trades = df[df['status'].isin(['filled', 'closed'])]
        if not filled_trades.empty and 'slippage' in filled_trades.columns:
            avg_slippage = filled_trades['slippage'].abs().mean()
            total_slippage_cost = filled_trades['slippage_cost'].sum() if 'slippage_cost' in filled_trades.columns else 0
            print(f"Average Slippage: ${avg_slippage:.2f}")
            print(f"Total Slippage Cost: ${total_slippage_cost:.2f}")
        
        # P&L analysis for closed trades
        closed_trades = df[df['status'] == 'closed']
        if not closed_trades.empty and 'realized_pnl' in closed_trades.columns:
            total_pnl = closed_trades['realized_pnl'].sum()
            avg_pnl = closed_trades['realized_pnl'].mean()
            winners = closed_trades[closed_trades['realized_pnl'] > 0]
            losers = closed_trades[closed_trades['realized_pnl'] <= 0]
            win_rate = len(winners) / len(closed_trades) * 100 if len(closed_trades) > 0 else 0
            
            print(f"\nClosed Trades: {len(closed_trades)}")
            print(f"Winners: {len(winners)}")
            print(f"Losers: {len(losers)}")
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"Total P&L: ${total_pnl:.2f}")
            print(f"Average P&L: ${avg_pnl:.2f}")
            
            if 'r_multiple' in closed_trades.columns:
                avg_r = closed_trades['r_multiple'].mean()
                max_r = closed_trades['r_multiple'].max()
                min_r = closed_trades['r_multiple'].min()
                print(f"Average R-Multiple: {avg_r:.2f}R")
                print(f"Best Trade: {max_r:.2f}R")
                print(f"Worst Trade: {min_r:.2f}R")
        
        print("=" * 100)
        
    except Exception as e:
        print(f"Error reading trade logs: {e}")

if __name__ == "__main__":
    view_trade_logs()