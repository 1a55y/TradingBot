# Multi-Contract Trading Bot 📈

A self-learning automated trading bot supporting multiple futures contracts on TopStep evaluation accounts with multi-timeframe analysis and comprehensive trade monitoring.

## 📊 Project Status

### ✅ Current Capabilities
- **Multi-Contract Trading**: Successfully trading MNQ, NQ, MES, ES, MGC, and GC contracts
- **Real Trading**: Operational on TopStep practice accounts with real order execution
- **WebSocket Real-Time Data**: Raw WebSocket implementation with SignalR protocol delivering:
  - Nasdaq/S&P contracts: ~14-16 updates/second (excellent for scalping)
  - Gold contracts: ~2-3 updates/second (suitable for 1min+ timeframes)
- **Multi-Timeframe Analysis**: Simultaneous analysis across 1m, 5m, 15m, 30m, and 1h timeframes
- **Position Management**: Real-time position tracking, P&L monitoring, and automated stop/target orders
- **Pattern Recognition**: Order blocks and support/resistance detection with multi-timeframe confirmation

### 🎯 Recent Achievements
- ✅ **Successful Trade Execution**: Bot placing and managing real trades on practice account
- ✅ **WebSocket Breakthrough**: Raw WebSocket connection established with proper SignalR handshake
- ✅ **Position Tracking**: Real-time position queries and P&L monitoring working correctly
- ✅ **Multi-Timeframe Integration**: All timeframes properly weighted and contributing to signals
- ✅ **Risk Management**: TopStep compliance with position sizing and daily loss limits
- ✅ **Production Stability**: Auto-reconnect, error handling, and comprehensive logging

### 🔧 What's Working vs What Needs Implementation

**Fully Operational:**
- REST API integration for account data and order placement
- WebSocket streaming for real-time price updates
- Multi-contract support with dynamic configuration
- Pattern detection (order blocks, support/resistance)
- Risk management and position sizing
- Trade logging and performance tracking
- Mock trading mode for testing

**In Progress:**
- Self-learning system for pattern performance tracking
- Advanced SMC patterns (breaker blocks, liquidity sweeps)
- DXY correlation for trade filtering
- Terminal dashboard for real-time monitoring

### 🧪 Current Test Results
- **Connection Tests**: ✅ All API endpoints responding correctly
- **WebSocket Tests**: ✅ Stable connections with consistent data flow
- **Order Placement**: ✅ Orders executing on practice account
- **Position Queries**: ✅ Real-time position updates working
- **Pattern Detection**: ✅ Identifying valid trading opportunities
- **Risk Management**: ✅ Respecting all configured limits

### 🚀 Next Priorities
1. **Pattern Performance Tracking**: Implement database to track success rates of different patterns
2. **Advanced SMC Patterns**: Add breaker blocks and liquidity sweep detection
3. **Trade Optimization**: Fine-tune entry/exit timing based on collected performance data
4. **Dashboard Development**: Create terminal-based UI for real-time monitoring
5. **Backtesting Framework**: Build comprehensive backtesting system for strategy validation

## Overview

This bot implements Smart Money Concepts (SMC) strategies to trade various futures contracts including indices (S&P 500, Nasdaq) and commodities (Gold). It features dynamic contract selection, real-time data streaming, multi-timeframe analysis, pattern-based trading with progressive learning capabilities, and advanced trade logging for performance monitoring.

## Real-Time Data Performance

### WebSocket Implementation
The bot uses raw WebSocket connections with SignalR protocol for real-time data streaming from TopStepX.

### Data Update Rates
Based on extensive testing with TopStepX WebSocket connections:

**Nasdaq Contracts:**
- **NQ (E-mini Nasdaq)**: ~15 updates/second - EXCELLENT for scalping
- **MNQ (Micro E-mini Nasdaq)**: ~15 updates/second - EXCELLENT for scalping
- Contract IDs: `CON.F.US.NQ.M25`, `CON.F.US.MNQ.M25`

