# TopStep Gold Futures Bot - Complete Implementation Plan 🥇

A comprehensive guide combining both practical and detailed approaches to building a profitable Gold Futures trading bot. Realistic timeline, flexible structure, complete implementation details.

**Note**: This is the active plan. The file `/Plans/MainPlan/Ultimate_Practical_Plan_Combined.md` contains the same content and was created from merging the original practical and detailed plans.

## 🎯 Core Philosophy
**Start Small. Prove It Works. Scale Gradually.**

Build what matters first, add complexity only when profitable.

**Important Note**: This plan is a living document. Technical decisions, implementations, and even file structure may change as we build and learn. The goal is a working, profitable bot - not rigid adherence to initial plans.

## 📋 What We're Actually Building

### The Reality
- **Week 1**: Connect to API and execute trades
- **Week 2**: Detect basic SMC patterns (order blocks first)
- **Week 3**: Add risk management and position sizing
- **Week 4**: Implement JSON status monitoring system
- **Week 5-6**: Add advanced patterns (breaker blocks, inducement)
- **Week 7-8**: Polish, backtest, and go live

### What We're NOT Building (Yet)
- Complex ML systems (neural networks, deep learning)
- 20+ file architectures
- Real-time web dashboards
- Fancy optimization algorithms

### What We ARE Building
- Simple self-learning system that tracks pattern performance
- Adaptive position sizing based on recent results
- Pattern discovery from actual trade outcomes
- No ML complexity - just "track what works"

## 📁 Evolving File Structure

### Phase 1: Prove It Works (Week 1-2) - 3 Files
```
gold-bot/
├── bot.py                 # Everything in one file initially
├── config.py              # Basic settings
├── .env                   # API credentials
└── test_connection.py     # Verify we can connect and trade
```
**Goal**: Can we connect? Can we place orders? Start here!

### Phase 2: Core Functionality (Week 3-4) - 5 Files
```
gold-bot/
├── bot.py                 # Main bot logic
├── broker.py              # Split out API wrapper
├── patterns.py            # Basic order block detection
├── config.py              # Settings
├── .env                   # API credentials
└── logs/
    └── trades.log         # Simple trade logging
```
**Goal**: Detect patterns, execute trades, log results

### Phase 3: Add Core Features (Week 3-6) - 7 Files
```
gold-bot/
├── bot.py                 # Main logic
├── broker.py              # API wrapper
├── patterns.py            # Order blocks
├── risk_manager.py        # Position sizing
├── monitoring.py          # JSON status
├── config.py              # Settings
├── .env                   # API keys
└── logs/
    ├── status.json        # Current status
    └── trades_today.json  # Today's trades
```

### Phase 4: Risk & Monitoring (Week 5-6) - 8 Files
```
gold-bot/
├── bot.py                 # Main bot logic
├── broker.py              # TopStepX API wrapper
├── data_feed.py           # Market data (split from broker)
├── patterns.py            # SMC patterns (OB, structure)
├── risk_manager.py        # Position sizing and limits (NEW)
├── monitoring.py          # Status updates (NEW)
├── config.py              # All settings
├── .env                   # API credentials
└── logs/
    ├── status.json        # Current bot status
    ├── trades_today.json  # Today's trades
    └── signals.log        # All detected signals
```
**Goal**: Never blow account, monitor performance

### Phase 5: Learning & Enhancement (Week 7-8) - 10 Files
```
gold-bot/
├── bot.py                 # Main bot logic
├── broker.py              # TopStepX API wrapper
├── data_feed.py           # Market data and DXY
├── smc_patterns.py        # Basic patterns
├── advanced_patterns.py   # Breaker blocks, inducement (NEW)
├── risk_manager.py        # Position sizing and limits
├── learning_system.py     # Self-learning (NEW)
├── monitoring.py          # Status update functions
├── config.py              # All settings
├── .env                   # API credentials
├── requirements.txt       # Dependencies (NEW)
└── logs/
    ├── status.json        # Current bot status
    ├── trades_today.json  # Today's trades
    ├── signals.log        # All detected signals
    └── bot_learning.json  # Learned patterns (NEW)
```
**Goal**: Bot learns and improves, advanced patterns

### Future: Production Ready (Month 3+) - Organized Structure
```
gold-bot/
├── src/
│   ├── __init__.py
│   ├── bot.py
│   ├── broker/
│   │   ├── __init__.py
│   │   ├── topstep.py
│   │   └── websocket_handler.py  # If needed
│   ├── patterns/
│   │   ├── __init__.py
│   │   ├── smc_basic.py
│   │   └── smc_advanced.py
│   ├── risk_manager.py
│   ├── learning_system.py
│   └── monitoring.py
├── tests/
│   ├── test_patterns.py
│   ├── test_risk.py
│   └── test_broker.py
├── backtest/
│   ├── engine.py
│   └── data/
├── config.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── README.md
└── logs/
```
**Goal**: Professional structure, ready for cloud deployment

**Evolution Notes**:
- Start with EVERYTHING in bot.py (even patterns)
- Split files only when they exceed 300 lines
- Add files only when current structure feels painful
- WebSocket handler only if broker.py gets complex
- Utils.py is a code smell - avoid until absolutely necessary

## 🔄 Plan Flexibility & Expected Changes

### What Might Change During Development:

1. **File Structure**
   - Might need `websocket_handler.py` if connection logic gets complex
   - Could split `smc_patterns.py` into basic and advanced
   - Might add `backtest.py` if we decide to build backtesting
   - Could need `notifications.py` for alerts

2. **Technical Decisions**
   - WebSocket vs REST API polling (depends on TopStepX capabilities)
   - Async vs threading (might change based on performance)
   - Database choice (SQLite vs PostgreSQL vs just JSON)
   - Pattern detection algorithms (might find better approaches)

3. **Timeline Adjustments**
   - Pattern detection might need 3 weeks instead of 2
   - Risk management could be done in 1 week if straightforward
   - Might need extra week for API quirks and edge cases
   - Paper trading might reveal issues requiring 2 more weeks

4. **Feature Scope**
   - Might skip some advanced patterns if basics work well
   - Could add correlation trading if DXY relationship is strong
   - Might simplify or enhance dashboard based on actual needs
   - Could add features we haven't thought of yet

