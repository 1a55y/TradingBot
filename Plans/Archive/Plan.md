# TopStepX Gold Futures Trading Bot 🥇 (Helsinki Edition)

A disciplined, professional-grade trading bot designed specifically for TopStep Combine evaluation accounts. This bot implements a Smart Money Concepts (SMC) strategy on Gold Futures (GC/MGC), focusing on institutional order flow, liquidity sweeps, and market structure analysis. Configured to trade exclusively during the New York session from Helsinki timezone (4:45 PM - 10:30 PM local time).

## 🚀 Features

### Core Trading Features
- **Advanced SMC Engine**: Multi-timeframe confluence scoring with ML-powered order block classification
- **Market Regime Adaptation**: Auto-detects trending/ranging/news conditions and adjusts strategy
- **Institutional Analysis**: Volume profile integration, delta/footprint analysis for real order flow
- **Smart Position Management**: Automated scaling, dynamic stops, 4H order flow runner management
- **Predictive Liquidity Mapping**: Identifies stop-loss clusters and institutional accumulation zones

### Risk & Performance Management
- **TopStep-Specific Optimizations**: Trailing drawdown protection, consistency scoring, profit curve optimizer
- **Psychological Capital Protection**: Confidence scoring, automated breaks, success momentum mode
- **Advanced Analytics Dashboard**: Real-time pattern success rates, heat maps, win rate by pattern type
- **AI-Enhanced Entry Optimization**: Personalized ML model trained on your winning trades

### Infrastructure & Reliability
- **Bulletproof Infrastructure**: Redundant data feeds, order execution failover, auto-recovery
- **Enterprise Backtesting**: Monte Carlo simulations, walk-forward optimization, stress testing
- **24/7 Session Management**: Automatic token refresh and reconnection
- **Emergency Systems**: Single-keystroke flatten, trade reconciliation, real-time alerts

## 📋 Requirements

- Python 3.8 or higher
- TopStepX account with API access ($14.50/month with code "topstep")
- Windows, Mac, or Linux operating system
- Stable internet connection (no VPS allowed per TopStep rules)

## 📊 Gold Futures Contract Specifications

### Contract Details
- **MGC (Micro Gold)**: 
  - Contract size: 10 troy ounces
  - Tick value: $1.00 per tick
  - Minimum tick: 0.10 ($0.10 price movement)
  
- **GC (Full-size Gold)**:
  - Contract size: 100 troy ounces  
  - Tick value: $10.00 per tick
  - Minimum tick: 0.10 ($0.10 price movement)

### Key Trading Facts
- MGC is exactly 1/10th the size of GC
- Perfect for precise position sizing within $500 risk limit
- 16 MGC = 1.6 GC in terms of dollar risk

## 🛠️ Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd tradingisfun
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your credentials**
   Edit `.env` file with your TopStepX API credentials:
   ```
   TOPSTEPX_API_KEY=your_api_key_here
   TOPSTEPX_USERNAME=your_username_here
   ```

5. **Validate setup** (Recommended)
   ```bash
   python test_setup.py
   ```

## 🔧 Configuration

The bot features multiple configuration profiles optimized for different scenarios:

