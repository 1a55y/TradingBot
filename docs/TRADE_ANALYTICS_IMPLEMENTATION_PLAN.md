# Trade Analytics and Performance Metrics Implementation Plan

## Overview
Implement comprehensive trade analytics system for Blue2.0 to enable self-learning capabilities and performance optimization.

## Current State Analysis
### Existing Infrastructure
- ✅ Basic trade logging in JSON format
- ✅ Simple win rate calculation
- ✅ Daily trade summaries
- ✅ Trade execution details logging
- ✅ Real-time status monitoring

### Missing Components
- ❌ Advanced metrics (Profit Factor, Sharpe Ratio, Max Drawdown)
- ❌ Pattern-specific performance tracking
- ❌ Historical performance database
- ❌ Self-learning system integration
- ❌ Risk-adjusted metrics
- ❌ Performance optimization feedback loop

## Implementation Plan

### Phase 1: Core Analytics Engine (Week 1)
1. **Create Analytics Module** (`src/analytics/`)
   - `performance_tracker.py` - Main analytics engine
   - `metrics_calculator.py` - Advanced metrics calculations
   - `pattern_analyzer.py` - Pattern-specific performance
   - `risk_analyzer.py` - Risk metrics and drawdown

2. **Implement Key Metrics**
   ```python
   # Core metrics to implement
   - Win Rate (existing, enhance)
   - Profit Factor = Gross Profit / Gross Loss
   - Sharpe Ratio = (Returns - Risk Free Rate) / Std Dev
   - Maximum Drawdown (peak to trough)
   - Average R-Multiple
   - Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
   - Recovery Factor = Net Profit / Max Drawdown
   ```

3. **Database Schema** (SQLite)
   ```sql
   -- trades table
   CREATE TABLE trades (
       id TEXT PRIMARY KEY,
       timestamp DATETIME,
       contract TEXT,
       side TEXT,
       entry_price REAL,
       exit_price REAL,
       quantity INTEGER,
       pnl REAL,
       r_multiple REAL,
       pattern_type TEXT,
       pattern_score REAL,
       timeframes_aligned TEXT,
       max_adverse_excursion REAL,
       max_favorable_excursion REAL,
       duration_minutes REAL
   );
   
   -- pattern_performance table
   CREATE TABLE pattern_performance (
       pattern_type TEXT,
       timeframe TEXT,
       total_trades INTEGER,
       win_rate REAL,
       avg_r_multiple REAL,
       profit_factor REAL,
       last_updated DATETIME
   );
   
   -- daily_metrics table
   CREATE TABLE daily_metrics (
       date DATE PRIMARY KEY,
       total_trades INTEGER,
       win_rate REAL,
       profit_factor REAL,
       sharpe_ratio REAL,
       max_drawdown REAL,
       total_pnl REAL
   );
   ```

### Phase 2: Self-Learning Integration (Week 2)
1. **Pattern Performance Tracking**
   - Track success rate by pattern type
   - Monitor performance by timeframe
   - Identify best/worst performing patterns
   - Auto-adjust pattern minimum scores

2. **Dynamic Optimization**
   ```python
   class SelfLearningSystem:
       def update_pattern_weights(self):
           """Adjust pattern scores based on performance"""
           pass
           
       def optimize_position_sizing(self):
           """Kelly Criterion based position sizing"""
           pass
           
       def identify_edge_conditions(self):
           """Find market conditions where bot performs best"""
           pass
   ```

3. **Feedback Loop Implementation**
   - Real-time performance updates after each trade
   - Pattern score adjustments based on 20-trade rolling window
   - Position size optimization based on recent performance

### Phase 3: Reporting & Visualization (Week 3)
1. **Performance Reports**
   - Daily/Weekly/Monthly summaries
   - Pattern-specific reports
   - Risk analysis reports
   - CSV export functionality

