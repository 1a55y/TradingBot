#!/usr/bin/env python3
"""
Simple Manual Trade Testing Script for T-BOT
Tests trade mechanics without waiting for patterns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.contracts import CONTRACTS
import asyncio

def test_trade(direction='LONG', entry_price=None, stop_points=15):
    """Test a manual trade setup"""
    
    # Get current contract
    contract = CONTRACTS[Config.SYMBOL]
    
    print("=" * 60)
    print(f"MANUAL TRADE TEST - {direction}")
    print("=" * 60)
    
    # Use provided entry or default
    if entry_price is None:
        entry_price = 22850.0  # Default test price for MNQ
    
    # Calculate levels
    if direction == 'LONG':
        stop_price = entry_price - (stop_points * contract.tick_size * 4)  # 4 ticks per point for MNQ
        target_price = entry_price + (stop_points * 2 * contract.tick_size * 4)  # 2:1 R:R
    else:  # SHORT
        stop_price = entry_price + (stop_points * contract.tick_size * 4)
        target_price = entry_price - (stop_points * 2 * contract.tick_size * 4)
    
    # Calculate risk
    position_size = Config.DEFAULT_POSITION_MNQ
    risk_per_contract = abs(entry_price - stop_price) * contract.tick_value / contract.tick_size
    total_risk = risk_per_contract * position_size
    potential_profit = abs(target_price - entry_price) * contract.tick_value / contract.tick_size * position_size
    
    print(f"\n📊 TRADE SETUP:")
    print(f"   Contract: {Config.SYMBOL}")
    print(f"   Direction: {direction}")
    print(f"   Entry Price: ${entry_price:,.2f}")
    print(f"   Position Size: {position_size} contracts")
    
    print(f"\n🎯 LEVELS:")
    print(f"   Stop Loss: ${stop_price:,.2f} ({stop_points} points)")
    print(f"   Take Profit: ${target_price:,.2f} ({stop_points * 2} points)")
    print(f"   Risk/Reward: 1:2")
    
    print(f"\n💰 RISK CALCULATIONS:")
    print(f"   Risk per contract: ${risk_per_contract:.2f}")
    print(f"   Total risk: ${total_risk:.2f}")
    print(f"   Potential profit: ${potential_profit:.2f}")
    
    print(f"\n📋 CONTRACT SPECS:")
    print(f"   Tick size: {contract.tick_size}")
    print(f"   Tick value: ${contract.tick_value}")
    print(f"   Points per tick: {1/4}")  # MNQ has 4 ticks per point
    
    print(f"\n✅ VERIFICATION:")
    print(f"   Stop distance: {abs(entry_price - stop_price):.2f} points")
    print(f"   Target distance: {abs(target_price - entry_price):.2f} points")
    print(f"   Risk check: {position_size} × ${risk_per_contract:.2f} = ${total_risk:.2f}")
    
    if total_risk > Config.MAX_RISK_PER_TRADE:
        print(f"\n⚠️  WARNING: Risk ${total_risk:.2f} exceeds limit ${Config.MAX_RISK_PER_TRADE}")
    else:
        print(f"\n✅ Risk within limits (${total_risk:.2f} < ${Config.MAX_RISK_PER_TRADE})")
    
    print("\n" + "=" * 60)
    
    return {
        'direction': direction,
        'entry': entry_price,
        'stop': stop_price,
        'target': target_price,
        'risk': total_risk,
        'reward': potential_profit
    }

def main():
    """Run manual trade test"""
    
    if len(sys.argv) > 1:
        direction = sys.argv[1].upper()
        if direction not in ['LONG', 'SHORT']:
            print("Usage: python test_manual_trade_simple.py [LONG|SHORT] [entry_price] [stop_points]")
            sys.exit(1)
    else:
        # Interactive mode
        print("Test a trade setup")
        print("-" * 30)
        direction = input("Direction (LONG/SHORT): ").upper()
        if direction not in ['LONG', 'SHORT']:
            direction = 'LONG'
    
    # Optional parameters
    entry_price = float(sys.argv[2]) if len(sys.argv) > 2 else None
    stop_points = float(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    # Run test
    result = test_trade(direction, entry_price, stop_points)
    
    # Save result only in interactive mode
    if len(sys.argv) == 1:
        save = input("\nSave this trade setup? (y/n): ")
        if save.lower() == 'y':
            filename = f"trade_setup_{direction}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Saved to {filename}")

if __name__ == "__main__":
    from datetime import datetime
    import json
    main()