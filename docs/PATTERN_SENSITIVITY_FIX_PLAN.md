# Pattern Detection Sensitivity Fix Implementation Plan
*GitHub Issue #7 - Priority: HIGH (Bug)*

## Problem Statement

The current pattern detection system has rigid, hardcoded sensitivity values that don't adapt to market conditions. This causes:
- Missed trading opportunities in low-volatility/ranging markets
- Potential false signals in high-volatility periods
- No adjustment for different trading sessions (Asian vs US)
- Fixed thresholds that don't learn from performance

## Root Causes

1. **Hardcoded Body Size Multiplier**: 1.5x average is too rigid
2. **Static Scoring System**: Doesn't adapt to market volatility
3. **Fixed MIN_PATTERN_SCORE**: 5-6 threshold doesn't adjust
4. **No Market Context**: Ignores overall market conditions
5. **Limited Pattern Types**: Only basic order blocks detected

## Solution Design

### 1. Dynamic Volatility-Based Sensitivity

```python
# src/indicators/market_context.py
class MarketContext:
    def calculate_volatility_regime(self, candles):
        """Determine if market is in low/normal/high volatility"""
        atr = self.calculate_atr(candles)
        historical_atr = self.get_historical_atr_percentile(atr)
        
        if historical_atr < 30:
            return "LOW", 0.7  # Reduce thresholds by 30%
        elif historical_atr > 70:
            return "HIGH", 1.3  # Increase thresholds by 30%
        else:
            return "NORMAL", 1.0
    
    def get_session_context(self):
        """Identify current trading session"""
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour < 7:  # Asian session
            return "ASIAN", 0.8  # More sensitive
        elif 7 <= current_hour < 15:  # European session
            return "EUROPEAN", 1.0
        else:  # US session
            return "US", 1.1  # Less sensitive due to higher volatility
```

### 2. Configurable Pattern Parameters

```python
# src/config.py additions
PATTERN_DETECTION = {
    'SENSITIVITY_MODE': 'ADAPTIVE',  # CONSERVATIVE, NORMAL, AGGRESSIVE, ADAPTIVE
    'BODY_SIZE_MULTIPLIER': {
        'CONSERVATIVE': 2.0,
        'NORMAL': 1.5,
        'AGGRESSIVE': 1.2,
        'ADAPTIVE': None  # Calculated dynamically
    },
    'MIN_PATTERN_SCORE_ADJUSTMENT': {
        'LOW_VOLATILITY': -1,    # Reduce minimum score by 1
        'NORMAL_VOLATILITY': 0,   # No adjustment
        'HIGH_VOLATILITY': +1     # Increase minimum score by 1
    },
    'ENABLE_ADVANCED_PATTERNS': True,  # FVG, Breaker blocks, etc.
    'PATTERN_PERFORMANCE_WINDOW': 50,  # Last 50 trades for performance tracking
}
```

### 3. Enhanced Pattern Scoring

```python
# src/core/signal_generator.py modifications
def calculate_pattern_score(self, pattern, market_context):
    base_score = self._calculate_base_score(pattern)
    
    # Market context adjustments
    volatility_adjustment = market_context.get_volatility_adjustment()
    session_adjustment = market_context.get_session_adjustment()
    
    # Performance-based adjustment
    pattern_performance = self.analytics.get_pattern_performance(
        pattern.type, 
        timeframe=pattern.timeframe
    )
    performance_adjustment = self._calculate_performance_adjustment(pattern_performance)
    
    # Confidence scoring instead of binary pass/fail
    confidence = (base_score * volatility_adjustment * 
                 session_adjustment * performance_adjustment)
    
    return {
        'score': base_score,
        'adjusted_score': confidence,
        'confidence_level': self._get_confidence_level(confidence),
        'adjustments': {
            'volatility': volatility_adjustment,
            'session': session_adjustment,
            'performance': performance_adjustment
        }
    }
```

