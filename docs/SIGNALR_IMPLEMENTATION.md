# TopStepX SignalR Real-time Data Implementation

## Overview

This implementation provides real-time market data and trading updates from TopStepX using SignalR WebSocket connections. This works for both practice and evaluation accounts, providing live quotes, trades, market depth, and order/position updates.

## Architecture

### Core Components

1. **TopStepXSignalRClient** (`src/api/topstep_signalr_client.py`)
   - Manages SignalR hub connections
   - Handles authentication with JWT tokens
   - Provides subscription methods for market data
   - Implements automatic reconnection

2. **TopStepXRealTimeDataManager** (`src/api/topstep_realtime_integration.py`)
   - Higher-level abstraction for bot integration
   - Manages data storage and caching
   - Provides analytical methods (order book imbalance, volume profile)
   - Implements callback system for data updates

3. **RealTimeGoldBot** (`src/bot_realtime.py`)
   - Example bot implementation with real-time data
   - Shows integration patterns
   - Implements order flow confirmation for signals

## SignalR Hubs

### Market Hub (`https://rtc.topstepx.com/hubs/market`)
Provides real-time market data:
- **Quote Updates**: Bid/ask/last prices with sizes
- **Trade Updates**: Individual trades with price, size, and side
- **Market Depth**: Order book with multiple levels
- **Market Status**: Trading session status

### User Hub (`https://rtc.topstepx.com/hubs/user`)
Provides account-specific updates:
- **Order Updates**: Order status changes, fills, rejections
- **Position Updates**: Position changes, P&L updates
- **Fill Updates**: Execution details
- **Account Updates**: Balance and margin changes

## Authentication

SignalR requires JWT token authentication:
```python
# JWT token is passed as query parameter
url = f"{hub_url}?access_token={jwt_token}"
```

The JWT token is obtained from the standard TopStepX API login.

## Contract IDs

TopStepX uses specific contract ID format:
- Format: `CON.F.US.{SYMBOL}.{MONTH}{YEAR}`
- Example: `CON.F.US.MGC.Q25` (Micro Gold July 2025)

## Usage Examples

### Basic Connection
```python
from src.api.topstep_signalr_client import TopStepXSignalRClient

# Create client with JWT token
client = TopStepXSignalRClient(jwt_token)

# Connect to hubs
await client.connect()

# Subscribe to quotes
await client.subscribe_to_quotes(["CON.F.US.MGC.Q25"])

# Register callback
def on_quote(quote):
    print(f"New quote: Bid={quote['bid']}, Ask={quote['ask']}")

client.on_quote(on_quote)
```

### Using the Data Manager
```python
from src.api.topstep_realtime_integration import TopStepXRealTimeDataManager

# Initialize manager
manager = TopStepXRealTimeDataManager()
await manager.initialize(jwt_token)

# Subscribe to contracts
await manager.subscribe_to_contracts(["CON.F.US.MGC.Q25"])

# Get real-time data
quote = manager.get_latest_quote("CON.F.US.MGC.Q25")
bid, ask = manager.get_bid_ask("CON.F.US.MGC.Q25")
imbalance = manager.get_order_book_imbalance("CON.F.US.MGC.Q25")
```

### Bot Integration
```python
# The RealTimeGoldBot shows full integration
bot = RealTimeGoldBot()
await bot.connect()  # Connects both REST API and SignalR
await bot.run()      # Uses real-time data for trading
```

## Data Flow

1. **Authentication**: Bot authenticates via REST API, gets JWT token
2. **SignalR Connection**: Uses JWT to connect to SignalR hubs
3. **Subscriptions**: Subscribes to required contract IDs
4. **Data Reception**: Receives real-time updates via callbacks
5. **Processing**: Bot processes data for trading decisions
6. **Order Execution**: Uses real-time quotes for better fills

## Key Features

### Order Book Imbalance
Calculates buy/sell pressure from order book:
- Range: -1 to +1
- Positive: More buyers (bullish)
- Negative: More sellers (bearish)

### Volume Profile
Tracks volume at each price level:
- Identifies high-volume nodes (support/resistance)
- Helps with entry/exit decisions

### Trade Momentum
Analyzes recent trade flow:
- Compares buy vs sell volume
- Indicates short-term direction

## Testing

### Test SignalR Connection
```bash
python scripts/test_signalr_connection.py
```

This will:
1. Authenticate and get JWT token
2. Connect to SignalR hubs
3. Subscribe to MGC data
4. Log received data for 30 seconds

### Test with Bot
```bash
python src/bot_realtime.py
```

Runs the enhanced bot with real-time data integration.

## Troubleshooting

### Connection Issues
- Ensure JWT token is valid (not expired)
- Check network connectivity
- Verify contract IDs are correct

### No Data Received
- Confirm subscriptions were successful
- Check if markets are open
- Verify contract is active/tradeable

### Data Quality
- Monitor `is_data_stale()` method
- Check `last_data_timestamp`
- Use diagnostics: `manager.get_diagnostics()`

## Benefits

1. **Real-time Execution**: Better fills with live quotes
2. **Order Flow Analysis**: See actual market activity
3. **Reduced Latency**: Instant updates vs polling
4. **Works with Practice**: Full functionality even in sim mode
5. **Professional Features**: Order book depth, trade tape

## Implementation Notes

- SignalR uses WebSocket transport with automatic reconnection
- Data is cached locally for fast access
- Callbacks are async-safe
- Graceful degradation to REST API if SignalR fails
- Memory-efficient with circular buffers for trade history

## Future Enhancements

1. **Delta Compression**: Reduce bandwidth with incremental updates
2. **Multi-Symbol Support**: Trade multiple instruments
3. **Advanced Analytics**: VWAP, market microstructure
4. **Recording/Replay**: Save data for backtesting
5. **Performance Metrics**: Latency monitoring