2. **Terminal Dashboard** (using `rich` library)
   ```
   ╔══════════════════════════════════════════════════════╗
   ║                Blue2.0 Performance Dashboard          ║
   ╠══════════════════════════════════════════════════════╣
   ║ Today's Performance                                   ║
   ║ ├─ Trades: 12        Win Rate: 66.7%                ║
   ║ ├─ P&L: +$487.50     Profit Factor: 2.8             ║
   ║ └─ Max DD: -$125     Sharpe: 1.85                   ║
   ╠══════════════════════════════════════════════════════╣
   ║ Pattern Performance (Last 50 trades)                  ║
   ║ ├─ Order Blocks:     72% win rate, 2.1 avg R        ║
   ║ ├─ Support/Resist:   58% win rate, 1.8 avg R        ║
   ║ └─ Breaker Blocks:   N/A                             ║
   ╠══════════════════════════════════════════════════════╣
   ║ Risk Metrics                                          ║
   ║ ├─ Current DD: -2.5% Recovery Factor: 3.9           ║
   ║ └─ VaR (95%): $350   Risk per Trade: $250           ║
   ╚══════════════════════════════════════════════════════╝
   ```

## File Structure
```
src/
├── analytics/
│   ├── __init__.py
│   ├── performance_tracker.py      # Main analytics engine
│   ├── metrics_calculator.py       # Metric calculations
│   ├── pattern_analyzer.py         # Pattern performance
│   ├── risk_analyzer.py           # Risk metrics
│   └── database.py                # SQLite interface
├── learning/
│   ├── __init__.py
│   ├── self_learning_system.py    # Core learning logic
│   ├── pattern_optimizer.py       # Pattern weight adjustment
│   └── position_optimizer.py      # Position sizing optimization
└── reporting/
    ├── __init__.py
    ├── report_generator.py        # Report creation
    ├── dashboard.py               # Terminal UI
    └── export_manager.py          # CSV/JSON export

scripts/
├── analytics/
│   ├── generate_report.py         # Generate performance reports
│   ├── analyze_patterns.py        # Pattern analysis tool
│   └── backtest_analytics.py     # Backtest with analytics

tests/
├── test_analytics/
│   ├── test_metrics_calculator.py
│   ├── test_pattern_analyzer.py
│   └── test_self_learning.py
```

## Integration Points
1. **Bot Integration**
   - Hook into `_log_trade_execution()` in `bot_live.py`
   - Update after each trade completion
   - Use analytics for signal generation decisions

2. **Signal Generator Enhancement**
   - Use pattern performance data to adjust scores
   - Filter patterns based on recent performance
   - Dynamic threshold adjustment

3. **Risk Manager Updates**
   - Use drawdown data for position sizing
   - Implement performance-based risk limits
   - Add circuit breakers based on metrics

## Testing Strategy
1. **Unit Tests**
   - Test each metric calculation
   - Verify database operations
   - Test pattern analysis logic

2. **Integration Tests**
   - Test full trade lifecycle with analytics
   - Verify self-learning adjustments
   - Test report generation

3. **Performance Tests**
   - Ensure analytics don't slow trading
   - Test with 1000+ historical trades
   - Verify real-time update speed

## Success Metrics
- [ ] All metrics calculate correctly (verified against manual calculations)
- [ ] Pattern performance tracking improves win rate by 5%+
- [ ] Self-learning system reduces drawdowns by 10%+
- [ ] Reports generate in <1 second
- [ ] Database handles 10,000+ trades efficiently
- [ ] Real-time dashboard updates without lag

## Timeline
- **Week 1**: Core analytics engine + database
- **Week 2**: Self-learning integration + optimization
- **Week 3**: Reporting + dashboard + testing
- **Week 4**: Integration, testing, and refinement

## Next Steps
1. Create `src/analytics/` directory structure
2. Implement `metrics_calculator.py` with core calculations
3. Set up SQLite database with schema
4. Create basic performance tracking tests
5. Integrate with existing trade logging

This implementation will fulfill GitHub Issue #10 and enable Phase 2.5's self-learning capabilities.