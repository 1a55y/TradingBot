# Protective Orders Implementation

## Overview
The bot now implements proper stop loss and take profit order placement using separate orders after market order fills, since TopStep's API doesn't reliably support bracket orders on market orders.

## Implementation Details

### 1. Market Order Changes
- Market orders are now placed WITHOUT stop/limit prices attached
- The order data structure no longer includes `stopPrice` or `limitPrice` for market orders
- This ensures reliable fills without rejection

### 2. New Method: `place_protective_orders()`
Located in `bot_live.py`, this method:
- Places separate stop loss and take profit orders after market order fills
- Uses proper order types:
  - Stop loss: Stop market order
  - Take profit: Limit order
- Tracks protective orders in `self.protective_orders` dictionary
- Maps position ID to stop and target order IDs for management

### 3. Order Flow
1. **Market Order Placed** → No stop/limit attached
2. **Fill Event Received** → `_handle_fill()` called
3. **Protective Orders Placed** → Stop and limit orders submitted separately
4. **Order Tracking** → Protective orders linked to position

### 4. Protective Order Management
- When stop loss fills → Target order is automatically cancelled
- When take profit fills → Stop loss order is automatically cancelled
- Handled by `_handle_protective_order_fill()` method

### 5. Key Features
- **Order Relationships**: Uses custom tags to track which protective orders belong to which position
- **Automatic Cleanup**: One-cancels-other (OCO) behavior implemented manually
- **Proper Sides**: Correctly handles buy/sell sides for closing positions
- **Error Handling**: Cancels stop if target placement fails

## Testing
- `test_protective_orders.py`: Unit tests for protective order placement
- `test_full_protective_workflow.py`: Integration test showing complete workflow
- Mock API client updated to support order cancellation tracking

## Configuration
- Temporarily disabled `ENABLE_PARTIAL_PROFITS` to focus on basic protective orders
- Can be re-enabled once protective orders are stable

## Benefits
1. **Reliability**: Avoids issues with bracket orders on market orders
2. **Flexibility**: Can modify stop/target after position entry
3. **Control**: Full visibility into individual order states
4. **Compatibility**: Works with TopStep's order management system

## Future Enhancements
1. Re-enable partial profits with protective orders
2. Add trailing stop functionality
3. Implement breakeven stops
4. Add order modification capabilities