# Blue2.0 Testing Guide

This guide provides comprehensive instructions for testing the Blue2.0 trading system, including manual trade verification, automated testing, trade log analysis, and risk calculations.

## Table of Contents
1. [Manual Trade Testing](#manual-trade-testing)
2. [Automated Trade Execution Testing](#automated-trade-execution-testing)
3. [Trade Log Analysis](#trade-log-analysis)
4. [Force Trading for Testing](#force-trading-for-testing)
5. [Understanding Trade Logs](#understanding-trade-logs)
6. [Risk Calculations and Position Sizing Verification](#risk-calculations-and-position-sizing-verification)

---

## Manual Trade Testing

The `scripts/test_manual_trade.py` script allows you to test trade mechanics without waiting for patterns to form in the market.

### Interactive Mode

Run the script without arguments to enter interactive mode:

```bash
python scripts/test_manual_trade.py
```

**Example Interactive Session:**
```
🔧 MANUAL TRADE TESTER FOR MNQ
================================

Select trade direction:
1. LONG
2. SHORT
3. Exit

Enter choice (1-3): 1

Enter price for LONG trade (or 'current' for current price): 21000

Enter stop loss distance in points (default: 10): 15

============================================================
MANUAL TRADE TEST - LONG
============================================================

📊 TRADE SETUP:
   Direction: LONG
   Entry Price: $21000.00
   Position Size: 3 contracts

🎯 LEVELS:
   Stop Loss: $20985.00 (15.0 points)
   Take Profit: $21030.00 (30.0 points)
   Risk/Reward: 1:2

💰 RISK CALCULATIONS:
   Risk per trade: 1.0% of account
   Risk amount: $22.50
   Potential profit: $45.00
   Point value: $0.50

🔄 TRAILING STOP:
   Activation: $21015.00
   Distance: 10.0 points

💼 ACCOUNT:
   Balance: $50,000.00
   Max daily loss: $1000.00
   Risk % of balance: 0.05%

============================================================

✅ VERIFICATION:
   Stop loss points: 15.00 ✓
   Risk calculation: 3 × 15.00 × $0.50 = $22.50 ✓
   Risk/Reward ratio: 1:2.0 ✓

📋 MNQ CONTRACT SPECS:
   Symbol: MNQ
   Point value: $0.50
   Tick size: 0.25
   Min tick movement: $0.12

Save this trade setup to file? (y/n): y
✅ Trade setup saved to: trade_test_LONG_20250102_143022.json
```

### Command Line Mode

For quick testing, provide parameters via command line:

```bash
# Test LONG trade at 21000 with 10 point stop
python scripts/test_manual_trade.py LONG 21000 10

# Test SHORT trade at 21500 with 20 point stop
python scripts/test_manual_trade.py SHORT 21500 20
```

**Expected Output:**
```
============================================================
MANUAL TRADE TEST - LONG
============================================================

📊 TRADE SETUP:
   Direction: LONG
   Entry Price: $21000.00
   Position Size: 5 contracts

🎯 LEVELS:
   Stop Loss: $20990.00 (10.0 points)
   Take Profit: $21020.00 (20.0 points)
   Risk/Reward: 1:2

[... rest of output ...]
```

---

## Automated Trade Execution Testing

The `tests/test_trade_execution.py` provides comprehensive unit tests for trade execution mechanics.

### Running All Tests

```bash
# Run all trade execution tests
python -m pytest tests/test_trade_execution.py -v

# Run with coverage report
python -m pytest tests/test_trade_execution.py --cov=src --cov-report=html
```

### Running Specific Test Categories

```bash
# Test stop loss placement only
python -m pytest tests/test_trade_execution.py::TestTradeExecution::test_stop_loss_placement_bullish -v

# Test position sizing
python -m pytest tests/test_trade_execution.py::TestTradeExecution::test_position_sizing_based_on_risk -v

# Test order validation
python -m pytest tests/test_trade_execution.py::TestOrderValidation -v

# Test risk calculations
python -m pytest tests/test_trade_execution.py::TestRiskCalculations -v
```

**Expected Test Output:**
```
============================= test session starts ==============================
collected 20 items

tests/test_trade_execution.py::TestTradeExecution::test_stop_loss_placement_bullish PASSED [ 5%]
tests/test_trade_execution.py::TestTradeExecution::test_stop_loss_placement_bearish PASSED [10%]
tests/test_trade_execution.py::TestTradeExecution::test_take_profit_calculations PASSED [15%]
tests/test_trade_execution.py::TestTradeExecution::test_position_sizing_based_on_risk PASSED [20%]
tests/test_trade_execution.py::TestTradeExecution::test_risk_per_trade_calculations PASSED [25%]
...
============================== 20 passed in 0.45s ==============================
```

### Understanding Test Results

The test suite verifies:
- **Stop Loss Placement**: Ensures stops are placed correctly for LONG/SHORT trades
- **Take Profit Calculations**: Verifies 1:1, 1:2, and 2.5:1 R:R ratios
- **Position Sizing**: Tests dynamic sizing based on risk and consecutive losses
- **Order Validation**: Ensures invalid orders are rejected
- **Risk Limits**: Verifies daily loss and consecutive loss limits

---

## Trade Log Analysis

Use `scripts/analysis/view_trade_logs.py` to analyze historical trades.

### Basic Usage

```bash
python scripts/analysis/view_trade_logs.py
```

**Expected Output (with trades):**
```
====================================================================================================
TRADE EXECUTION LOG ANALYSIS
====================================================================================================
Total Trades: 5
----------------------------------------------------------------------------------------------------

Trade #1
--------------------------------------------------
Order ID: ORD-20250102-143022
Timestamp: 2025-01-02T14:30:22.123Z
Side: BUY
Quantity: 3
Entry Price: $21000.00
Stop Loss: $20985.00
Take Profit: $21030.00
Risk Amount: $22.50
R:R Ratio: 1:2.00
Status: filled
Fill Price: $21000.50
Slippage: $0.50
Slippage Cost: $1.50

Trade #2
--------------------------------------------------
Order ID: ORD-20250102-145512
Timestamp: 2025-01-02T14:55:12.456Z
Side: SELL
Quantity: 2
Entry Price: $21500.00
Stop Loss: $21520.00
Take Profit: $21460.00
Risk Amount: $20.00
R:R Ratio: 1:2.00
Status: closed
Exit Price: $21460.00
P&L: $40.00
R-Multiple: 2.00R

====================================================================================================
SUMMARY STATISTICS
====================================================================================================
Average Risk per Trade: $21.25
Total Risk Taken: $106.25
Average R:R Ratio: 1:2.00
Average Slippage: $0.35
Total Slippage Cost: $1.75

Closed Trades: 2
Winners: 1
Losers: 1
Win Rate: 50.0%
Total P&L: $15.00
Average P&L: $7.50
Average R-Multiple: 0.50R
Best Trade: 2.00R
Worst Trade: -1.00R
====================================================================================================
```

**Expected Output (no trades):**
```
No trade logs found yet.
```

---

## Force Trading for Testing

To test trade execution without waiting for patterns, you have several options:

### 1. Manual Trade Tester (Recommended)

Use the manual trade tester as shown above to simulate trades at any price point.

### 2. Mock Bot Testing

Run the mock bot which simulates trades based on synthetic patterns:

```bash
# Run mock bot with forced trade signals
python src/bot_mock.py --force-trade --interval 60
```

### 3. Test Trade Logging

Force a trade execution log entry for testing:

```bash
python scripts/test_trade_logging.py
```

This creates a sample trade in the logs for testing the viewing script.

### 4. Modify Pattern Detection Temporarily

For testing in live mode, temporarily adjust pattern detection thresholds:

```python
# In config/settings.py, temporarily reduce thresholds
MIN_TOUCHES = 2  # Instead of 3
PATTERN_LOOKBACK = 50  # Instead of 100
```

**⚠️ WARNING**: Remember to restore original values after testing!

---

## Understanding Trade Logs

The `logs/trade_executions.json` file contains detailed trade information:

### Log Structure

```json
[
  {
    "order_id": "ORD-20250102-143022",
    "entry_timestamp": "2025-01-02T14:30:22.123Z",
    "side": "BUY",
    "quantity": 3,
    "entry_price": 21000.00,
    "stop_price": 20985.00,
    "target_price": 21030.00,
    "risk_amount": 22.50,
    "risk_reward_ratio": 2.0,
    "status": "filled",
    "fill_price": 21000.50,
    "slippage": 0.50,
    "slippage_cost": 1.50,
    "exit_timestamp": "2025-01-02T15:45:33.789Z",
    "exit_price": 21030.00,
    "realized_pnl": 89.50,
    "r_multiple": 2.0
  }
]
```

### Key Fields to Monitor

1. **Order Execution**
   - `order_id`: Unique identifier
   - `status`: "pending", "filled", "closed", "cancelled"
   - `slippage`: Difference between expected and actual fill

2. **Risk Management**
   - `risk_amount`: Dollar risk for the trade
   - `risk_reward_ratio`: Target R:R ratio
   - `quantity`: Position size

3. **Performance**
   - `realized_pnl`: Actual profit/loss
   - `r_multiple`: Profit/loss expressed in R units
   - `slippage_cost`: Cost of slippage in dollars

---

## Risk Calculations and Position Sizing Verification

### Manual Verification

Use the manual trade tester to verify calculations:

```bash
python scripts/test_manual_trade.py LONG 21000 10
```

Look for the verification section:
```
✅ VERIFICATION:
   Stop loss points: 10.00 ✓
   Risk calculation: 5 × 10.00 × $0.50 = $25.00 ✓
   Risk/Reward ratio: 1:2.0 ✓
```

### Automated Testing

Run specific risk calculation tests:

```bash
# Test risk calculations
python -m pytest tests/test_trade_execution.py::TestRiskCalculations -v

# Test position sizing
python -m pytest tests/test_trade_execution.py::TestTradeExecution::test_position_sizing_based_on_risk -v
```

### Risk Calculation Formulas

1. **Risk per Trade**
   ```
   Risk = Position Size × Stop Distance (points) × Point Value
   Example: 5 contracts × 10 points × $0.50 = $25
   ```

2. **Position Size Calculation**
   ```
   Position Size = Risk Amount / (Stop Distance × Point Value)
   Example: $500 / (10 × $0.50) = 100 contracts (capped at max position)
   ```

3. **Risk as % of Account**
   ```
   Risk % = (Risk Amount / Account Balance) × 100
   Example: ($25 / $50,000) × 100 = 0.05%
   ```

### Verifying Dynamic Position Sizing

The system reduces position size after consecutive losses:

```python
# Normal conditions
Default: 10 contracts

# After 1 loss
Reduced: 5 contracts (50% reduction)

# After 2 losses
Minimum: 2 contracts (minimum allowed)

# After 3 losses
Trading halted (max consecutive losses reached)
```

Test this behavior:
```bash
python -m pytest tests/test_trade_execution.py::TestTradeExecution::test_position_sizing_based_on_risk -v
```

---

## Common Testing Scenarios

### 1. Pre-Trade Verification

Before going live, run:
```bash
# Test trade mechanics
python scripts/test_manual_trade.py

# Run all unit tests
python -m pytest tests/test_trade_execution.py -v

# Verify risk calculations at your typical stop distances
python scripts/test_manual_trade.py LONG 21000 10
python scripts/test_manual_trade.py LONG 21000 15
python scripts/test_manual_trade.py LONG 21000 20
```

### 2. Post-Trade Analysis

After trades execute:
```bash
# View recent trades
python scripts/analysis/view_trade_logs.py

# Check for slippage issues
grep "slippage" logs/trade_executions.json

# Verify risk was within limits
grep "risk_amount" logs/trade_executions.json
```

### 3. System Health Check

```bash
# Run all tests
python -m pytest tests/ -v

# Check configuration
python -c "from config.settings import *; print(f'Risk per trade: {RISK_PER_TRADE*100}%')"
python -c "from config.settings import *; print(f'Max position: {MAX_POSITION_SIZE} contracts')"
```

---

## Troubleshooting

### No Trades Appearing in Logs

1. Check if the bot is running: `ps aux | grep bot`
2. Verify WebSocket connection: Check logs for connection status
3. Ensure pattern detection is working: Lower thresholds temporarily

### Risk Calculations Don't Match

1. Verify point value: MNQ = $0.50 per point
2. Check tick size: MNQ = 0.25 point minimum movement
3. Ensure position size caps are applied

### Tests Failing

1. Update dependencies: `pip install -r requirements.txt`
2. Check configuration hasn't changed
3. Ensure test data is valid

---

## Best Practices

1. **Always test before trading**: Run manual tests with your planned parameters
2. **Monitor logs regularly**: Check for unusual slippage or failed orders
3. **Verify risk limits**: Ensure daily loss limits are enforced
4. **Test edge cases**: Try extreme values to ensure system handles them
5. **Document test results**: Save test outputs for future reference

Remember: Testing is crucial for safe and profitable trading. Never skip testing steps, especially after system updates or configuration changes.