### What WON'T Change:
- Core risk management rules
- TopStep compliance requirements
- Focus on profitability over complexity
- Test-first approach

**Remember**: The best plan is one that adapts to reality. If something isn't working, we change it. If something works better than expected, we double down on it.

## ⚠️ Code Examples Disclaimer

**IMPORTANT**: All code examples in this plan are **conceptual sketches**, not production code. They show structure and intent but skip:
- Error handling
- Edge cases
- Real API details
- Recovery logic
- Actual algorithms

Treat them as **conversation starters**, not copy-paste solutions. The real implementation will be 5-10x more complex.

## 🔧 Complete Configuration

```python
# config.py - Everything in one place
import os
from datetime import time
from typing import Dict, List

class Config:
    # API Settings
    TOPSTEP_API_KEY = os.getenv('TOPSTEP_API_KEY')
    TOPSTEP_API_SECRET = os.getenv('TOPSTEP_API_SECRET')
    PAPER_TRADING = True  # Start with paper!
    
    # WebSocket URLs
    WS_DATA_URL = "wss://api.topstepx.com/market-data"
    WS_TRADING_URL = "wss://api.topstepx.com/trading"
    
    # Contract Specifications
    SYMBOL = 'MGC'  # Micro Gold
    TICK_SIZE = 0.10  # $0.10 price movement
    TICK_VALUE = 1.0  # $1 per tick
    CONTRACT_MONTHS = ['G', 'J', 'M', 'Q', 'V', 'Z']  # Feb, Apr, Jun, Aug, Oct, Dec
    
    # Position Limits
    MAX_POSITION_MGC = 50  # Exchange limit
    MIN_POSITION_MGC = 5   # Our minimum
    DEFAULT_POSITION_MGC = 8  # Starting size
    
    # Risk Parameters (TopStep Rules)
    ACCOUNT_SIZE = 50000
    DAILY_LOSS_LIMIT = 800  # Hard stop
    TRAILING_DRAWDOWN = 2000  # TopStep trailing
    MAX_RISK_PER_TRADE = 500
    WARNING_RISK_PER_TRADE = 400  # Alert level
    MAX_CONSECUTIVE_LOSSES = 2
    
    # Trading Hours (Helsinki Time)
    SESSION_START = time(16, 45)  # 4:45 PM
    SESSION_END = time(22, 30)    # 10:30 PM
    NEWS_BLACKOUT_START = time(22, 15)  # No new trades
    
    # Pattern Detection Settings
    MIN_PATTERN_SCORE = 7  # Only high-quality trades
    LOOKBACK_CANDLES = 100
    MIN_VOLUME_RATIO = 1.5  # vs 20-period average
    
    # Order Block Settings
    MIN_OB_MOVE_TICKS = 20  # Minimum displacement
    MAX_OB_AGE_CANDLES = 50  # How old can OB be
    MIN_OB_TOUCHES = 1  # Before considering valid
    
    # Stop Loss Settings
    MIN_STOP_TICKS = 25  # Absolute minimum
    MAX_STOP_TICKS = 50  # Risk limit constraint
    DEFAULT_STOP_TICKS = 35  # Starting point
    ATR_STOP_MULTIPLIER = 1.5  # For volatility adjustment
    
    # Take Profit Settings
    TP1_RATIO = 1.0  # 1:1 (50% exit)
    TP2_RATIO = 2.0  # 1:2 (40% exit)
    RUNNER_RATIO = 2.5  # Max runner target
    
    # Timeframes
    PRIMARY_TIMEFRAME = '15m'  # Entry signals
    HTF_TIMEFRAME = '1h'  # Trend filter
    ENTRY_TIMEFRAME = '5m'  # Fine-tuning (optional)
    
    # DXY Correlation
    DXY_SYMBOL = 'DX'  # Dollar Index
    MIN_CORRELATION = -0.7  # Gold/Dollar inverse
    CORRELATION_PERIOD = 20  # Candles
    
    # Logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    LOG_TRADES = True
    LOG_SIGNALS = True
    LOG_ERRORS = True
    
    # Trading Stages
    TRADING_STAGE = "BASIC"  # BASIC → ENHANCED → ADVANCED
    
    @classmethod
    def get_active_contract(cls) -> str:
        """Get current active gold futures contract"""
        # Implementation would determine current front month
        return "MGCM24"  # Example: June 2024
```

## 📅 Realistic Timeline (10 Weeks)

**Flexibility Note**: Some weeks might take longer, some shorter. If Week 2 takes 10 days instead of 7, that's fine. Quality over speed.

### Overview:
- **Weeks 1-2**: Foundation (Connection, Data, Basic Execution)
- **Weeks 3-4**: Core Patterns (Order Blocks, Market Structure)
- **Weeks 5-6**: Risk Management & Dashboard
- **Weeks 7-8**: Enhanced Patterns (Breaker Blocks, Inducement)
- **Weeks 9-10**: Testing, Optimization, Paper Trading

## 🚦 Week 1-2: Foundation (Detailed)

### Monday-Tuesday: API Connection & Order Execution

**Goal**: Execute trades via API without errors

