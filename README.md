# Gold Futures Trading Bot 🥇

A self-learning automated trading bot for Gold Futures (MGC) on TopStep evaluation accounts.

## Overview

This bot implements Smart Money Concepts (SMC) strategies to trade Micro Gold Futures (MGC) contracts. It starts with basic order block detection and progressively learns from its trading results to improve performance over time.

## Real-Time Data Performance

### WebSocket Implementation
The bot uses raw WebSocket connections with SignalR protocol for real-time data streaming from TopStepX.

### Data Update Rates
Based on extensive testing with TopStepX WebSocket connections:

**S&P 500 Contracts:**
- **EP (E-mini S&P)**: 14.3 updates/second - EXCELLENT for scalping
- **MES (Micro E-mini)**: 16.3 updates/second - EXCELLENT for scalping
- Contract IDs: `CON.F.US.EP.U25`, `CON.F.US.MES.U25`

**Gold Contracts:**
- **GCE (Full-size Gold)**: 1.7 updates/second - Suitable for 1min+ timeframes
- **MGC (Micro Gold)**: 2.5 updates/second - Suitable for 1min+ timeframes
- Contract IDs: `CON.F.US.GCE.Q25`, `CON.F.US.MGC.Q25`

### Trading Timeframe Recommendations
- **Scalping (tick/sub-minute)**: Use S&P contracts (EP/MES) only
- **1-minute to hourly**: Both S&P and Gold work excellently
- **Swing/Position trading**: All contracts suitable

### Data Architecture
- **REST API**: Official exchange candles for pattern detection
- **WebSocket**: Real-time price monitoring for execution timing
- **Hybrid Approach**: Accurate patterns + fast execution

## Features

- ✅ Phase 1: Basic order block detection
- ✅ Mock trading mode for testing without API credentials
- ✅ JSON-based status monitoring
- ✅ Risk management with TopStep compliance
- ✅ Phase 2: Real-time WebSocket data streaming
- ✅ Position query and order placement via REST API
- ✅ Production WebSocket client with auto-reconnect
- 🚧 Self-learning system (in progress)
- 🚧 Advanced SMC patterns (coming in Phase 3)

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd T-BOT
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API credentials
Copy the `.env` file and add your TopStepX credentials:
```bash
# Edit .env file with your credentials
TOPSTEP_API_KEY=your_api_key_here
TOPSTEP_API_SECRET=your_api_secret_here
TOPSTEP_ACCOUNT_ID=your_account_id_here
```

## Running the Bot

### Mock Mode (No API Required)
Test the bot logic without real API connections:
```bash
python bot_mock.py
```

### Production Mode (Requires API Credentials)
```bash
python bot.py
```

### Check Bot Status
Monitor the bot's performance in real-time:
```bash
python check_status.py

# Or use command line tools:
cat logs/status.json | jq .
watch -n 5 python check_status.py
```

## File Structure

```
T-BOT/
├── bot.py                      # Main bot (production)
├── bot_mock.py                 # Mock bot for testing
├── config.py                   # Configuration settings
├── check_status.py             # Status monitoring tool
├── test_connection.py          # API connection tester
├── requirements.txt            # Python dependencies
├── .env                       # API credentials (not in git)
├── .gitignore                 # Git ignore rules
├── src/                       # Source code modules
│   ├── api/
│   │   ├── topstep_client.py          # REST API client
│   │   └── topstep_websocket_client.py # WebSocket client
│   ├── core/
│   │   ├── risk_manager.py            # Risk management
│   │   └── signal_generator.py        # Trading signals
│   ├── indicators/
│   │   ├── atr.py                     # ATR calculation
│   │   ├── order_blocks.py           # Order block detection
│   │   └── support_resistance.py      # S/R levels
│   ├── utils/
│   │   ├── logger_setup.py           # Logging configuration
│   │   └── time_utils.py             # Time utilities
│   └── config.py                      # Centralized config
└── logs/                      # Trading logs and status
    ├── status.json            # Current bot status
    └── trades_today.json      # Today's trades
```

## Trading Configuration