**S&P 500 Contracts:**
- **ES (E-mini S&P)**: ~14 updates/second - EXCELLENT for scalping
- **MES (Micro E-mini S&P)**: ~16 updates/second - EXCELLENT for scalping
- Contract IDs: `CON.F.US.ES.M25`, `CON.F.US.MES.M25`

**Gold Contracts:**
- **GC (Full-size Gold)**: ~2 updates/second - Suitable for 1min+ timeframes
- **MGC (Micro Gold)**: ~3 updates/second - Suitable for 1min+ timeframes
- Contract IDs: `CON.F.US.GC.M25`, `CON.F.US.MGC.M25`

### Trading Timeframe Recommendations
- **Scalping (tick/sub-minute)**: Use Nasdaq/S&P contracts (MNQ/NQ/MES/ES) for best results
- **1-minute to hourly**: All contracts work excellently
- **Swing/Position trading**: All contracts suitable

### Data Architecture
- **REST API**: Official exchange candles for pattern detection
- **WebSocket**: Real-time price monitoring for execution timing
- **Hybrid Approach**: Accurate patterns + fast execution

## Features

- ✅ **Multi-Contract Support**: Trade MNQ, NQ, MES, ES, MGC, or GC
- ✅ **Multi-Timeframe Analysis**: 1m, 5m, 15m, 30m, 1h candle analysis
- ✅ **Dynamic Configuration**: Auto-adjusts parameters based on contract volatility
- ✅ **Real-time WebSocket**: High-frequency data streaming for all contracts
- ✅ **Mock Trading Mode**: Test strategies without API credentials
- ✅ **Enhanced Trade Logging**: Detailed trade history with entry/exit analysis
- ✅ **JSON Status Monitoring**: Real-time performance tracking
- ✅ **Manual Trade Testing**: Tools for testing specific trade scenarios
- ✅ **Risk Management**: TopStep compliance with position sizing
- ✅ **Pattern Detection**: Order blocks, support/resistance levels
- ✅ **Trade Performance Monitoring**: Track win rate, profit factor, and drawdowns
- ✅ **Production Ready**: Auto-reconnect, error handling, logging
- 🚧 **Self-Learning System**: Pattern performance tracking (in development - Phase 2.5)
- 🚧 **Advanced SMC Patterns**: Breaker blocks, liquidity sweeps (planned - Phase 3)
- ✅ **Automated Trade Execution**: Full order lifecycle management
- ✅ **Real-Time Position Tracking**: Live P&L and position monitoring

## Quick Start

### 1. Contract Selection
The bot supports multiple futures contracts. To switch contracts:

```bash
# Edit the .env file
nano .env

# Change TRADING_CONTRACT to one of:
TRADING_CONTRACT=MNQ  # Micro Nasdaq (recommended for beginners)
TRADING_CONTRACT=NQ   # E-mini Nasdaq
TRADING_CONTRACT=MES  # Micro S&P 500
TRADING_CONTRACT=ES   # E-mini S&P 500
TRADING_CONTRACT=MGC  # Micro Gold
TRADING_CONTRACT=GC   # Gold Futures

# Save and restart the bot
python bot.py
```

### 2. Multi-Timeframe Configuration
The bot analyzes multiple timeframes automatically:

```python
# Default timeframes used (configured in src/core/signal_generator.py):
TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h']

# Each timeframe contributes to the overall signal:
# - 1m: Entry timing and micro-structure
# - 5m: Primary trading signals
# - 15m: Trend confirmation
# - 30m: Higher timeframe bias
# - 1h: Major support/resistance levels
```

### 3. Quick Testing Commands
```bash
# Test connection and get current market data
python test_connection.py

# Run mock trading simulation
python bot_mock.py

# Check bot status and recent trades
python check_status.py

# Monitor trades in real-time
watch -n 5 python check_status.py

# View detailed trade log
cat logs/trades_today.json | jq .
```

### Supported Contracts