```python
# broker.py - SKETCH v1 (Week 1-2: Just get connected)
class TopStepBroker:
    """Handle API connection and basic orders"""
    
    async def connect(self) -> bool:
        """CONCEPT: WebSocket connection"""
        # TODO: Add retry logic, heartbeat, reconnection
        self.ws = await websockets.connect(url, auth=credentials)
        return self.ws.open
    
    async def place_order_v1(self, side: str, quantity: int):
        """Week 1: Can we place ANY order?"""
        # SIMPLIFIED: Just market orders first
        order = {"action": "order", "side": side, "qty": quantity}
        return await self.ws.send(json.dumps(order))

# broker.py - SKETCH v2 (Week 3-4: Add stops/targets)
class TopStepBroker:
    async def place_order_v2(self, side: str, quantity: int, stop: float, target: float):
        """Week 3: Add bracket orders"""
        # TODO: Handle partial fills, rejections, modifications
        bracket_order = {
            "action": "bracket",
            "side": side,
            "quantity": quantity,
            "stop_loss": stop,     # SIMPLIFIED: Assumes API wants this format
            "take_profit": target  # REALITY: Probably more complex
        }
        # TODO: Add timeout, error handling, order tracking
        
# broker.py - SKETCH v3 (Week 5+: Production features)  
class TopStepBroker:
    async def place_order_v3(self, signal: Signal) -> OrderResult:
        """Production: Full order management"""
        # TODO: 
        # - Position size validation
        # - Margin checks
        # - Order modification
        # - Partial fill handling
        # - Disconnect recovery
        # Real implementation will be 10x this size
    
    async def flatten_all(self) -> bool:
        """Emergency close all positions"""
        try:
            request = {
                "action": "flatten_all",
                "account": "PAPER" if self.config.PAPER_TRADING else "LIVE",
                "confirm": True
            }
            
            await self.ws_trading.send(json.dumps(request))
            response = await self.ws_trading.recv()
            
            result = json.loads(response)
            if result.get("status") == "success":
                logger.warning("All positions flattened")
                self.positions = {}
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to flatten positions: {e}")
            return False
    
    async def _get_account_info(self):
        """Get account balance and details"""
        request = {
            "action": "get_account",
            "account": "PAPER" if self.config.PAPER_TRADING else "LIVE"
        }
        
        await self.ws_trading.send(json.dumps(request))
        response = await self.ws_trading.recv()
        
        self.account_info = json.loads(response)
        logger.info(f"Account Balance: ${self.account_info.get('balance', 0):,.2f}")
        
    def _get_auth_headers(self) -> Dict:
        """Get authentication headers"""
        return {
            "X-API-KEY": self.config.TOPSTEP_API_KEY,
            "X-API-SECRET": self.config.TOPSTEP_API_SECRET
        }
```

### Wednesday-Thursday: Market Data Feed

```python
# data_feed.py - SKETCH (Progressive versions)

# Week 1: Can we get any data?
class DataFeed_v1:
    """CONCEPT: Just get price data flowing"""
    
    async def get_candles(self, symbol: str) -> pd.DataFrame:
        # TODO: Real WebSocket subscription
        # TODO: Handle disconnections
        response = await self.broker.ws.send({"get": "candles", "symbol": symbol})
        return pd.DataFrame(response)  # SIMPLIFIED: No error handling

# Week 2: Add calculations
class DataFeed_v2:
    """Add technical indicators"""
    
    async def get_candles(self, symbol: str, timeframe: str) -> pd.DataFrame:
        df = await self._fetch_candles(symbol, timeframe)
        
        # CONCEPT: Add basic calculations
        df['atr'] = self._calculate_atr(df)  # TODO: Implement
        df['volume_spike'] = df['volume'] > df['volume'].mean() * 1.5
        
        return df
    
    async def get_current_price(self, symbol: str) -> float:
        # TODO: Real-time price updates via WebSocket
        return self.current_prices.get(symbol, 0.0)

# Week 3-4: DXY Correlation
class DataFeed_v3:
    """Add correlation and caching"""
    
    async def get_dxy_correlation(self) -> float:
        """SIMPLIFIED: Basic correlation calc"""
        # TODO: 
        # - Handle different data frequencies
        # - Missing data alignment
        # - Rolling window optimization
        gold = await self.get_candles("MGC", "15m")
        dxy = await self.get_candles("DXY", "15m")
        
        # CONCEPT: Simple correlation
        return gold['close'].corr(dxy['close'])
    
    # REALITY CHECK: Need to handle:
    # - Market hours differences
    # - Data quality issues  
    # - Calculation performance
    # - Cache invalidation
```

### Friday: Testing Checklist

```python
# test_week1.py - SKETCH: Basic validation

# Week 1: Can we do ANYTHING?
async def test_basics_v1():
    """Minimum viable tests"""
    # 1. Connect?
    broker = TopStepBroker(config)
    assert await broker.connect()  # TODO: Add timeout
    
    # 2. Get data?
    candles = await feed.get_candles("MGC")
    assert len(candles) > 0  # TODO: Validate data quality
    
    # 3. Place order?
    result = await broker.place_order_v1("BUY", 5)
    assert result  # TODO: Check fills, handle rejections

# Week 2: More sophisticated tests
async def test_basics_v2():
    """Test error handling"""
    # TODO: Test disconnection recovery
    # TODO: Test invalid orders
    # TODO: Test data gaps
    # TODO: Test outside market hours
```

## 🚦 Week 3-4: Pattern Detection (Detailed)

**Goal**: Detect order blocks reliably

**Implementation Note**: Pattern detection is where many bots fail. Take your time here. If you need to refactor the detection logic 3 times to get it right, that's normal.

### Order Block Detection Algorithm

```python
# smc_patterns.py - SKETCH (Progressive versions)

# Week 3: Just find SOMETHING that looks like an order block
class SMCPatterns_v1:
    """CONCEPT: Basic order block detection"""
    
    def find_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """v1: Find big candles before moves"""
        obs = []
        
        # SIMPLIFIED: Just find large opposing candles
        for i in range(1, len(df)-1):
            current = df.iloc[i]
            next_candle = df.iloc[i+1]
            
            # Bullish OB: Big red before green move
            if (current['close'] < current['open'] and  # Red candle
                next_candle['close'] > current['high']):  # Green breaks high
                
                obs.append({
                    'type': 'bullish',
                    'level': current['low'],
                    'index': i
                })
        
        return obs
        
        # TODO: Define "big" properly
        # TODO: Add volume confirmation
        # TODO: Check market structure

# Week 4: Add scoring and validation
class SMCPatterns_v2:
    """Add quality scoring"""
    
    def find_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        # TODO: Add these checks:
        # - Volume spike (> 1.5x average)
        # - Clean move away (no retest)
        # - At structure level (HH/LL)
        # - Body-to-wick ratio
        
        obs = self._find_basic_obs(df)
        
        # CONCEPT: Score each OB
        for ob in obs:
            ob.score = self._calculate_score(ob, df)
            
        # Only return high quality
        return [ob for ob in obs if ob.score >= 7]
    
    def calculate_score(self, pattern):
        """Score 1-10 based on quality"""
        score = 0
        if pattern.has_volume: score += 2
        if pattern.at_structure: score += 2
        if pattern.clean_move: score += 2
        # etc...
        return score

# Week 5+: Production features
class SMCPatterns_v3:
    """Full implementation"""
    
    def find_patterns(self, df: pd.DataFrame) -> Dict[str, List]:
        """Find all SMC patterns"""
        return {
            'order_blocks': self._find_order_blocks(df),
            'breaker_blocks': [],  # TODO: Week 6
            'fair_value_gaps': [],  # TODO: Week 7
            'liquidity_pools': []   # TODO: Week 8
        }
    
    # REALITY CHECK:
    # - Pattern detection is 10% of success
    # - Execution and risk management is 90%
    # - Don't over-optimize patterns
```

