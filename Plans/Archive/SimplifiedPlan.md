# TopStep Gold Futures Trading Bot - Practical Plan 🥇

A professional yet achievable trading bot for passing TopStep Combine evaluations. This bot implements a robust Smart Money Concepts (SMC) strategy on Gold Futures (MGC/GC), with proper risk management, performance tracking, and systematic improvements based on real trading data.

## 🎯 Core Philosophy
**Professional. Data-Driven. Scalable.**

Build a solid foundation, measure everything, improve systematically.

## 📋 What This Bot Actually Does

### Phase 1: Core Infrastructure (Week 1)
- TopStepX API integration with robust error handling
- WebSocket real-time data streaming
- Order execution with automatic retry logic
- Position tracking and P&L monitoring
- Comprehensive logging system
- Emergency shutdown capabilities
- Basic dashboard for monitoring

### Phase 2: SMC Strategy Engine (Week 2-3)
- Order block detection with volume validation
- Fair value gap identification with filters
- Market structure analysis (HH/HL/LH/LL)
- Simple market regime detection (trending/ranging/volatile)
- Entry optimization at premium/discount zones
- Dynamic stop placement based on structure
- Multi-timeframe confluence (15m primary, 1H filter)
- Session-based trading logic
- **Volume profile analysis for key levels**
- **Economic calendar integration**
- **News event filtering**

### Phase 3: Advanced Risk & Position Management (Week 4)
- Dynamic position sizing based on:
  - Account equity
  - Recent performance
  - Market volatility (ATR-based)
  - **Upcoming news events**
- Partial profit system (60% at TP1, 30% at TP2, 10% runner)
- Breakeven management after TP1
- Trailing stop for runners
- Correlation-based risk adjustment
- Performance analytics and reporting
- **Pre-news position reduction protocols**

### Phase 4: Optimization & Scaling (Month 2)
- Statistical analysis of trade performance
- Pattern success rate tracking
- Time-of-day performance analysis
- Automated parameter optimization
- A/B testing framework for strategy improvements
- Advanced backtesting with walk-forward analysis
- Scaling protocols based on performance metrics

## 🛠️ Technical Requirements

- Python 3.8+
- TopStepX API access ($14.50/month)
- Stable internet connection
- Local machine (no VPS per TopStep rules)

## 📁 Organized File Structure

```
topstep-bot/
├── core/
│   ├── config.py          # Configuration management
│   ├── auth.py            # TopStepX authentication
│   ├── websocket.py       # Real-time data streaming
│   ├── logger.py          # Advanced logging system
│   └── database.py        # Trade data storage
├── market/
│   ├── data.py            # Market data handler
│   ├── structure.py       # Market structure analysis
│   ├── indicators.py      # Technical indicators
│   ├── regime.py          # Market regime detection
│   ├── volume_profile.py  # Volume profile analysis
│   ├── calendar.py        # Economic calendar integration
│   └── news.py            # News event detection
├── strategy/
│   ├── signals.py         # SMC signal generation
│   ├── orderblocks.py     # Order block detection
│   ├── fvg.py            # Fair value gap logic
│   └── confluence.py      # Multi-timeframe analysis
├── execution/
│   ├── orders.py          # Order management
│   ├── positions.py       # Position tracking
│   └── risk.py           # Risk management
├── analysis/
│   ├── performance.py     # Performance metrics
│   ├── statistics.py      # Trade statistics
│   ├── optimizer.py       # Parameter optimization
│   └── reports.py         # Report generation
├── backtest/
│   ├── engine.py          # Backtesting engine
│   ├── data_loader.py     # Historical data handling
│   └── validator.py       # Strategy validation
├── dashboard/
│   ├── web_server.py      # Flask dashboard
│   ├── templates/         # HTML templates
│   └── static/           # CSS/JS files
├── main.py               # Main entry point
├── requirements.txt      # Dependencies
├── .env                  # Credentials
└── data/
    ├── logs/            # System logs
    ├── trades/          # Trade history
    └── reports/         # Performance reports
```

## 🔧 Configuration