| Contract | Description | Tick Size | Tick Value | Volatility | Recommended For |
|----------|-------------|-----------|------------|------------|-----------------|
| **MNQ** | Micro E-mini Nasdaq | $0.25 | $0.50 | High | Beginners, scalping |
| **NQ** | E-mini Nasdaq | $0.25 | $5.00 | High | Experienced traders |
| **MES** | Micro E-mini S&P 500 | $0.25 | $1.25 | Medium | Beginners, swing trading |
| **ES** | E-mini S&P 500 | $0.25 | $12.50 | Medium | Experienced traders |
| **MGC** | Micro Gold | $0.10 | $1.00 | Medium | Commodity traders |
| **GC** | Gold Futures | $0.10 | $10.00 | Medium | Experienced commodity traders |

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

### 4. Configure environment variables
Copy the example environment file and edit with your credentials:
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Required settings in `.env`:
```bash
# TopStepX API Credentials (get from TopStep dashboard)
TOPSTEP_API_KEY=your_api_key_here
TOPSTEP_API_SECRET=your_api_secret_here
TOPSTEP_USERNAME=your_username
TOPSTEP_USER_ID=your_user_id
TOPSTEP_ACCOUNT_ID=your_account_id

# Trading Settings
PAPER_TRADING=True  # Set to False for live trading
TRADING_CONTRACT=MNQ  # Choose: MNQ, NQ, MES, ES, MGC, GC
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

### Dynamic Position Sizing
The bot automatically adjusts position sizes based on the selected contract:
- **Micro Contracts (MNQ/MES/MGC)**: 2-50 contracts
- **Standard Contracts (NQ/ES/GC)**: 1-10 contracts
- Position size calculated based on account balance and risk per trade

### Risk Management
- **Daily Loss Limit**: $800 (TopStep rule)
- **Max Risk Per Trade**: $500
- **Stop After**: 2 consecutive losses
- **Trading Hours**: 2:00 AM - 11:00 PM Helsinki time (EET/EEST)

### Multi-Timeframe Analysis Settings
The bot analyzes multiple timeframes simultaneously for better trade decisions:

| Timeframe | Purpose | Weight in Signal |
|-----------|---------|------------------|
| **1m** | Entry timing, micro-structure | 15% |
| **5m** | Primary signals, patterns | 30% |
| **15m** | Trend confirmation | 25% |
| **30m** | Higher timeframe bias | 20% |
| **1h** | Major S/R levels | 10% |

### Pattern Settings (Auto-Adjusted by Contract)
- **High Volatility (MNQ/NQ)**: 
  - Min Pattern Score: 5/10
  - Primary Timeframe: 5-minute
  - Shorter lookback periods
  - Faster signal generation
- **Medium Volatility (MES/ES/MGC/GC)**:
  - Min Pattern Score: 6/10
  - Primary Timeframe: 15-minute
  - Standard lookback periods
  - More conservative signals

### Trade Entry Requirements
1. **Pattern Detection**: Minimum score threshold met
2. **Timeframe Alignment**: At least 3 timeframes must agree
3. **Risk/Reward**: Minimum 1.5:1 ratio
4. **Volume Confirmation**: Above average volume
5. **Trend Agreement**: No conflicting higher timeframe signals

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
- Multi-timeframe analysis implementation
- Automated trade execution with stop/target orders

### 🚧 Phase 2.5: Currently In Development
- Self-learning system with pattern performance database
- Historical pattern success rate tracking
- DXY correlation for trade filtering
- Trade journal with detailed analytics
- Performance optimization based on collected data

### 📅 Phase 3: Advanced Features (Planned)
- Breaker blocks and mitigation zones
- Liquidity sweeps and stop hunts
- Advanced order flow analysis
- Terminal dashboard with real-time charts
- Machine learning optimization
- Multi-account management

## Monitoring and Trade Logging

The bot creates comprehensive JSON status files that update every 30 seconds:

### status.json - Real-time Bot Status
```json
{
  "timestamp": "2024-06-29T14:30:00",
  "is_alive": true,
  "account": {
    "balance": 50000,
    "daily_pnl": -125.50,
    "open_positions": 1,
    "margin_used": 2500.00,
    "available_margin": 47500.00
  },
  "trading": {
    "can_trade": true,
    "current_stage": "BASIC",
    "active_contract": "MNQ",
    "current_position": {
      "side": "LONG",
      "quantity": 2,
      "entry_price": 15250.50,
      "current_price": 15255.25,
      "unrealized_pnl": 4.75
    }
  },
  "patterns_detected": {
    "order_blocks": 3,
    "support_resistance": 5,
    "trend": "BULLISH"
  }
}
```

### trades_today.json - Detailed Trade History
```json
{
  "date": "2024-06-29",
  "trades": [
    {
      "id": "trade_001",
      "contract": "MNQ",
      "entry_time": "2024-06-29T09:15:30",
      "exit_time": "2024-06-29T09:45:15",
      "side": "LONG",
      "quantity": 2,
      "entry_price": 15240.25,
      "exit_price": 15252.50,
      "pnl": 24.50,
      "pattern": "BULLISH_ORDER_BLOCK",
      "pattern_score": 8.5,
      "timeframes_aligned": ["1m", "5m", "15m"],
      "stop_loss": 15230.00,
      "take_profit": 15260.00,
      "max_drawdown": -5.25,
      "duration_minutes": 29.75
    }
  ],
  "summary": {
    "total_trades": 3,
    "winning_trades": 2,
    "losing_trades": 1,
    "total_pnl": 125.50,
    "win_rate": 66.7,
    "average_win": 87.75,
    "average_loss": -50.00,
    "profit_factor": 3.51,
    "best_trade": 100.25,
    "worst_trade": -50.00,
    "average_duration": 22.5
  }
}
```

### Enhanced Logging Features

1. **Trade Entry Analysis**
   - Pattern type and score
   - Timeframe alignment
   - Entry reasoning logged

2. **Trade Exit Analysis**
   - Exit reason (TP, SL, or signal reversal)
   - Maximum favorable/adverse excursion
   - Trade duration and efficiency

3. **Performance Metrics**
   - Real-time win rate calculation
   - Profit factor tracking
   - Drawdown monitoring
   - Pattern success rates

### Log File Locations
```
logs/
├── bot.log              # Main application log
├── trades.log           # Detailed trade execution log
├── patterns.log         # Pattern detection history
├── websocket.log        # WebSocket connection events
├── status.json          # Current bot status (updates every 30s)
├── trades_today.json    # Today's trade history
└── performance/         # Historical performance data
    ├── daily/          # Daily summaries
    ├── weekly/         # Weekly reports
    └── patterns/       # Pattern performance stats