### Testing Pattern Detection

```python
# test_week2.py - SKETCH: Validate patterns work

async def test_patterns_v1():
    """Week 3-4: Do patterns find anything?"""
    patterns = SMCPatterns_v1()
    candles = await feed.get_candles("MGC", "15m")
    
    obs = patterns.find_order_blocks(candles)
    print(f"Found {len(obs)} order blocks")
    
    # TODO: Manually verify these make sense
    # TODO: Backtest on historical data
    # TODO: Compare with manual analysis
```

## 🚦 Week 5-6: Risk Management & Self-Learning System (Detailed)

**Goal**: Never blow the account + Bot that improves automatically

**Critical Note**: Risk management is non-negotiable. If this takes 2 full weeks to get right, it's worth it. This is what keeps you in the game.

### 🧠 Self-Learning System Integration

**Goal**: Bot that improves automatically without complex ML

**Core Learning Components**:

1. **Pattern Performance Tracking**
   - Track win/loss rate for each pattern type (order blocks, breaker blocks, etc.)
   - Record average profit/loss per pattern
   - Identify which market conditions help each pattern succeed
   - Automatically disable patterns that consistently lose money (< 40% win rate)

2. **Dynamic Position Sizing**
   - Start with minimum size (2-5 contracts) while learning
   - Increase size after consecutive wins (up to 15 contracts max)
   - Decrease size after losses to protect capital
   - Base size on recent 20-trade performance and confidence level

3. **Condition Discovery**
   - Track which conditions were present for winning trades
   - Learn correlations (e.g., "order blocks work 75% of time in NY session")
   - Discover toxic combinations (e.g., "never trade near news events")
   - Build personalized trading rules from actual results

4. **Progressive Complexity**
   - Start with ONE pattern only (order blocks)
   - Add new patterns only after current ones prove profitable
   - Each pattern must prove itself over minimum 20 trades
   - Remove patterns with consistent poor performance

**How the Learning System Works**:
1. **Every Trade**: Log pattern type, market conditions, and outcome
2. **Every 10 Trades**: Update pattern statistics and win rates
3. **Every 20 Trades**: Adjust position sizing based on performance
4. **Every 50 Trades**: Enable/disable patterns based on profitability
5. **Weekly**: Generate insights report on what's working

**No Complex ML Needed**:
- Simple tracking: "When I did X, I made/lost $Y"
- Basic statistics: win rate, average profit, profit factor
- Clear rules: "If pattern wins < 40%, stop using it"
- Gradual evolution: "NY session adds 15% to win rate"

**Learning Data Structure**:
- All learning stored in bot_learning.json
- Pattern performance stats updated after each trade
- Condition correlations tracked continuously
- Position sizing rules adapt based on recent performance

```python
# risk_manager.py - SKETCH (Progressive versions)

# Week 5: Basic risk checks
class RiskManager_v1:
    """CONCEPT: Don't blow the account"""
    
    def can_trade(self) -> bool:
        # v1: Just check daily loss
        if self.daily_pnl <= -800:  # TopStep limit
            return False
            
        if self.daily_trades >= 3:  # Start conservative
            return False
            
        return True
    
    def calculate_position_size(self, stop_ticks: int) -> int:
        """v1: Fixed size to start"""
        # TODO: Dynamic sizing based on stop
        # TODO: Reduce after losses
        # TODO: Scale with confidence
        return 5  # Start with 5 MGC always

# Week 6: Smarter position sizing
class RiskManager_v2:
    """Add dynamic position sizing"""
    
    def can_trade(self):
        # Check daily loss
        # Check consecutive losses
        # Check time of day
        
    def calculate_position_size(self, stop_ticks: int) -> int:
        max_risk = 500  # $500 per trade
        
        # After losses, reduce risk
        if self.consecutive_losses >= 2:
            max_risk = 250
            
        # Calculate size
        size = int(max_risk / stop_ticks)
        
        # Apply limits
        return max(2, min(size, 50))  # 2-50 contracts
        
    def emergency_stop(self):
        # Flatten everything
        # Stop the bot

# v3: Production with statistics
class RiskManager_v3:
    """Add performance tracking and emergency procedures"""
    def __init__(self):
        self.v2_features = "All from v2..."
        self.trade_history = []
        
    def record_trade(self, trade):
        """Track every trade outcome"""
        # TODO: Store pnl, pattern type, conditions
        # TODO: Update consecutive loss counter
        # TODO: Calculate running statistics
        
    def get_statistics(self):
        """Calculate performance metrics"""
        # TODO: Win rate, profit factor, avg win/loss
        # TODO: Pattern-specific stats
        # TODO: Time-of-day analysis
        
    def emergency_stop(self):
        """CRITICAL: Flatten all positions"""
        # TODO: Create EMERGENCY_STOP.txt
        # TODO: Close all positions via broker
        # TODO: Alert user somehow
```