```python
# Initial Conservative Settings
ACCOUNT_SIZE = 50000
DAILY_LOSS_LIMIT = 800
MAX_RISK_PER_TRADE = 500  # Maximum $500 risk per trade
POSITION_SIZE = "dynamic"  # Based on stop distance and max risk
MAX_POSITION_GC = 5  # Maximum 5 GC contracts
MAX_POSITION_MGC = 50  # Maximum 50 MGC contracts (equivalent to 5 GC)
STOP_LOSS_RANGE = (30, 50)  # 30-50 ticks based on setup
RISK_REWARD_MIN = 1.0  # 1:1 minimum
RISK_REWARD_MAX = 2.5  # 1:2.5 maximum
MAX_DAILY_TRADES = 3
MAX_CONSECUTIVE_LOSSES = 2

# Gold Futures Contract Specifications
MGC_TICK_VALUE = 1.00  # $1 per tick
GC_TICK_VALUE = 10.00  # $10 per tick
PREFERRED_CONTRACT = "MGC"  # Better for position sizing precision

# Position Sizing Logic: 
# Use smaller of: (1) Risk-based calc or (2) Position limits
# Example: 10-tick stop = max 50 MGC (risk-based) vs 50 MGC (limit) = 50 MGC
# Example: 40-tick stop = max 12 MGC (risk-based) vs 50 MGC (limit) = 12 MGC

# Trading Hours (Helsinki Time)
SESSION_START = "16:45"  # 4:45 PM
SESSION_END = "22:30"    # 10:30 PM

# SMC Settings for Gold Futures
LOOKBACK_CANDLES = 50
MIN_ORDER_BLOCK_TOUCHES = 2
FVG_MIN_SIZE_TICKS = 15  # Minimum 15-tick gap
# Note: MGC = $0.10/tick, GC = $10/tick

# Market Regime Settings
ATR_PERIOD = 14
TREND_STRENGTH_THRESHOLD = 0.7  # ADX > 25
VOLATILITY_THRESHOLD = 1.5  # ATR ratio vs 20-period average
REGIME_LOOKBACK = 100  # Candles for regime analysis

# News & Economic Events Settings
NEWS_PROVIDERS = ["forexfactory", "investing.com"]
HIGH_IMPACT_BUFFER = 30  # Minutes before/after high impact news
MEDIUM_IMPACT_BUFFER = 15  # Minutes before/after medium impact
REDUCE_POSITION_BEFORE_NEWS = True
NEWS_POSITION_SCALE = 0.5  # Trade 50% size near news

# Volume Profile Settings
VOLUME_PROFILE_PERIOD = 20  # Days for profile calculation
POC_DEVIATION_THRESHOLD = 10  # Ticks from Point of Control
VALUE_AREA_PERCENTAGE = 70  # Standard value area calculation
VOLUME_NODE_MIN_SIZE = 1000  # Minimum contracts for significant level
```

## 🚦 Detailed Implementation Plan

### Week 1: Bulletproof Infrastructure
**Monday-Tuesday: Core Systems**
- Set up project structure and virtual environment
- Implement TopStepX authentication with token management
- Create WebSocket connection for real-time data
- Build order execution system with retry logic
- Set up comprehensive logging framework

**Wednesday-Thursday: Data & Monitoring**
- Implement market data handler with caching
- Create position tracking system
- Build account monitoring (balance, P&L, drawdown)
- Add emergency shutdown mechanisms
- Create basic CLI dashboard

**Friday: Testing & Integration**
- Integration testing of all components
- Paper trading connection test
- Error handling verification
- Documentation of setup process

### Week 2-3: SMC Strategy Implementation
**Week 2: Pattern Detection**
- Implement market structure analysis (swing highs/lows)
- Build simple market regime detection:
  - Trending: Clear directional movement (ADX > 25)
  - Ranging: Sideways price action (ADX < 20)
  - Volatile: High ATR relative to average
- Build order block detection with volume validation
- Create FVG identification with filtering
- Add premium/discount zone calculation
- Implement 15-minute timeframe analysis
- **Set up economic calendar API integration**
- **Build basic volume profile calculator**

**Week 3: Signal Generation & Confluence**
- Add 1-hour timeframe structure filter
- Build confluence scoring system
- Implement entry signal logic
- Create trade setup validation
- Add session time filtering
- **Integrate news event filtering**
- **Add volume profile confirmation to signals**
- **Implement pre-news position protocols**

### Week 4: Risk & Position Management
**Monday-Tuesday: Risk Systems**
- Implement dynamic position sizing
- Add volatility-based stop calculation
- Create daily loss limit enforcement
- Build consecutive loss protection
- Add correlation monitoring

**Wednesday-Thursday: Advanced Exits**
- Implement three-tier profit taking
- Add breakeven management
- Create trailing stop for runners
- Build partial close functionality
- Test all exit scenarios