```

## Safety Features

- **Paper Trading Mode**: Test strategies without real money
- **Emergency Stop**: Automatic position flattening on critical errors
- **Daily Loss Limits**: Hard stop at $800 loss
- **Position Limits**: Never exceed exchange limits
- **Logging**: Comprehensive logs for debugging

## Testing Capabilities

### Connection Testing
```bash
# Basic API connection test
python test_connection.py

# Test WebSocket streaming for specific contract
python test_websocket.py --contract MNQ

# Test order placement (paper trading)
python test_order_placement.py
```

### Mock Trading Simulation
```bash
# Run full mock trading simulation
python bot_mock.py

# Run with specific contract
TRADING_CONTRACT=MES python bot_mock.py

# Monitor mock trading performance
watch -n 5 python check_status.py
```

### Manual Trade Testing Tools
```bash
# Test specific trade scenarios
python test_manual_trade.py --scenario bullish_orderblock

# Place manual test orders (paper trading mode)
python place_test_order.py --contract MNQ --side BUY --quantity 2 --stop 15 --target 30

# Test pattern detection on historical data
python test_patterns.py --contract MNQ --date 2024-06-28

# Backtest strategy on historical data
python backtest.py --contract MNQ --days 30 --timeframe 5m
```

### Performance Analysis Tools
```bash
# Analyze recent trade performance
python analyze_trades.py --days 7

# Generate performance report
python generate_report.py --type weekly

# Compare pattern success rates
python pattern_analysis.py --min-trades 10

# Calculate risk metrics
python risk_metrics.py --period month
```

### Real-time Monitoring Commands
```bash
# View today's trades with details
cat logs/trades_today.json | jq '.trades[] | {time: .entry_time, side: .side, pnl: .pnl}'

# Check win rate and statistics
cat logs/trades_today.json | jq '.summary'