### 4. Additional Pattern Types

```python
# src/indicators/advanced_patterns.py
class AdvancedPatterns:
    def find_fair_value_gaps(self, candles):
        """Detect FVG (imbalance) patterns"""
        pass
    
    def find_breaker_blocks(self, candles):
        """Detect breaker block patterns"""
        pass
    
    def find_liquidity_sweeps(self, candles):
        """Detect stop hunts and liquidity grabs"""
        pass
    
    def find_order_flow_imbalances(self, candles, volume_data):
        """Detect order flow imbalances"""
        pass
```

### 5. Pattern Performance Tracking Integration

```python
# src/learning/pattern_performance_tracker.py
class PatternPerformanceTracker:
    def __init__(self, analytics_db):
        self.db = analytics_db
        self.performance_cache = {}
    
    def update_pattern_performance(self, trade_result):
        """Update pattern success rates after trade completion"""
        pattern_type = trade_result['pattern_type']
        pattern_score = trade_result['pattern_score']
        success = trade_result['pnl'] > 0
        
        # Update database
        self.db.update_pattern_metrics(pattern_type, pattern_score, success)
        
        # Update cache for fast access
        self._update_performance_cache(pattern_type, pattern_score, success)
    
    def get_minimum_score_recommendation(self, pattern_type):
        """Recommend minimum score based on historical performance"""
        performance = self.db.get_pattern_performance_by_score(pattern_type)
        
        # Find score threshold with >55% win rate
        for score in range(10, 0, -1):
            if performance.get(score, {}).get('win_rate', 0) > 55:
                return score
        
        return 6  # Default fallback
```

## Implementation Steps

### Phase 1: Core Sensitivity Fix (2-3 days)
1. Implement MarketContext class
2. Add configurable pattern parameters
3. Modify pattern detection to use dynamic thresholds
4. Update signal generator with enhanced scoring

### Phase 2: Advanced Patterns (2 days)
1. Implement Fair Value Gap detection
2. Add Breaker Block patterns
3. Integrate with existing pattern system

### Phase 3: Performance Integration (1-2 days)
1. Connect pattern performance tracker
2. Implement auto-adjustment logic
3. Add performance-based filtering

### Phase 4: Testing & Tuning (2 days)
1. Unit tests for new components
2. Integration tests with historical data
3. Parameter tuning based on backtest results
4. Live testing with paper trading

## Success Metrics

1. **Pattern Detection Rate**: Increase from current ~5-10 patterns/day to 15-25
2. **False Positive Rate**: Keep below 20%
3. **Adaptability**: Successful pattern detection across all market conditions
4. **Win Rate Impact**: Improve overall win rate by 5-10%
5. **Self-Learning**: Automatic threshold adjustment based on performance

## Risk Mitigation

1. **Gradual Rollout**: Test each sensitivity mode separately
2. **Override Controls**: Manual sensitivity adjustment option
3. **Performance Monitoring**: Real-time pattern success tracking
4. **Fallback Mode**: Revert to conservative settings if performance degrades

## Configuration Examples

```python
# Conservative mode for uncertain markets
PATTERN_DETECTION['SENSITIVITY_MODE'] = 'CONSERVATIVE'

# Aggressive mode for trending markets
PATTERN_DETECTION['SENSITIVITY_MODE'] = 'AGGRESSIVE'

# Adaptive mode for self-adjusting (recommended)
PATTERN_DETECTION['SENSITIVITY_MODE'] = 'ADAPTIVE'
```

## Next Steps

1. Create feature branch: `fix/pattern-sensitivity-issue-7`
2. Implement MarketContext class
3. Add configuration options
4. Modify pattern detection logic
5. Test with historical data
6. Deploy to paper trading

This fix will significantly improve the bot's ability to detect valid trading opportunities across different market conditions, directly addressing the GitHub Issue #7 bug while also enabling better data collection for the self-learning system (Issue #10).