**Friday: Performance Analytics**
- Create trade logging database
- Build performance metrics calculator
- Implement basic reporting
- Add trade analysis tools

### Month 2: Optimization & Scaling
**Week 5-6: Data Analysis**
- Build comprehensive backtesting framework
- Implement walk-forward analysis
- Create performance visualization
- Add pattern success tracking
- Build parameter optimization tools

**Week 7-8: Production Readiness**
- Create web-based dashboard
- Add real-time performance monitoring
- Implement automated reporting
- Build A/B testing framework
- Prepare scaling protocols

## 📊 Realistic Expectations

### Performance Targets
- **Win Rate**: 45-50% (this is normal and profitable)
- **Risk/Reward**: 1:1 to 1:2.5 (dynamic based on setup quality)
- **Daily Goal**: $250-500 (0.5-1% of account per day)
- **Monthly Goal**: Pass evaluation in 30-45 days
- **Expected Monthly Profit**: $1,000-2,400 (with proper risk management)

### What Success Looks Like
- Consistent small wins
- Respecting stop losses
- No revenge trading
- Steady equity curve
- Meeting TopStep requirements

## 🎯 Simple Market Regime Detection

The bot identifies three market conditions and adapts accordingly:

### 1. Trending Market (ADX > 25)
- **Strategy**: Trade with the trend direction
- **Stops**: Tighter stops (30-40 ticks)
- **Targets**: Extended targets (1:2 to 1:2.5 ratio)
- **Position Size**: 12-16 MGC (max $500 risk, limited by 50 MGC max)
- **Entry**: Focus on pullbacks to order blocks

### 2. Ranging Market (ADX < 20)
- **Strategy**: Trade from range extremes
- **Stops**: Standard stops (40-50 ticks)
- **Targets**: Conservative targets (1:1 to 1:1.5 ratio)
- **Position Size**: 10-12 MGC (moderate size, limited by 50 MGC max)
- **Entry**: Focus on liquidity sweeps

### 3. Volatile Market (ATR > 1.5x average)
- **Strategy**: Reduce trading frequency
- **Stops**: Maximum stops (50 ticks)
- **Targets**: Quick profits (1:1 ratio only)
- **Position Size**: 8-10 MGC (minimum size, well under 50 MGC limit)
- **Entry**: Only A+ setups with confluence

### Implementation Details
```python
def detect_market_regime(self):
    # Simple and effective regime detection
    adx = calculate_adx(period=14)
    current_atr = calculate_atr(period=14)
    avg_atr = sma(current_atr, period=20)
    
    if adx > 25:
        return "TRENDING"
    elif adx < 20:
        return "RANGING"
    elif current_atr > avg_atr * 1.5:
        return "VOLATILE"
    else:
        return "NORMAL"
```

## 📰 News Event Handling & Economic Calendar

The bot monitors economic events and adjusts trading behavior to avoid volatility spikes and whipsaws.

### Economic Calendar Integration
- **Data Sources**: ForexFactory API and Investing.com scraper
- **Event Categories**:
  - **High Impact**: NFP, FOMC, CPI, GDP (No trading ±30 mins)
  - **Medium Impact**: Retail Sales, PMI (Reduced size ±15 mins)
  - **Low Impact**: Regular data (Normal trading)
- **Gold-Specific Events**: 
  - US Dollar Index movements
  - Treasury yields
  - Fed speeches
  - Geopolitical events

### News Trading Rules
```python
def check_news_filter(self):
    upcoming_events = self.calendar.get_events_next_hour()
    
    for event in upcoming_events:
        if event.impact == "HIGH":
            if event.time_until < 30:  # 30 minutes
                return "NO_TRADE"
        elif event.impact == "MEDIUM":
            if event.time_until < 15:  # 15 minutes
                return "REDUCED_SIZE"
    
    return "NORMAL_TRADE"
```

### Pre-News Position Management
1. **30 Minutes Before High Impact**: 
   - Close all positions
   - Cancel pending orders
   - Set "NEWS_LOCKOUT" flag

2. **15 Minutes Before Medium Impact**:
   - Reduce position size by 50%
   - Tighten stops to breakeven
   - No new entries allowed

3. **Post-News Protocol**:
   - Wait 15-30 minutes for volatility to settle
   - Check for new market structure
   - Resume trading with reduced size initially