```python
# learning_system.py - Self-learning implementation
class LearningSystem:
    def __init__(self):
        self.pattern_stats = {}
        self.condition_correlations = {}
        self.enabled_patterns = ['order_blocks']  # Start with one
        self.position_sizing_rules = {
            'base_size': 5,
            'confidence_multiplier': 1.0,
            'recent_performance': []
        }
        
    def record_trade_result(self, trade):
        """Log every trade for learning"""
        pattern = trade['pattern']
        conditions = trade['conditions']
        outcome = trade['pnl']
        
        # Update pattern statistics
        if pattern not in self.pattern_stats:
            self.pattern_stats[pattern] = {
                'trades': 0,
                'wins': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0
            }
            
        stats = self.pattern_stats[pattern]
        stats['trades'] += 1
        if outcome > 0:
            stats['wins'] += 1
        stats['total_pnl'] += outcome
        stats['win_rate'] = stats['wins'] / stats['trades']
        
        # Track condition correlations
        for condition, value in conditions.items():
            key = f"{condition}:{value}"
            if key not in self.condition_correlations:
                self.condition_correlations[key] = {'wins': 0, 'total': 0}
            
            self.condition_correlations[key]['total'] += 1
            if outcome > 0:
                self.condition_correlations[key]['wins'] += 1
                
        # Update position sizing
        self.recent_performance.append(outcome > 0)
        if len(self.recent_performance) > 20:
            self.recent_performance.pop(0)
            
        # Adjust confidence
        if len(self.recent_performance) >= 10:
            recent_win_rate = sum(self.recent_performance) / len(self.recent_performance)
            if recent_win_rate > 0.6:
                self.confidence_multiplier = 1.5
            elif recent_win_rate < 0.4:
                self.confidence_multiplier = 0.5
            else:
                self.confidence_multiplier = 1.0
                
        # Disable poor patterns
        if stats['trades'] >= 20 and stats['win_rate'] < 0.4:
            if pattern in self.enabled_patterns:
                self.enabled_patterns.remove(pattern)
                print(f"❌ Disabling {pattern} - Win rate: {stats['win_rate']:.1%}")
                
        # Enable new patterns when ready
        if 'order_blocks' in self.pattern_stats:
            ob_stats = self.pattern_stats['order_blocks']
            if ob_stats['trades'] >= 50 and ob_stats['win_rate'] > 0.5:
                if 'breaker_blocks' not in self.enabled_patterns:
                    self.enabled_patterns.append('breaker_blocks')
                    print("✅ Enabling breaker blocks pattern")
```

## 🚦 Week 5-6: JSON Status Monitoring (Detailed)

**Goal**: Simple, reliable monitoring that actually works

**Development Note**: Simple, reliable monitoring that actually works in production. No Jupyter kernels to crash, no browser required.

```python
# monitoring.py - JSON status monitoring (progressive versions)

# v1: Basic heartbeat
class MonitoringSystem_v1:
    """Minimal monitoring - just prove bot is alive"""
    def __init__(self):
        os.makedirs('logs', exist_ok=True)
        
    def update_status(self, bot):
        """Write simple status every 30 seconds"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "is_alive": True,
            "daily_pnl": bot.daily_pnl
        }
        # TODO: Write to status.json
        # TODO: Handle write errors

# v2: Full monitoring
class MonitoringSystem_v2:
    """Complete monitoring with positions, trades, errors"""
    def update_status(self, bot):
        """Write current status to JSON file"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "is_alive": True,
            "daily_pnl": self.daily_pnl,
            "open_positions": len(self.positions),
            "active_trades": [
                {"symbol": t.symbol, "side": t.side, "pnl": t.unrealized_pnl}
                for t in self.positions
            ],
            "last_signal": self.last_signal_time,
            "patterns_enabled": self.learning_system.enabled_patterns,
            "errors_today": len(self.recent_errors),
            "next_update": (datetime.now() + timedelta(seconds=30)).isoformat()
        }
        
        # Overwrite file (stays small ~1KB)
        with open('logs/status.json', 'w') as f:
            json.dump(status, f, indent=2)

# v3: Production monitoring with alerting
class MonitoringSystem_v3:
    """Add learning stats and advanced features"""
    def update_status(self, bot):
        # All v2 features plus:
        # TODO: Pattern performance stats
        # TODO: Learning system metrics
        # TODO: Predictive warnings
        # TODO: Slack/email alerts on errors
    
    def create_dashboard_html(self):
        """Generate simple HTML dashboard"""
        # TODO: Read JSON files
        # TODO: Create simple HTML with charts
        # TODO: Auto-refresh JavaScript
```

### How to Use JSON Monitoring:

**1. Check Bot Status (from anywhere):**
```bash
# View current status
cat logs/status.json

# Pretty print with jq
jq . logs/status.json

# Watch status updates
watch -n 5 cat logs/status.json

# Check if bot is alive
jq .is_alive logs/status.json
```

**2. Monitor Today's Trades:**
```bash
# View today's trades
cat logs/trades_today.json

# Check win rate
jq .summary.win_rate logs/trades_today.json

# List all trades
jq '.trades[] | {time, pattern, pnl}' logs/trades_today.json
```

**3. Quick Status Script:**
```bash
#!/bin/bash
# save as check_bot.sh
echo "=== Bot Status ==="
echo "Alive: $(jq .is_alive logs/status.json)"
echo "P&L: $(jq .account.daily_pnl logs/status.json)"
echo "Positions: $(jq '.positions | length' logs/status.json)"
echo "Can Trade: $(jq .risk.can_trade logs/status.json)"
```

**4. Integration with Bot:**
```python
# In bot.py main loop
async def _status_updater(self):
    """Update status files every 30 seconds"""
    while self.is_running:
        try:
            self.monitoring.update_status(self)
            self.monitoring.update_trades(self)
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Status update error: {e}")
            await asyncio.sleep(60)
```

### Future Enhancement: Terminal Dashboard

**After the JSON monitoring is working well, consider upgrading to a rich terminal dashboard:**

```python
# terminal_dashboard.py (Future enhancement)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import asyncio

console = Console()

async def terminal_dashboard(bot):
    """Professional terminal monitoring"""
    with Live(console=console, refresh_per_second=1) as live:
        while bot.is_running:
            # Create dashboard layout
            layout = create_dashboard_layout(bot)
            live.update(layout)
            await asyncio.sleep(1)

def create_dashboard_layout(bot):
    """Create rich terminal layout"""
    # Account panel
    account_table = Table(show_header=False)
    account_table.add_row("Balance", f"${bot.broker.account_info.get('balance', 0):,.2f}")
    account_table.add_row("Daily P&L", f"${bot.risk_manager.daily_pnl:+.2f}")
    account_table.add_row("Positions", str(len(bot.positions)))
    
    return Panel(account_table, title="Gold Trading Bot")
```

**Note**: The terminal dashboard is a future enhancement. Start with JSON monitoring first, which is simpler and more reliable.

## 🚦 Week 7-8: Enhanced Patterns (Detailed)

**Goal**: Add breaker blocks and inducement

**Evolution Note**: Only add these patterns after basic order blocks are profitable. If OBs aren't working, breaker blocks won't save you. We might even decide to skip some patterns if the basics are performing well.

