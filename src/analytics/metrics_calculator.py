"""
Core metrics calculator for trading performance analysis.
Implements key performance indicators for the Blue2.0 trading bot.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate trading performance metrics."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize metrics calculator.
        
        Args:
            risk_free_rate: Annual risk-free rate for Sharpe ratio calculation (default 2%)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """
        Calculate win rate percentage.
        
        Args:
            trades: List of trade dictionaries with 'pnl' field
            
        Returns:
            Win rate as percentage (0-100)
        """
        if not trades:
            return 0.0
            
        winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
        return (winning_trades / len(trades)) * 100
    
    def calculate_profit_factor(self, trades: List[Dict]) -> float:
        """
        Calculate profit factor (gross profit / gross loss).
        
        Args:
            trades: List of trade dictionaries with 'pnl' field
            
        Returns:
            Profit factor ratio
        """
        if not trades:
            return 0.0
            
        gross_profit = sum(trade['pnl'] for trade in trades if trade.get('pnl', 0) > 0)
        gross_loss = abs(sum(trade['pnl'] for trade in trades if trade.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
            
        return gross_profit / gross_loss
    
    def calculate_sharpe_ratio(self, returns: List[float], period: str = 'daily') -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: List of returns (as decimals, not percentages)
            period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Annualized Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
            
        # Annualization factors
        annualization_factors = {
            'daily': 252,    # Trading days per year
            'weekly': 52,
            'monthly': 12
        }
        
        factor = annualization_factors.get(period, 252)
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array, ddof=1)  # Sample standard deviation
        
        if std_return == 0:
            return 0.0
            
        # Annualize returns and calculate Sharpe
        annualized_return = mean_return * factor
        annualized_std = std_return * np.sqrt(factor)
        
        return (annualized_return - self.risk_free_rate) / annualized_std
    
    def calculate_maximum_drawdown(self, equity_curve: List[float]) -> Tuple[float, int, int]:
        """
        Calculate maximum drawdown and locations.
        
        Args:
            equity_curve: List of equity values over time
            
        Returns:
            Tuple of (max_drawdown_percentage, peak_index, trough_index)
        """
        if not equity_curve or len(equity_curve) < 2:
            return 0.0, 0, 0
            
        equity_array = np.array(equity_curve)
        cumulative_returns = equity_array / equity_array[0] - 1
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / (1 + running_max)
        
        max_dd_index = np.argmin(drawdown)
        max_dd = drawdown[max_dd_index]
        
        # Find the peak before the maximum drawdown
        peak_index = np.argmax(equity_array[:max_dd_index + 1])
        
        return abs(max_dd) * 100, peak_index, max_dd_index
    
    def calculate_average_r_multiple(self, trades: List[Dict]) -> float:
        """
        Calculate average R-multiple (risk-adjusted returns).
        
        Args:
            trades: List of trades with 'pnl' and 'risk_amount' fields
            
        Returns:
            Average R-multiple
        """
        if not trades:
            return 0.0
            
        r_multiples = []
        for trade in trades:
            risk = trade.get('risk_amount', 0)
            pnl = trade.get('pnl', 0)
            
            if risk > 0:
                r_multiples.append(pnl / risk)
        
        return np.mean(r_multiples) if r_multiples else 0.0
    
    def calculate_expectancy(self, trades: List[Dict]) -> float:
        """
        Calculate expectancy (average profit per trade).
        
        Formula: (Win% × Avg Win) - (Loss% × Avg Loss)
        
        Args:
            trades: List of trades with 'pnl' field
            
        Returns:
            Expectancy value
        """
        if not trades:
            return 0.0
            
        winners = [t['pnl'] for t in trades if t.get('pnl', 0) > 0]
        losers = [abs(t['pnl']) for t in trades if t.get('pnl', 0) < 0]
        
        if not winners and not losers:
            return 0.0
            
        win_rate = len(winners) / len(trades)
        loss_rate = len(losers) / len(trades)
        
        avg_win = np.mean(winners) if winners else 0
        avg_loss = np.mean(losers) if losers else 0
        
        return (win_rate * avg_win) - (loss_rate * avg_loss)
    
    def calculate_recovery_factor(self, total_profit: float, max_drawdown: float) -> float:
        """
        Calculate recovery factor (net profit / max drawdown).
        
        Args:
            total_profit: Total net profit
            max_drawdown: Maximum drawdown (as positive value)
            
        Returns:
            Recovery factor
        """
        if max_drawdown == 0:
            return float('inf') if total_profit > 0 else 0.0
            
        return total_profit / max_drawdown
    
    def calculate_calmar_ratio(self, annual_return: float, max_drawdown: float) -> float:
        """
        Calculate Calmar ratio (annual return / max drawdown).
        
        Args:
            annual_return: Annualized return percentage
            max_drawdown: Maximum drawdown percentage
            
        Returns:
            Calmar ratio
        """
        if max_drawdown == 0:
            return float('inf') if annual_return > 0 else 0.0
            
        return annual_return / max_drawdown
    
    def calculate_sortino_ratio(self, returns: List[float], target_return: float = 0) -> float:
        """
        Calculate Sortino ratio (like Sharpe but only considers downside volatility).
        
        Args:
            returns: List of returns
            target_return: Minimum acceptable return
            
        Returns:
            Sortino ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
            
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        
        # Calculate downside deviation
        downside_returns = returns_array[returns_array < target_return]
        
        if len(downside_returns) == 0:
            return float('inf')  # No downside risk
            
        downside_std = np.std(downside_returns, ddof=1)
        
        if downside_std == 0:
            return 0.0
            
        # Annualize (assuming daily returns)
        annualized_return = mean_return * 252
        annualized_downside_std = downside_std * np.sqrt(252)
        
        return (annualized_return - self.risk_free_rate) / annualized_downside_std
    
    def calculate_pattern_metrics(self, trades: List[Dict], pattern_type: str) -> Dict:
        """
        Calculate metrics for a specific pattern type.
        
        Args:
            trades: List of all trades
            pattern_type: Pattern to analyze
            
        Returns:
            Dictionary of pattern-specific metrics
        """
        pattern_trades = [t for t in trades if t.get('pattern_type') == pattern_type]
        
        if not pattern_trades:
            return {
                'pattern_type': pattern_type,
                'total_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_r_multiple': 0.0,
                'total_pnl': 0.0
            }
        
        return {
            'pattern_type': pattern_type,
            'total_trades': len(pattern_trades),
            'win_rate': self.calculate_win_rate(pattern_trades),
            'profit_factor': self.calculate_profit_factor(pattern_trades),
            'avg_r_multiple': self.calculate_average_r_multiple(pattern_trades),
            'total_pnl': sum(t.get('pnl', 0) for t in pattern_trades)
        }
    
    def calculate_timeframe_metrics(self, trades: List[Dict]) -> Dict[str, Dict]:
        """
        Calculate metrics grouped by primary timeframe.
        
        Args:
            trades: List of trades
            
        Returns:
            Dictionary of metrics by timeframe
        """
        timeframe_metrics = {}
        
        # Group trades by primary timeframe
        for trade in trades:
            timeframes = trade.get('timeframes_aligned', [])
            if timeframes and isinstance(timeframes, list):
                primary_tf = timeframes[0]  # Assume first is primary
                
                if primary_tf not in timeframe_metrics:
                    timeframe_metrics[primary_tf] = []
                    
                timeframe_metrics[primary_tf].append(trade)
        
        # Calculate metrics for each timeframe
        results = {}
        for tf, tf_trades in timeframe_metrics.items():
            results[tf] = {
                'total_trades': len(tf_trades),
                'win_rate': self.calculate_win_rate(tf_trades),
                'profit_factor': self.calculate_profit_factor(tf_trades),
                'avg_pnl': np.mean([t.get('pnl', 0) for t in tf_trades])
            }
        
        return results
    
    def calculate_daily_metrics(self, trades: List[Dict], equity_curve: List[float]) -> Dict:
        """
        Calculate comprehensive daily metrics.
        
        Args:
            trades: List of today's trades
            equity_curve: Equity values throughout the day
            
        Returns:
            Dictionary of daily metrics
        """
        if not trades:
            return {
                'date': datetime.now().date().isoformat(),
                'total_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_pnl': 0.0,
                'expectancy': 0.0,
                'avg_r_multiple': 0.0
            }
        
        # Calculate returns for Sharpe ratio
        if len(equity_curve) > 1:
            returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] 
                      for i in range(1, len(equity_curve))]
        else:
            returns = []
        
        max_dd, _, _ = self.calculate_maximum_drawdown(equity_curve)
        
        return {
            'date': datetime.now().date().isoformat(),
            'total_trades': len(trades),
            'win_rate': self.calculate_win_rate(trades),
            'profit_factor': self.calculate_profit_factor(trades),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns) if returns else 0.0,
            'max_drawdown': max_dd,
            'total_pnl': sum(t.get('pnl', 0) for t in trades),
            'expectancy': self.calculate_expectancy(trades),
            'avg_r_multiple': self.calculate_average_r_multiple(trades),
            'best_trade': max((t.get('pnl', 0) for t in trades), default=0),
            'worst_trade': min((t.get('pnl', 0) for t in trades), default=0),
            'avg_win': np.mean([t['pnl'] for t in trades if t.get('pnl', 0) > 0]) if any(t.get('pnl', 0) > 0 for t in trades) else 0,
            'avg_loss': np.mean([t['pnl'] for t in trades if t.get('pnl', 0) < 0]) if any(t.get('pnl', 0) < 0 for t in trades) else 0
        }