### Account Settings
- **Account Size**: $50,000 (TopStep Combine)
- **Daily Loss Limit**: $800 (80% of TopStep's $1,000 limit)
- **Profit Target**: $3,000
- **Trailing Drawdown Alert**: 75% threshold warning

### Configuration Profiles
```python
# Conservative Mode (Days 1-10)
PROFILE_CONSERVATIVE = {
    "max_daily_trades": 2,
    "position_size": 5,
    "min_confluence_score": 8/10,
    "use_ml_optimization": False
}

# Standard Mode (Days 11-20)
PROFILE_STANDARD = {
    "max_daily_trades": 4,
    "position_size": "dynamic",
    "min_confluence_score": 7/10,
    "use_ml_optimization": True
}

# Graduation Mode (Days 21+)
PROFILE_GRADUATION = {
    "max_daily_trades": 2,
    "position_size": "reduced",
    "min_confluence_score": 9/10,
    "protect_profits": True
}
```

### Trading Parameters
- **Max Risk Per Trade**: $500 (maximum allowed)
- **Position Sizing**: Dynamic (8-16 MGC based on stop distance)
- **Max Position**: 5 GC or 50 MGC contracts (exchange/broker limit)
- **Max Daily Trades**: 4 (quality over quantity)  
- **Trading Hours**: 4:45 PM - 10:30 PM Helsinki Time (NY Session)
- **Dynamic Stops**: 30-50 ticks based on ATR and market regime
- **Smart Targets**: 1:1 to 1:2.5 risk/reward ratios with three-tier exits

### Advanced Position Management
- **Scaling Logic**: Add to winners at key SMC levels
- **Partial Exit Points**: Automated based on order flow
- **Runner Management**: Uses 4H institutional levels
- **Correlation Adjustment**: Monitors DXY/Gold inverse correlation
- **Volatility Scaling**: Position size adapts to market conditions

### Position Sizing Constraints
- **Standard Size**: 8-16 MGC (based on 30-50 tick stops)
- **GC Alternative**: 1-2 GC for wider stops (10-20 tick minimum)
- **Absolute Maximum**: 5 GC or 50 MGC (exchange/broker limit)
- **Risk Limit**: $500 per trade (may further reduce position size)
- **Sizing Logic**: Use smaller of (1) Risk-based calculation or (2) Position limits

## 🚦 Getting Started

1. **Configure Timezone**
   Set your timezone to Helsinki (Europe/Helsinki) in `config.py` to ensure proper NY session trading hours.

2. **Test Authentication**
   ```bash
   python auth.py
   ```
   This will verify your API credentials and display your account info.

3. **Paper Trade First** (Recommended)
   ```bash
   python main.py --paper
   ```
   Or set `ENABLE_PAPER_TRADING = True` in `config.py`

4. **Run the Bot**
   
   **Option 1: Interactive Launcher** (Recommended)
   ```bash
   python launcher.py
   ```
   
   **Option 2: Standard Polling Mode**
   ```bash
   python main.py
   ```
   
   **Option 3: Real-time WebSocket Mode**
   ```bash
   python main_realtime.py
   ```
   
   **Option 4: Convenience Scripts**
   - Windows: `run_bot.bat`
   - Unix/Mac: `./run_bot.sh`

## 📊 Strategy Overview

The bot uses Smart Money Concepts (SMC) strategy on Gold Futures (GC/MGC) that:
1. Operates exclusively during NY session (4:45 PM - 10:30 PM Helsinki time)
2. Identifies institutional order blocks and breaker blocks
3. Trades fair value gaps (FVGs) with market structure confirmation
4. Targets liquidity sweeps above/below key highs and lows
5. Enters at premium/discount zones with 30-50 tick stops
6. Takes partial profits at 50 ticks (60% of position)
7. Trails remaining position using order flow imbalances

### What is SMC?
Smart Money Concepts focuses on tracking institutional trading patterns:
- **Order Blocks**: Areas where institutions placed large orders
- **Fair Value Gaps**: Price inefficiencies that need to be filled
- **Liquidity Sweeps**: Stop-loss hunting by institutions
- **Market Structure**: Higher highs/lows and lower highs/lows analysis
- **Premium/Discount Zones**: Optimal entry areas based on price equilibrium

### Advanced SMC Implementation
Our bot goes beyond basic SMC with:
- **Multi-Timeframe Confluence**: 15m, 1H, and 4H alignment scoring
- **Volume Profile Integration**: Validates order blocks with actual volume
- **Delta Analysis**: Tracks buy/sell imbalances for true institutional activity
- **ML Classification**: AI ranks order block strength based on historical performance
- **Automated Zone Refinement**: Dynamically adjusts zones based on price reactions

## 🛡️ Safety Features

### Core Protection
- **Automatic shutdown** after 3 consecutive losses
- **Daily loss limit** enforcement ($800)
- **NY Session Only** (4:45 PM - 10:30 PM Helsinki time)
- **Position size limits** based on performance
- **Emergency kill switch** (set `EMERGENCY_STOP = True`)

### TopStep-Specific Safeguards
- **Trailing Drawdown Monitor**: Real-time tracking with alerts at 75% threshold
- **Consistency Optimizer**: Ensures profit distribution meets TopStep requirements
- **End-of-Day Protection**: Auto-flattens positions 15 minutes before session end
- **Graduation Mode**: Conservative settings when approaching profit target

### Advanced Risk Management
- **Correlation Protection**: Monitors DXY/Gold inverse relationship
- **Volatility Adjustment**: Dynamic stop placement based on ATR
- **News Event Detection**: Pauses during FOMC, NFP, and gold-specific events
- **Recovery Protocol**: Special mode after drawdown to rebuild safely

## 📁 Project Structure

```
T-BOT/
├── auth.py           # Authentication and session management
├── config.py         # Configuration settings (dataclasses)
├── setup.py          # Initial setup script
├── test_setup.py     # Comprehensive setup validation
├── main.py           # Main bot entry point (polling mode)
├── main_realtime.py  # Real-time WebSocket entry point
├── launcher.py       # Interactive launcher
├── signals.py        # Advanced SMC engine with ML classification
├── market_regime.py  # Market condition detection (trending/ranging/news)
├── liquidity_map.py  # Predictive liquidity and stop-loss cluster mapping
├── orders.py         # Smart order management with scaling logic
├── positions.py      # Position tracking with runner management
├── market_data.py    # Multi-source data with redundancy
├── websocket.py      # Real-time streaming with auto-reconnect
├── volume_profile.py # Volume analysis and delta calculations
├── ml_optimizer.py   # AI entry optimization and pattern learning
├── risk_manager.py   # Advanced risk and psychology management
├── utils.py          # Core utilities and safety checks
├── backtest.py       # Monte Carlo and walk-forward testing
├── analytics.py      # Real-time performance analytics
├── dashboard.py      # Advanced metrics and heat maps
├── check_files.py    # File integrity checks
├── .env              # Your credentials (DO NOT COMMIT)
├── requirements.txt  # Python dependencies
├── logs/             # Trading and system logs
├── data/
│   ├── trades/       # Trade history
│   └── historical/   # Historical market data
└── backtest/
    └── results/      # Backtesting results
```

## ⚠️ Important Warnings

1. **NO VPS/VPN**: TopStep requires trading from your personal device
2. **API Trades Final**: Trades made via API cannot be reversed by TopStep
3. **Your Responsibility**: This bot is a tool; you're responsible for all trades
4. **Start Small**: Begin with paper trading or minimum size
5. **Monitor Regularly**: Don't leave the bot completely unattended

## 🎯 "Perfect 10" Features

### Market Intelligence
- **Multi-Timeframe Confluence Engine**: Scores setups across 15m, 1H, 4H timeframes
- **Predictive Liquidity Mapping**: Identifies stop clusters before price arrival
- **Market Regime Detection**: Automatically adapts strategy to market conditions
- **Volume Profile Integration**: Validates setups with real institutional activity

### Execution Excellence
- **Smart Position Sizing**: Dynamic adjustment based on win rate and market volatility
- **Automated Scaling**: Adds to winners at predetermined SMC levels
- **Intelligent Exit Management**: Partial profits optimized by order flow
- **Runner Optimization**: Uses 4H institutional levels for maximum gains

### Performance Enhancement
- **AI Entry Optimization**: ML model learns from your winning patterns
- **Psychological Capital Protection**: Monitors confidence and enforces breaks
- **TopStep Graduation Path**: Optimizes journey from evaluation to funding
- **Real-time Analytics**: Heat maps, pattern success rates, and performance tracking

### Infrastructure & Reliability
- **Redundant Data Feeds**: Primary and backup sources with auto-failover
- **Enterprise Backtesting**: Monte Carlo, walk-forward, and stress testing
- **Bulletproof Recovery**: Automatic reconnection and position reconciliation
- **Emergency Controls**: Single-keystroke flatten and kill switch

## 🧪 Testing & Validation

### Advanced Testing Suite

#### Monte Carlo Backtesting
```bash
# Run 1000 simulations with different market conditions
python backtest.py --mode monte-carlo --simulations 1000

# Walk-forward optimization
python backtest.py --mode walk-forward --window 30 --step 5

# Stress test against Black Swan events
python backtest.py --mode stress-test --scenario "flash-crash"
```

#### ML Model Training
```bash
# Train personalized entry model on your trades
python ml_optimizer.py --train --data "trades/*.json"

# Validate model performance
python ml_optimizer.py --validate --out-of-sample
```

#### Real-time Analytics
```bash
# Launch advanced dashboard with heat maps
python dashboard.py --advanced

# Export performance report
python analytics.py --export pdf --period "last-30-days"
```

#### System Validation
```bash
# Comprehensive system check
python check_files.py --deep-scan

# Test failover systems
python test_failover.py --simulate-disconnection

# Validate TopStep compliance
python topstep_validator.py --account $50k
```

## 🏗️ Architecture Overview

The bot follows an advanced modular architecture optimized for institutional-grade performance:

### Core Trading Engine
- **Trading Core**: `main.py` (polling) and `main_realtime.py` (WebSocket) with intelligent orchestration
- **Signal Generation**: `signals.py` implements advanced SMC with ML-powered classification
- **Market Regime**: `market_regime.py` auto-detects and adapts to market conditions
- **Liquidity Mapping**: `liquidity_map.py` predicts institutional zones before price arrival

### Smart Execution Layer
- **Order Management**: `orders.py` with automated scaling and partial exit logic
- **Position Tracking**: `positions.py` includes runner management using 4H order flow
- **Volume Analysis**: `volume_profile.py` integrates delta and footprint for real institutional activity

### Intelligence & Optimization
- **ML Optimizer**: `ml_optimizer.py` learns from your trades and improves entry timing
- **Analytics Engine**: `analytics.py` provides real-time pattern success rates and heat maps
- **Advanced Backtesting**: `backtest.py` with Monte Carlo simulations and stress testing

### Risk & Infrastructure
- **Risk Manager**: `risk_manager.py` handles psychology, correlation, and TopStep-specific rules
- **Bulletproof Data**: `market_data.py` with redundant feeds and automatic failover
- **Real-time Streaming**: `websocket.py` with enterprise-grade reconnection logic
- **Configuration**: `config.py` with environment-specific optimization profiles

## 📞 Support

- TopStep Support: For account issues
- ProjectX Support: For API billing issues  
- Discord #api-trading: For community help

## 📈 Expected Performance

### Realistic Performance Targets
- **Win Rate**: 45-55% (Professional trading range)
- **Average Winner**: $600-800 (12 MGC x 50 ticks x $1.00, 1:1.5 avg R:R)
- **Average Loser**: $450-500 (staying within max risk limit)
- **Risk/Reward Ratio**: 1:1 to 1:2.5 (dynamic based on setup)
- **Daily Target**: $250-500 (0.5-1% of account)
- **Time to Funded**: 20-30 trading days (with higher profit per trade)

### Performance Evolution
- **Month 1**: 40-45% win rate, $800-1,200/month (learning phase)
- **Month 2**: 45-50% win rate, $1,200-1,800/month (optimization)
- **Month 3+**: 50-55% win rate, $1,800-2,400/month (mature system)
- **Best Case**: 55-60% win rate, $2,400-3,000/month (exceptional conditions)

### Key Success Factors
- **Consistency**: More important than win rate
- **Risk Management**: Keeping losses small
- **Market Selection**: Trading only A+ setups
- **Position Sizing**: Conservative approach
- **Psychological Discipline**: Following the system

### TopStep Graduation Optimizer
The bot includes special modes for different funding stages:
- **Days 1-10**: Conservative mode, building consistency
- **Days 11-20**: Momentum mode, optimizing profit curve
- **Days 21+**: Graduation mode, protecting gains

## 🚨 Risk Disclosure

Trading futures involves substantial risk. Past performance is not indicative of future results. This bot is for educational purposes and should be thoroughly tested before live trading. Always trade with capital you can afford to lose.

---

**Remember**: The goal isn't to get rich quick - it's to prove consistent, disciplined trading to earn TopStep funding. Trade like a professional, not a gambler.

Good luck! 🍀