```python
# Enhanced smc_patterns.py - Progressive versions

# v2: Add breaker blocks (only if v1 profitable)
class SMCPatterns_v2:
    """Add breaker blocks to existing order blocks"""
    def __init__(self):
        self.v1_features = "All basic OB detection..."
        
    def find_breaker_blocks(self, candles):
        """Failed OBs that flip direction"""
        # TODO: Find order blocks first
        # TODO: Check which OBs were broken
        # TODO: Look for retest of broken OB
        # TODO: Breaker = stronger signal
        
    def calculate_score_v2(self, pattern):
        """Enhanced scoring with breakers"""
        score = self.calculate_score_v1(pattern)
        if pattern.type == 'breaker_block':
            score += 2  # Breakers score higher
        return score
    
    def find_inducement(self, candles):
        """Equal highs/lows that trap traders"""
        # Look for liquidity pools
        
    def detect_choch_vs_bos(self, candles):
        """Distinguish reversal vs continuation"""
        # Critical for trend trading

# v3: Add inducement patterns (only if v2 profitable)  
class SMCPatterns_v3:
    """Add liquidity sweeps and traps"""
    def find_inducement(self, candles):
        """Equal highs/lows that get swept"""
        # TODO: Find equal price levels (2+ touches)
        # TODO: Detect liquidity sweep
        # TODO: Look for reversal after sweep
        # TODO: Higher probability setups
        
    def detect_choch_vs_bos(self, candles):
        """Change of Character vs Break of Structure"""
        # TODO: Find swing highs/lows
        # TODO: Determine current trend
        # TODO: ChoCH = trend reversal signal
        # TODO: BOS = trend continuation
        
# v4: Complete SMC suite (months later)
class SMCPatterns_v4:
    """Add advanced concepts when basics mastered"""
    # TODO: Mitigation blocks
    # TODO: Fair value gaps
    # TODO: Power of 3 (AMD)
    # TODO: Kill zones timing
```

## 🚦 Week 9-10: Main Bot Logic & Testing (Detailed)

**Goal**: Profitable paper trading

**Final Phase Note**: This is where everything comes together. Don't rush. The difference between a bot that works and one that makes money is thorough testing. If you need an extra week for paper trading, take it.

```python
# bot.py - Progressive versions

# v1: Minimal working bot
class GoldBot_v1:
    """Just prove we can trade"""
    def __init__(self):
        self.broker = TopStepBroker()
        self.data_feed = DataFeed()
        self.patterns = SMCPatterns()
        self.is_running = False
        
    async def run(self):
        """Simple trading loop"""
        while self.is_running:
            # TODO: Get candles
            # TODO: Find order blocks
            # TODO: If score > 7, trade
            # TODO: Sleep 30 seconds
            await asyncio.sleep(30)

# v2: Add risk and monitoring            
class GoldBot_v2:
    """Real trading with safety"""
    def __init__(self):
        self.v1_features = "All from v1..."
        self.risk_manager = RiskManager()
        self.monitoring = MonitoringSystem()
        self.settings = {
            'enabled': True,
            'max_trades': 3
        }
        
    async def run(self):
        """Multi-task architecture"""
        # TODO: Connect to broker
        # TODO: Start concurrent tasks:
        #   - Trading loop
        #   - Position monitor
        #   - Risk monitor
        #   - Status updater
        tasks = [
            self._trading_loop(),
            self._monitor_positions(),
            self._update_status()
        ]
        await asyncio.gather(*tasks)
        
    async def _trading_loop(self):
        """Core trading logic"""
        while self.is_running:
            # TODO: Check risk.can_trade()
            # TODO: Get candles
            # TODO: Find patterns
            # TODO: Score patterns
            # TODO: Check DXY
            # TODO: Execute best signal
            # TODO: Update monitoring
            await asyncio.sleep(30)
            
# v3: Full production bot
class GoldBot_v3:
    """Complete with learning system"""
    def __init__(self):
        self.broker = TopStepBroker()
        self.data = DataFeed()
        self.patterns = SMCPatterns()
        self.risk = RiskManager()
        self.monitoring = MonitoringSystem()
        self.learning = LearningSystem()
        
    async def run(self):
        """Main trading loop"""
        while True:
            # 1. Check if we can trade
            if not self.risk.can_trade():
                await asyncio.sleep(60)
                continue
                
            # 2. Get market data
            candles = await self.data.get_candles('MGC', '15m', 100)
            
            # 3. Find patterns (start basic!)
            patterns = self.patterns.find_order_blocks(candles)
            
            # 4. Score and filter
            for pattern in patterns:
                score = self.patterns.calculate_score(pattern)
                
                if score >= Config.MIN_PATTERN_SCORE:
                    # 5. Check DXY correlation
                    if self.data.get_dxy_correlation() < -0.7:
                        
                        # 6. Calculate position size
                        size = self.risk.calculate_position_size(
                            pattern.stop_distance
                        )
                        
                        # 7. Execute trade
                        await self.broker.place_order(
                            side=pattern.direction,
                            quantity=size,
                            stop=pattern.stop_loss,
                            target=pattern.take_profit
                        )
                        
                        # 8. Log everything
                        self.log_trade(pattern, score)
                        
            await asyncio.sleep(30)
            
    def emergency_shutdown(self):
        """CRITICAL: Stop everything"""
        # TODO: Set is_running = False
        # TODO: Flatten all positions
        # TODO: Write EMERGENCY_STOP.txt
        
# Main function sketch
async def main():
    """Bot entry point"""
    # TODO: Load config
    # TODO: Create bot instance
    # TODO: Start bot.run()
    # TODO: Handle shutdown gracefully

# Actual usage example:
if __name__ == "__main__":
    # v1: Just run it
    bot = GoldBot_v1()
    asyncio.run(bot.run())
    
    # v2: With monitoring
    bot = GoldBot_v2()
    # Check logs/status.json
    
    # v3: Full system
    bot = GoldBot_v3()
    # Learning improves over time
```

## 📊 Testing & Validation Procedures

### Week 9-10: Complete Testing Checklist

**Testing Philosophy**: A bug found in testing costs minutes. A bug found in production costs money and confidence. Test everything, then test it again.