### Position Sizing
- **Default**: 5 MGC contracts (conservative start)
- **Minimum**: 2 MGC (after losses)
- **Maximum**: 50 MGC (exchange limit)

### Risk Management
- **Daily Loss Limit**: $800 (TopStep rule)
- **Max Risk Per Trade**: $500
- **Stop After**: 2 consecutive losses
- **Trading Hours**: 4:45 PM - 10:30 PM Helsinki time

### Pattern Settings
- **Minimum Pattern Score**: 7/10 (high quality only)
- **Primary Timeframe**: 15-minute charts
- **Order Block Criteria**: 
  - Large candle (1.5x average body)
  - Strong move away
  - Volume confirmation

## Development Phases

### ✅ Phase 1: Foundation (Complete)
- Basic API connection
- Order block detection
- Risk management
- JSON monitoring

### ✅ Phase 2: Core Features (Complete)
- Split code into modules
- Real-time WebSocket data streaming
- Production-ready API client
- Position query and order placement

### 🚧 Phase 2.5: In Progress
- Self-learning system
- Pattern performance tracking
- DXY correlation for trade filtering

### 📅 Phase 3: Advanced Features
- Breaker blocks
- Liquidity sweeps
- Multi-timeframe analysis
- Terminal dashboard

## Monitoring

The bot creates JSON status files that update every 30 seconds:

### status.json
```json
{
  "timestamp": "2024-06-29T14:30:00",
  "is_alive": true,
  "account": {
    "balance": 50000,
    "daily_pnl": -125.50,
    "open_positions": 1
  },
  "trading": {
    "can_trade": true,
    "current_stage": "BASIC"
  }
}
```

### trades_today.json
```json
{
  "date": "2024-06-29",
  "trades": [...],
  "summary": {
    "total": 3,
    "pnl": 250.00,
    "win_rate": 66.7
  }
}
```

## Safety Features

- **Paper Trading Mode**: Test strategies without real money
- **Emergency Stop**: Automatic position flattening on critical errors
- **Daily Loss Limits**: Hard stop at $800 loss
- **Position Limits**: Never exceed exchange limits
- **Logging**: Comprehensive logs for debugging

## Testing

### Run connection test:
```bash
python test_connection.py
```

### Run mock trading:
```bash
python bot_mock.py
# Check status in another terminal:
python check_status.py
```

## Important Notes

1. **Start with Paper Trading**: Always test thoroughly before live trading
2. **Monitor Regularly**: Check status.json frequently during initial runs
3. **Risk Management**: Never disable risk limits
4. **API Limits**: Be aware of rate limits on TopStepX API
5. **Time Zones**: Bot uses Helsinki time (EET/EEST)

## API Implementation Notes

### Critical Fixes Applied
1. **Position Query**: Changed from `"accountIds": [id]` to `"accountId": id` (singular)
2. **WebSocket**: Implemented raw WebSocket with SignalR protocol (0x1e delimiter)
3. **Empty Handshake**: TopStepX returns empty `{}` handshake response - this is normal
4. **Contract IDs**: Use correct IDs (e.g., `CON.F.US.EP.U25` not `CON.F.US.ES.U25` for S&P)

### REST API Settings
- **Practice Account**: Uses `live: false` (returns 15-min delayed data)
- **Live/Evaluation Accounts**: Uses `live: true` for real-time data
- **WebSocket**: Required for real-time data streaming regardless of account type

## Troubleshooting

### Bot won't start
- Check API credentials in .env
- Verify Python version (3.8+)
- Check logs/bot.log for errors

### No trades executing
- Verify trading hours
- Check pattern score threshold
- Review daily loss limits

### Connection issues
- Test with bot_mock.py first
- Check API endpoint URLs
- Verify network connectivity

## Support

For issues or questions:
1. Check logs/bot.log for detailed error messages
2. Run test_connection.py to verify setup
3. Review the Plans/MainPlan folder for detailed documentation

## Disclaimer

This bot is for educational purposes. Trading futures involves substantial risk of loss. Past performance does not guarantee future results. Always trade within your risk tolerance.