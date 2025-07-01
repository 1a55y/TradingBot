# Phase 2: Live API Integration

## Overview
Phase 2 implements the connection to the real TopStepX API, enabling live trading capabilities while maintaining all safety features from Phase 1.

## What's New

### 1. TopStepX API Client (`src/api/topstep_client.py`)
- Full API client implementation with WebSocket support
- Authentication using credentials from `.env`
- Market data streaming
- Order placement and management
- Position tracking
- Automatic reconnection logic

### 2. Live Trading Bot (`src/bot_live.py`)
- Extends `BaseGoldBot` with real API functionality
- Concurrent market data and trading event processing
- Real-time position monitoring
- Caching for efficient data access
- Paper trading mode support

### 3. Updated Main Entry Point
- New `--live` flag to enable API connection
- Default to mock mode for safety
- Paper trading controlled by `.env` setting

## Usage

### Test API Connection
```bash
python test_api_connection.py
```

### Run in Live Mode (Paper Trading)
```bash
# Ensure PAPER_TRADING=True in .env
python main.py --live
```

### Run in Live Mode (Real Trading)
```bash
# Set PAPER_TRADING=False in .env (USE WITH CAUTION!)
python main.py --live
```

### Run in Mock Mode (Default)
```bash
python main.py
# or
python main.py --mock
```

## API Endpoints Used

### HTTP Endpoints
- `GET /account/info` - Account information
- `GET /positions` - Current positions
- `POST /orders` - Place orders
- `DELETE /orders/{id}` - Cancel orders
- `GET /market/quote/{symbol}` - Current market data
- `GET /market/candles` - Historical data

### WebSocket Streams
- `wss://api.topstepx.com/hubs/market` - Real-time market data
- `wss://api.topstepx.com/hubs/user` - Trading events (fills, rejects, etc.)

## Safety Features Maintained

1. **Paper Trading Mode** - Test strategies without real money
2. **Daily Loss Limits** - $800 hard stop
3. **Risk Per Trade Limits** - Max $500 per trade
4. **Position Size Limits** - 2-50 MGC contracts
5. **Emergency Position Flattening** - On critical errors or limit breach
6. **Comprehensive Logging** - All actions logged

## Architecture

```
main.py
  └─> LiveGoldBot (bot_live.py)
       ├─> BaseGoldBot (base_bot.py) - Core trading logic
       └─> TopStepXClient (topstep_client.py) - API communication
            ├─> HTTP Session (aiohttp)
            └─> WebSocket Connections (aiohttp)
```

## Next Steps (Remaining Phase 2 Tasks)

1. **DXY Correlation** - Add Dollar Index monitoring
2. **Self-Learning System** - Track pattern performance
3. **Enhanced Position Monitoring** - Real-time P&L dashboard
4. **Breaker Blocks** - Add second SMC pattern

## Testing Checklist

- [ ] API connection successful
- [ ] Market data streaming working
- [ ] Order placement (paper mode)
- [ ] Position tracking
- [ ] WebSocket reconnection
- [ ] Error handling
- [ ] Daily loss limit enforcement
- [ ] JSON monitoring updates

## Notes

- Always test in paper trading mode first
- Monitor logs carefully during initial live runs
- WebSocket connections auto-reconnect on failure
- All Phase 1 safety features remain active
- Default mode is mock for safety