```python
# test_system.py - Progressive testing approach

# v1: Basic component tests
async def test_v1():
    """Test individual components work"""
    # TODO: Test broker connection
    # TODO: Test data feed
    # TODO: Test pattern detection
    # TODO: Manual verification
    print("✓ Connection works")
    print("✓ Can get candles")
    print("✓ Found 3 order blocks")

# v2: Integration tests
async def test_v2():
    """Test components work together"""
    # TODO: Test full signal generation
    # TODO: Test risk calculations
    # TODO: Test order placement (paper)
    # TODO: Test monitoring output
    
# v3: Full system test
async def test_v3():
    """Complete pre-production validation"""
    tests = {
        'connection': test_connection(),
        'data_feed': test_data_feed(),
        'patterns': test_patterns(),
        'risk': test_risk_mgmt(),
        'execution': test_paper_trade(),
        'full_bot': test_bot_integration()
    }
    # TODO: Run all tests
    # TODO: Generate report
    # TODO: 100% pass required

# Paper trading validation
def validate_paper_trades():
    """Before going live"""
    # TODO: 100+ trades minimum
    # TODO: Positive expectancy
    # TODO: Risk rules respected
    # TODO: No system crashes
```

**Checklist**:
- [ ] 50+ paper trades completed
- [ ] Positive expectancy proven
- [ ] All risk rules respected
- [ ] Pattern detection accurate
- [ ] Can run 24 hours without crash
- [ ] Clear logs for debugging

## 🛡️ Risk Rules (Non-Negotiable)

### Hard Stops:
- Daily loss: -$800 → STOP
- Consecutive losses: 2 → STOP
- Time: 10:30 PM → CLOSE ALL
- News in 30 min → NO TRADE

### Position Sizing:
```python
def calculate_position_size(stop_ticks):
    # Start conservative
    if bot.trades_count < 20:
        max_risk = 250  # Half risk while learning
    else:
        max_risk = 500
        
    # Calculate size
    size = max_risk / (stop_ticks * 1.0)
    
    # Apply limits
    return min(
        int(size),
        50,  # Exchange limit
        Config.MAX_POSITION_SIZE  # Our limit
    )
```

## 🚨 Common Issues & Solutions

### Issue 1: WebSocket Disconnections
```python
# Solution: Automatic reconnection
async def maintain_connection(self):
    while True:
        if not self.is_connected:
            logger.warning("Connection lost - reconnecting...")
            await self.connect()
        await asyncio.sleep(30)
```

### Issue 2: Missed Signals
```python
# Solution: Signal queue
self.signal_queue = asyncio.Queue()
# Producer adds signals
await self.signal_queue.put(signal)
# Consumer processes them
signal = await self.signal_queue.get()
```

### Issue 3: Position Sync Issues
```python
# Solution: Regular reconciliation
async def reconcile_positions(self):
    broker_positions = await self.broker.get_positions()
    # Compare with internal state
    # Fix discrepancies
```

## 📊 Realistic Performance Evolution (With Self-Learning)

### Month 1: Learning Phase
- **Trade Size**: 5-8 MGC (conservative)
- **Patterns**: Order blocks only
- **Win Rate**: 40-45% (this is fine!)
- **Goal**: Don't lose money
- **Learning**: Bot discovers best times/conditions for order blocks
- **Adaptation**: Position size adjusts based on performance

### Month 2: Optimization
- **Trade Size**: 10-12 MGC (bot-determined based on results)
- **Patterns**: Add breaker blocks (only if OBs profitable)
- **Win Rate**: 45-50% (improved by learning)
- **Goal**: Small consistent profits
- **Learning**: Bot identifies toxic patterns, disables them
- **Discovery**: "Order blocks + NY session + volume = 65% win rate"

### Month 3: Scaling
- **Trade Size**: 12-16 MGC (confidence-based sizing)
- **Patterns**: Full enhanced SMC (only proven ones)
- **Win Rate**: 50-55% (optimized by experience)
- **Goal**: Pass TopStep evaluation
- **Learning**: Bot has 300+ trade history, knows its edge
- **Evolution**: Personal trading style emerges from data

## 🎯 Pattern Trading Priority

Start with these patterns IN ORDER:

### Phase 1 (Weeks 1-4):
1. **Basic Order Blocks** - Simplest to code
2. **Market Structure** - HH/HL/LH/LL tracking

### Phase 2 (Weeks 5-6):
3. **Breaker Blocks** - Failed OBs (high win rate)
4. **Liquidity Sweeps** - Stop hunts

### Phase 3 (Weeks 7-8):
5. **Inducement Patterns** - Liquidity traps
6. **Fair Value Gaps** - With displacement only
7. **ChoCH vs BOS** - Trend changes

## 📈 Performance Optimization Tips (With Self-Learning)

1. **Start Conservative**
   - 5-8 MGC positions (learning system will adjust)
   - Only order blocks (until proven profitable)
   - 1 trade per day (bot will learn optimal frequency)

2. **Scale Gradually**
   - Learning system adds patterns automatically when ready
   - Position size increases with proven performance
   - Win rate improves through pattern filtering

3. **Track Everything**
   - Bot automatically logs every signal
   - Learning system discovers why trades win/lose
   - Conditions that improve win rate are identified

4. **Self-Learning Benefits**
   - **Month 1**: Bot discovers "Order blocks work 65% in NY session"
   - **Month 2**: Position size increases from 5 to 10 MGC based on performance
   - **Month 3**: Bot disables patterns with <40% win rate automatically
   - **Ongoing**: Personal trading style emerges from data

5. **Learning System Insights**
   - Weekly reports show which patterns are improving
   - Toxic market conditions automatically avoided
   - Position sizing adapts to recent performance
   - No manual optimization needed - bot learns continuously

6. **Continuous Improvement**
   - Weekly performance reviews
   - Adjust parameters based on data
   - Never change multiple things at once

## 🚀 Getting Started (For Real)

### Day 1:
```bash
# Setup
mkdir gold-bot && cd gold-bot
python -m venv venv
source venv/bin/activate

# Install only what we need
pip install ccxt websockets pandas jupyter asyncio
```

### Day 2-3:
- Write broker.py (just connection and orders)
- Test with paper account
- Make sure orders work

### Day 4-7:
- Add basic order block detection
- Paper trade manually first
- Verify patterns are correct

### Week 2:
- Automate the basic strategy
- Log everything
- Run for full sessions

## 📈 Success Metrics