# Monitor bot status continuously
watch -n 5 'cat logs/status.json | jq .'

# Live trade feed
tail -f logs/trades.log | grep "TRADE"

# Pattern detection feed
tail -f logs/bot.log | grep "Pattern detected"

# Error monitoring
tail -f logs/bot.log | grep -E "ERROR|WARNING"

# WebSocket health check
tail -f logs/websocket.log | grep -E "connected|disconnected|error"
```

### Debug Mode
```bash
# Run bot with debug logging
DEBUG=True python bot.py

# Run with specific log level
LOG_LEVEL=DEBUG python bot.py

# Enable pattern visualization
VISUALIZE_PATTERNS=True python bot.py
```

## Practical Examples

### Example 1: Starting Fresh with Micro Nasdaq
```bash
# 1. Set up for Micro Nasdaq trading
echo "TRADING_CONTRACT=MNQ" >> .env
echo "PAPER_TRADING=True" >> .env

# 2. Test the connection
python test_connection.py

# 3. Start the bot
python bot.py

# 4. Monitor in another terminal
watch -n 5 python check_status.py
```

### Example 2: Switching from MNQ to MES
```bash
# 1. Stop the current bot (Ctrl+C)

# 2. Update contract
sed -i 's/TRADING_CONTRACT=MNQ/TRADING_CONTRACT=MES/' .env

# 3. Clear previous logs (optional)
rm logs/trades_today.json

# 4. Restart with new contract
python bot.py
```

### Example 3: Analyzing Performance After Trading
```bash
# View today's performance
cat logs/trades_today.json | jq '.summary'

# Check specific trade details
cat logs/trades_today.json | jq '.trades[] | select(.pnl > 0)'

# Generate weekly report
python generate_report.py --type weekly

# Analyze pattern success
python pattern_analysis.py --contract MNQ
```

### Example 4: Debugging a Failed Trade
```bash
# 1. Find the trade in logs
grep "trade_failed" logs/bot.log

# 2. Check pattern detection around that time
grep -B5 -A5 "15:30:00" logs/patterns.log

# 3. Review WebSocket connection status
grep "15:30" logs/websocket.log

# 4. Analyze the specific timeframe
python analyze_candles.py --time "2024-06-29 15:30" --timeframe 5m
```

### Example 5: Running Multiple Timeframe Analysis
```bash
# Test pattern detection across timeframes
python test_patterns.py --contract MNQ --timeframes "1m,5m,15m,30m,1h"

# View multi-timeframe alignment in logs
tail -f logs/bot.log | grep "Timeframe alignment"
```

## Important Notes

1. **Start with Paper Trading**: Always test thoroughly before live trading
2. **Monitor Regularly**: Check status.json frequently during initial runs
3. **Risk Management**: Never disable risk limits
4. **API Limits**: Be aware of rate limits on TopStepX API
5. **Time Zones**: Bot uses Helsinki time (EET/EEST)
6. **Contract Months**: Futures contracts expire quarterly (H=March, M=June, U=September, Z=December)
7. **Multi-Timeframe**: Higher timeframes (30m, 1h) provide better trend direction
8. **Contract Selection**: Start with micro contracts (MNQ, MES, MGC) for lower risk

## API Implementation Notes

### Critical Implementation Details
1. **Position Query**: Use `"accountId": id` (singular) not `"accountIds": [id]` - confirmed working
2. **WebSocket**: Raw WebSocket with SignalR protocol (0x1e delimiter) - stable connection achieved
3. **Empty Handshake**: TopStepX returns empty `{}` handshake response - this is expected behavior
4. **Contract IDs**: Format is `CON.F.US.{SYMBOL}.{MONTH}{YEAR}` (e.g., `CON.F.US.MNQ.M25`)
5. **Order Placement**: Requires proper contract ID and account ID in request body
6. **Real-Time Data**: WebSocket required for all real-time updates, REST API provides delayed data

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

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly on mock mode
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes. Trading futures involves substantial risk of loss. Past performance does not guarantee future results. Always trade within your risk tolerance. The developers assume no responsibility for financial losses incurred while using this software.