## 📊 Volume Profile Analysis

Volume profile provides crucial insights into where institutions are positioned, helping identify strong support/resistance levels.

### Key Components
1. **Point of Control (POC)**: Highest volume price level
2. **Value Area**: 70% of volume (customizable)
3. **High Volume Nodes (HVN)**: Strong support/resistance
4. **Low Volume Nodes (LVN)**: Price tends to move quickly through

### Implementation
```python
class VolumeProfile:
    def __init__(self, period_days=20):
        self.period = period_days
        self.value_area_pct = 0.70
        
    def calculate_profile(self, price_data, volume_data):
        # Create price bins (10-tick intervals for Gold)
        price_bins = np.arange(
            price_data.min(), 
            price_data.max(), 
            10  # 10-tick bins
        )
        
        # Calculate volume at each price level
        volume_profile = {}
        for i, price in enumerate(price_data):
            bin_price = round(price / 10) * 10
            volume_profile[bin_price] = volume_profile.get(bin_price, 0) + volume_data[i]
        
        # Find Point of Control
        poc = max(volume_profile, key=volume_profile.get)
        
        # Calculate Value Area
        sorted_levels = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
        total_volume = sum(volume_profile.values())
        value_area_volume = 0
        value_area_prices = []
        
        for price, volume in sorted_levels:
            value_area_volume += volume
            value_area_prices.append(price)
            if value_area_volume >= total_volume * self.value_area_pct:
                break
        
        return {
            'poc': poc,
            'value_area_high': max(value_area_prices),
            'value_area_low': min(value_area_prices),
            'profile': volume_profile
        }
```

### Trading Integration
1. **Entry Confirmation**: 
   - Prefer entries near HVN levels (institutional interest)
   - Avoid entries in LVN zones (no support)
   - POC acts as a magnet price

2. **Stop Placement**:
   - Place stops beyond HVN levels
   - Never place stops in LVN (likely to be hit)

3. **Target Selection**:
   - Target next HVN level
   - Or opposite side of value area
   - POC as ultimate target in range-bound markets

### Combined Strategy Example
```python
def generate_trade_signal(self):
    # Check news filter first
    news_status = self.check_news_filter()
    if news_status == "NO_TRADE":
        return None
    
    # Get volume profile levels
    vp = self.volume_profile.calculate_profile(
        self.price_data[-20:], 
        self.volume_data[-20:]
    )
    
    # Check if price is near a key level
    current_price = self.get_current_price()
    distance_to_poc = abs(current_price - vp['poc'])
    
    # Combine with SMC signals
    if self.has_order_block_signal():
        # Confirm with volume profile
        if self.is_near_hvn_level(current_price, vp):
            signal_strength = "STRONG"
        else:
            signal_strength = "WEAK"
        
        # Adjust for news
        if news_status == "REDUCED_SIZE":
            position_size = self.base_size * 0.5
        else:
            position_size = self.base_size
            
        return {
            'direction': 'BUY',
            'strength': signal_strength,
            'size': position_size,
            'stop': self.calculate_stop_beyond_hvn(vp),
            'target': self.find_next_hvn_target(vp)
        }
```

## 💡 Key Features That Make This Worth Building

### Smart Entry System
- **Volume-Validated Order Blocks**: Not just price levels, but areas with actual institutional activity
- **Filtered FVGs**: Removes noise by requiring minimum size and confluence
- **Premium/Discount Zones**: Enters at optimal prices, not chasing
- **Multi-Timeframe Confirmation**: 15m signals filtered by 1H structure
- **Market Regime Adaptation**: Adjusts strategy parameters based on market conditions

### Professional Risk Management
- **Dynamic Position Sizing**: Adjusts based on volatility and performance
- **Three-Tier Exit System**: TP1 (quick win), TP2 (momentum), Runner (home runs)
- **Automated Breakeven**: Protects profits after TP1
- **Correlation Protection**: Reduces risk during abnormal market conditions

### Data-Driven Improvements
- **Performance Analytics**: Know exactly what's working and what isn't
- **Time Analysis**: Trade only during your most profitable hours
- **Pattern Success Tracking**: Focus on highest probability setups
- **Automated Optimization**: Let data guide parameter adjustments

### Reliability & Monitoring
- **WebSocket Real-Time Data**: No missed opportunities from polling delays
- **Auto-Recovery**: Handles disconnections and errors gracefully
- **Live Dashboard**: Monitor performance without touching code
- **Comprehensive Logging**: Debug issues and analyze decisions

