"""Market context analyzer for dynamic pattern sensitivity."""
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)


class MarketContext:
    """Analyzes market conditions for dynamic pattern sensitivity."""
    
    def __init__(self):
        self.atr_history = []
        self.volatility_window = 20
    
    def calculate_atr(self, candles: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(candles) < period + 1:
            return 0.0
        
        high_low = [abs(c['high'] - c['low']) for c in candles]
        high_close = [abs(c['high'] - candles[i-1]['close']) for i, c in enumerate(candles[1:], 1)]
        low_close = [abs(c['low'] - candles[i-1]['close']) for i, c in enumerate(candles[1:], 1)]
        
        true_ranges = []
        for i in range(1, len(candles)):
            tr = max(
                high_low[i],
                high_close[i-1] if i-1 < len(high_close) else 0,
                low_close[i-1] if i-1 < len(low_close) else 0
            )
            true_ranges.append(tr)
        
        if len(true_ranges) >= period:
            return np.mean(true_ranges[-period:])
        return 0.0
    
    def get_volatility_regime(self, current_atr: float, historical_atr: List[float]) -> Tuple[str, float]:
        """Determine volatility regime and adjustment factor."""
        if not historical_atr or len(historical_atr) < 20:
            return "NORMAL", 1.0
        
        # Calculate percentile of current ATR
        percentile = np.percentile(historical_atr, [30, 70])
        
        if current_atr < percentile[0]:
            # Low volatility - be more sensitive
            return "LOW", 0.7  # Reduce thresholds by 30%
        elif current_atr > percentile[1]:
            # High volatility - be less sensitive
            return "HIGH", 1.3  # Increase thresholds by 30%
        else:
            return "NORMAL", 1.0
    
    def get_session_adjustment(self) -> Tuple[str, float]:
        """Get trading session and sensitivity adjustment."""
        current_hour = datetime.now().hour
        
        # Asian session (10 PM - 7 AM)
        if current_hour >= 22 or current_hour < 7:
            return "ASIAN", 0.8  # More sensitive in quiet session
        # European session (7 AM - 3 PM)
        elif 7 <= current_hour < 15:
            return "EUROPEAN", 1.0
        # US session (3 PM - 10 PM)
        else:
            return "US", 1.1  # Less sensitive in volatile session
    
    def analyze_market(self, candles: List[Dict]) -> Dict:
        """Comprehensive market analysis for pattern detection."""
        if not candles or len(candles) < 20:
            return {
                'volatility_regime': 'NORMAL',
                'volatility_adjustment': 1.0,
                'session': 'UNKNOWN',
                'session_adjustment': 1.0,
                'atr': 0.0,
                'trend': 'NEUTRAL',
                'recommendation': 'Use default settings'
            }
        
        # Calculate ATR
        current_atr = self.calculate_atr(candles)
        self.atr_history.append(current_atr)
        
        # Keep only recent history
        if len(self.atr_history) > 100:
            self.atr_history = self.atr_history[-100:]
        
        # Get volatility regime
        vol_regime, vol_adjustment = self.get_volatility_regime(current_atr, self.atr_history)
        
        # Get session info
        session, session_adjustment = self.get_session_adjustment()
        
        # Calculate trend
        sma_20 = np.mean([c['close'] for c in candles[-20:]])
        sma_50 = np.mean([c['close'] for c in candles[-50:]]) if len(candles) >= 50 else sma_20
        current_price = candles[-1]['close']
        
        if current_price > sma_20 > sma_50:
            trend = "BULLISH"
        elif current_price < sma_20 < sma_50:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"
        
        # Combined adjustment
        total_adjustment = vol_adjustment * session_adjustment
        
        # Recommendation
        if total_adjustment < 0.8:
            recommendation = "Market quiet - using sensitive pattern detection"
        elif total_adjustment > 1.2:
            recommendation = "Market volatile - using conservative pattern detection"
        else:
            recommendation = "Normal market conditions"
        
        return {
            'volatility_regime': vol_regime,
            'volatility_adjustment': vol_adjustment,
            'session': session,
            'session_adjustment': session_adjustment,
            'total_adjustment': total_adjustment,
            'atr': current_atr,
            'trend': trend,
            'recommendation': recommendation
        }
    
    def get_dynamic_thresholds(self, base_config: Dict, market_analysis: Dict) -> Dict:
        """Calculate dynamic thresholds based on market conditions."""
        adjustment = market_analysis['total_adjustment']
        
        return {
            'min_pattern_score': max(3, int(base_config['min_pattern_score'] * adjustment)),
            'min_body_size_multiplier': max(1.0, base_config.get('body_size_multiplier', 1.5) * adjustment),
            'min_volume_ratio': max(1.0, base_config['min_volume_ratio'] * adjustment),
            'min_ob_move_ticks': max(5, int(base_config['min_ob_move_ticks'] * adjustment)),
            'pattern_violation_tolerance': base_config['pattern_violation_tolerance'] * adjustment
        }