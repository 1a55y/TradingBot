# Partial Profit Taking System

## Overview

The T-BOT trading system now includes an advanced partial profit taking mechanism that automatically splits positions into multiple targets, allowing traders to secure profits while maintaining exposure for larger moves.

## Features

### 1. **Position Splitting**
- Automatically divides each position into 3 parts with configurable percentages
- Default split: 50% / 40% / 10%
- Each part has its own profit target at different R:R ratios

### 2. **Target Management**
- **Target 1 (TP1)**: 1:1 Risk/Reward - Takes 50% of position
- **Target 2 (TP2)**: 1:2 Risk/Reward - Takes 40% of position  
- **Target 3 (Runner)**: 1:2.5 Risk/Reward - Keeps 10% for larger moves

### 3. **Stop Loss Adjustment**
- After TP1 is hit, stop automatically moves to breakeven + small buffer
- Protects profits while allowing remaining position to run
- Buffer of 2 ticks to cover costs and ensure profitability

### 4. **Order Types**
- Places individual limit orders for each target
- Orders are linked to the main position for tracking
- Unfilled targets are automatically cancelled when position closes

## Configuration

### Enable/Disable
```python
# In src/config.py
ENABLE_PARTIAL_PROFITS = True  # Set to False to use single target
```

### Customize Percentages
```python
PARTIAL_PROFIT_PERCENTAGES = {
    1: 0.50,  # 50% at first target
    2: 0.40,  # 40% at second target  
    3: 0.10   # 10% runner
}
```

### Customize Target Ratios
```python
PARTIAL_PROFIT_RATIOS = {
    1: 1.0,   # 1:1 R:R for first target
    2: 2.0,   # 1:2 R:R for second target
    3: 2.5    # 1:2.5 R:R for runner
}
```

### Stop Adjustment Settings
```python
ADJUST_STOP_AFTER_TP1 = True  # Move stop to breakeven after TP1
BREAKEVEN_BUFFER_TICKS = 2    # Buffer in ticks when moving to breakeven
```

## How It Works

### 1. **Position Entry**
When a trade signal is triggered:
1. Main market order is placed for full position size
2. System calculates 3 target levels based on risk distance
3. Places 3 separate limit orders at each target level

### 2. **Target Fills**
As price moves in favor:
1. Each target fills independently at its limit price
2. Position size reduces with each fill
3. P&L is tracked for each partial exit

### 3. **Stop Management**
After first target (TP1) is hit:
1. Stop loss automatically adjusts to breakeven + buffer
2. Remaining position (50%) is now risk-free
3. Allows trader to capture larger moves without risk

### 4. **Position Closure**
When position fully closes:
1. Any remaining unfilled targets are cancelled
2. Total P&L is calculated including all partials
3. Performance metrics updated

## Example Trade

**BUY Signal at $2650.00 with 10 contracts:**

1. **Entry**: Buy 10 @ $2650.00
2. **Stop Loss**: $2645.00 (5 points risk)
3. **Targets Placed**:
   - TP1: Sell 5 @ $2655.00 (1:1 R:R)
   - TP2: Sell 4 @ $2660.00 (1:2 R:R)
   - TP3: Sell 1 @ $2662.50 (1:2.5 R:R)

**Scenario 1 - All Targets Hit:**
- TP1 fills: +$25 profit (5 contracts × $5)
- Stop moves to $2650.50 (breakeven + buffer)
- TP2 fills: +$40 profit (4 contracts × $10)
- TP3 fills: +$12.50 profit (1 contract × $12.50)
- **Total P&L: +$77.50**

**Scenario 2 - Only TP1 Hit, Then Stop:**
- TP1 fills: +$25 profit (5 contracts × $5)
- Stop moves to $2650.50
- Price reverses, stop hit: +$2.50 profit (5 contracts × $0.50)
- **Total P&L: +$27.50** (vs -$50 without partials)

## Benefits

1. **Risk Reduction**: Secure profits early while maintaining upside
2. **Psychology**: Easier to hold runners when partial profits taken
3. **Flexibility**: Capture both small and large moves
4. **Protection**: Breakeven stop ensures winning trades stay winners

## Monitoring

The system provides real-time tracking of:
- Active managed positions
- Filled vs unfilled targets
- Running P&L for each position
- Stop adjustment status

Check `logs/status.json` for partial profit metrics:
```json
"partial_profits": {
    "enabled": true,
    "active_positions": 2,
    "targets": {
        "1": 0.5,
        "2": 0.4,
        "3": 0.1
    }
}
```

## Best Practices

1. **Position Sizing**: Account for partial exits when sizing positions
2. **Risk Management**: Total risk remains the same, but reward potential increases
3. **Market Conditions**: Works best in trending markets where runners can capture moves
4. **Monitoring**: Track fill rates to optimize target distances

## Troubleshooting

### Targets Not Filling
- Check if target prices are realistic for the timeframe
- Verify limit orders are being placed correctly
- Consider market volatility when setting ratios

### Stop Not Adjusting
- Ensure ADJUST_STOP_AFTER_TP1 is enabled
- Verify TP1 has actually filled
- Check logs for any error messages

### Order Rejections
- Verify account has sufficient margin for multiple orders
- Check position limits aren't exceeded
- Ensure contract specifications are correct