### Week 4 Checkpoint:
- [ ] 20+ trades executed
- [ ] No system crashes
- [ ] All trades logged
- [ ] Risk rules work
- [ ] Basic strategy profitable?

### Week 8 Checkpoint:
- [ ] 100+ trades completed
- [ ] 48%+ win rate
- [ ] Positive expectancy
- [ ] Enhanced patterns working
- [ ] Ready for small live trading

## 🚀 Future Phases (After Profitable)

### Phase 4: Complete SMC Implementation (Months 3-4)
Once basic patterns are consistently profitable, add:

**Advanced Patterns**:
- **Mitigation Blocks** - Institutional loss recovery zones
- **Power of 3** - Accumulation → Manipulation → Distribution
- **Judas Swing** - London fake-out patterns
- **Optimal Trade Entry (OTE)** - 62-79% Fibonacci zones

**Correlation Suite**:
- **Real-time DXY monitoring** - Automated bias adjustment
- **10Y Treasury yields** - Risk-on/off detection
- **Silver divergence** - Precious metals confirmation
- **VIX integration** - Volatility filtering

### Phase 5: Multi-Timeframe Mastery (Months 5-6)
- **Weekly/Daily** - Major liquidity draws
- **4H** - Institutional positioning
- **1H** - Trend structure
- **15M** - Entry precision
- **5M** - Fine-tuning (optional)

### Phase 6: Advanced Features (Month 6+)
**Risk Management 2.0**:
- Dynamic position sizing based on pattern quality
- Correlation-based exposure limits
- Volatility-adjusted targets
- Monte Carlo risk modeling

**Performance Analytics**:
- Pattern success rates by market condition
- Time-of-day optimization
- Seasonal adjustments for gold
- A/B testing framework

**Automation Enhancement**:
- Multi-broker support
- Cloud deployment (after funded)
- Mobile alerts and control
- Emergency protocols

**Professional Monitoring**:
- Terminal dashboard using 'rich' library
- Real-time charts in terminal
- SSH access from anywhere
- Tmux/screen for persistent sessions

### Phase 7: Scaling to Multiple Instruments
Once gold is mastered:
- **Silver (SI)** - Similar SMC patterns
- **Crude Oil (CL)** - Energy sector
- **S&P 500 (ES)** - Index futures
- **Euro (6E)** - Forex futures

## 💡 Key Principles

1. **One Pattern at a Time** - Master OBs before adding anything
2. **Risk First** - Better to miss trades than blow account
3. **Log Everything** - You need data to improve
4. **Paper Trade Longer** - At least 100 trades before live
5. **Start Small** - 5 MGC is fine for first month

## 🎓 Why This Plan Works

- **Actually achievable** in 8-10 weeks part-time
- **Focuses on what matters** (execution > complexity)
- **Progressive difficulty** (basic → enhanced → advanced)
- **Risk management first** (survive to thrive)
- **Real monitoring** via JSON files
- **Clear upgrade path** once profitable

## 🚫 What We're NOT Doing (Initially)

- Building complex ML models
- Creating web dashboards
- Optimizing prematurely
- Trading every pattern
- Assuming anything works

## 📊 Complete Timeline

### Foundation (Now - Week 10):
- **Week 1-2**: Basic infrastructure ✓
- **Week 3-4**: Simple strategy working ✓
- **Week 5-6**: Risk management & learning ✓
- **Week 7-8**: Enhanced patterns ✓
- **Week 9-10**: Polish and verify ✓

### Growth (Months 3-6):
- **Month 3**: Small live trading + advanced patterns
- **Month 4**: Full SMC implementation
- **Month 5**: Multi-timeframe mastery
- **Month 6**: Performance optimization

### Scaling (Month 6+):
- Add instruments
- Increase position sizes
- Deploy to cloud
- Build team/community

## 📝 Final Thoughts on Planning

### Why 10 Weeks Instead of 8?
- **Weeks 1-2 often have surprises** (API documentation gaps, authentication quirks)
- **Pattern detection is iterative** (you'll refine algorithms multiple times)
- **Risk management needs perfection** (one bug here = blown account)
- **Testing reveals issues** (always budget time for fixes)

### Signs You're On Track:
- Each component works independently before integration
- You understand every line of code
- Logs clearly show what's happening
- Paper trading shows consistent behavior
- You can explain the strategy to someone else
- Learning system shows improving win rates
- Position sizes increasing automatically
- Bot identifying profitable conditions

### Signs to Slow Down:
- "It mostly works" (it doesn't)
- Skipping tests to save time
- Adding features before basics work
- Negative paper trading results
- Confusion about why trades happen
- Learning system disabling most patterns
- Win rate declining over time
- Bot stuck on minimum position size

### The Reality:
Most traders spend months building bots that don't work. This plan, even at 10-12 weeks, is aggressive but achievable because it focuses on what matters: **a simple strategy executed reliably**.

### Self-Learning Evolution Timeline:

**Trades 1-20: Discovery Phase**
- Bot tries all patterns equally
- Logs every condition present
- Position size: minimum (2-5 MGC)
- Learning what works in YOUR trading

**Trades 21-50: Optimization Phase**
- Patterns with <40% win rate disabled
- Winning conditions identified
- Position size: adjusted by performance (5-8 MGC)
- Personal trading style emerging

**Trades 51-100: Confidence Phase**  
- Only proven patterns remain active
- Toxic conditions automatically avoided
- Position size: confident sizing (8-12 MGC)
- Consistent profitability expected

**Trades 100+: Mastery Phase**
- Bot has deep understanding of what works
- New patterns only added if they prove value
- Position size: maximum when confident (12-15 MGC)
- Your personal edge encoded in data

---

**Remember**: The goal is a WORKING bot that makes money, not a perfect bot that never ships. Start simple, prove it works, then enhance systematically.

**Final Reality Check**: If you can't get basic order blocks working profitably in paper trading, adding breaker blocks won't save you. Master the basics first, but know that the full SMC arsenal awaits once you prove the foundation works.

**This complete plan provides everything needed to build a working Gold Futures trading bot with self-learning capabilities. The bot will start simple and evolve based on real results, creating a personalized trading system that improves continuously. Follow it step by step, test thoroughly, and only move forward when each phase is working correctly. And remember - the plan will evolve as you build. That's not failure, that's learning.**