## 🛡️ Risk Management Rules

1. **Hard Rules** (Never Violated):
   - Stop trading after $800 daily loss
   - Maximum $500 risk per trade
   - **Maximum 5 GC or 50 MGC position size (exchange/broker limit)**
   - Stop after 2 consecutive losses
   - Exit all positions by 10:15 PM
   - **No trading 30 mins before/after high impact news**
   - **Close all positions before FOMC/NFP**

2. **Soft Rules** (Adjustable):
   - 3 trades per day maximum
   - Dynamic stops (30-50 ticks based on setup)
   - Risk/Reward between 1:1 and 1:2.5
   - Trade only clear patterns
   - Skip choppy/news-heavy days
   - **Reduce size to 50% near medium impact news**
   - **Prefer entries near high volume nodes**
   - **Avoid trading in low volume node zones**

## 🏃 Getting Started

### Day 1-3: Setup
```bash
# Clone repo and install
git clone <your-repo>
cd topstep-bot
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your API key

# Test connection
python test_auth.py
```

### Day 4-7: Paper Trade
```bash
# Run in paper mode
python main.py --paper

# Monitor logs
tail -f logs/trades.log
```

### Week 2+: Refine
- Review logs daily
- Adjust parameters based on results
- Only add features that solve real problems

## 💡 Key Success Principles

1. **Start Simple**: Get basic buy/sell working before adding features
2. **Log Everything**: You can't improve what you don't measure
3. **Paper Trade First**: Iron out bugs with fake money
4. **One Change at a Time**: Makes debugging easier
5. **Trust the Process**: Consistency beats home runs

## 📈 Scaling Path

Only after consistent profitability:

1. **Month 1**: 5 MGC with basic strategy
2. **Month 2**: Add partial profits and trailing stops
3. **Month 3**: Increase to 10 MGC or 1 GC if profitable
4. **Month 4+**: Add 1H timeframe confirmation

## 🚨 Common Pitfalls to Avoid

1. **Over-optimizing**: Perfect is the enemy of good
2. **Feature Creep**: Adding complexity too fast
3. **Ignoring Losses**: Every loss is a learning opportunity
4. **Chasing Profits**: Stick to the plan
5. **Assuming API Reliability**: Always have error handling

## 📞 When You're Stuck

1. Check the logs first
2. Verify API connection
3. Confirm market hours
4. Review recent trades
5. Simplify and retry

## 📊 Success Metrics & Milestones

### MVP Completion (End of Week 4)
- ✅ Executes 20+ paper trades without errors
- ✅ Maintains accurate position tracking
- ✅ Respects all risk limits
- ✅ Generates performance reports
- ✅ Runs 24 hours without intervention

### Production Ready (End of Month 2)
- ✅ 50%+ win rate in backtesting
- ✅ Positive expectancy over 500+ trades
- ✅ Automated parameter optimization
- ✅ Real-time monitoring dashboard
- ✅ < 5 minute recovery from any failure

### TopStep Funded (Month 3+)
- ✅ Passed evaluation
- ✅ Consistent daily profits
- ✅ < 5% daily drawdown
- ✅ Systematic scaling plan
- ✅ Full automation achieved

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **API Client**: aiohttp for async operations
- **WebSocket**: websockets library
- **Database**: SQLite for trade history
- **Dashboard**: Flask + Bootstrap
- **Charting**: Plotly for visualizations
- **Backtesting**: Vectorized NumPy operations
- **Deployment**: Docker containerization

## 💰 Realistic Budget & Returns

### Development Investment
- **Time**: 2 months part-time (10-15 hours/week)
- **TopStepX API**: $14.50/month
- **VPS (after funding)**: $20-40/month
- **Total Cost**: ~$100 + your time

### Expected Returns
- **Month 1-2**: -$100 (development costs)
- **Month 3**: Break even (pass evaluation)
- **Month 4+**: $1,000-2,400/month (conservative funded account)
- **Year 1 Goal**: $15,000-25,000 net profit
- **Per Trade Expectation**: $150-400 profit (based on 1:1.5 avg R:R)

---

**Remember**: This is a professional tool that can generate consistent income. The effort you put in during development will pay dividends for years. Build it right, and it becomes a valuable asset.

**Final Thought**: You're not building a "simple" bot - you're building a *focused* bot that does a few things exceptionally well. 