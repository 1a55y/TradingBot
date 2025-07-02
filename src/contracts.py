"""Contract Registry for Trading Bot"""
# Standard library imports
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ContractSpec:
    """Contract specification with all necessary parameters"""
    symbol: str  # Base symbol
    full_symbol: str  # Current active contract
    contract_id: str  # TopStepX contract ID
    tick_size: float  # Minimum price movement
    tick_value: float  # Dollar value per tick
    volatility: float  # Relative volatility (1.0 = baseline)
    min_position: int  # Minimum position size
    max_position: int  # Maximum position size
    default_position: int  # Default position size
    min_stop_ticks: int  # Minimum stop loss in ticks
    max_stop_ticks: int  # Maximum stop loss in ticks
    default_stop_ticks: int  # Default stop loss in ticks
    min_ob_move_ticks: int  # Minimum order block displacement
    min_pattern_score: float  # Minimum pattern detection score
    min_volume_ratio: float  # Minimum volume ratio for patterns
    primary_timeframe: str  # Primary analysis timeframe
    htf_timeframe: str  # Higher timeframe for trend
    entry_timeframe: str  # Entry timing timeframe


# Contract Registry
CONTRACTS: Dict[str, ContractSpec] = {
    # Micro E-mini Nasdaq (High volatility tech index)
    'MNQ': ContractSpec(
        symbol='MNQ',
        full_symbol='MNQU25',
        contract_id='CON.F.US.MNQ.U25',
        tick_size=0.25,
        tick_value=0.50,
        volatility=1.5,  # High volatility
        min_position=2,
        max_position=50,
        default_position=2,
        min_stop_ticks=40,
        max_stop_ticks=200,
        default_stop_ticks=60,
        min_ob_move_ticks=20,
        min_pattern_score=5,
        min_volume_ratio=1.2,
        primary_timeframe='5m',
        htf_timeframe='15m',
        entry_timeframe='1m'
    ),
    
    # Standard E-mini Nasdaq
    'NQ': ContractSpec(
        symbol='NQ',
        full_symbol='NQU25',
        contract_id='CON.F.US.NQ.U25',
        tick_size=0.25,
        tick_value=5.0,
        volatility=1.5,  # High volatility
        min_position=1,
        max_position=10,
        default_position=1,
        min_stop_ticks=40,
        max_stop_ticks=200,
        default_stop_ticks=60,
        min_ob_move_ticks=20,
        min_pattern_score=5,
        min_volume_ratio=1.2,
        primary_timeframe='5m',
        htf_timeframe='15m',
        entry_timeframe='1m'
    ),
    
    # Micro E-mini S&P 500 (Lower volatility broad index)
    'MES': ContractSpec(
        symbol='MES',
        full_symbol='MESU25',
        contract_id='CON.F.US.MES.U25',
        tick_size=0.25,
        tick_value=1.25,
        volatility=1.0,  # Baseline volatility
        min_position=3,
        max_position=50,
        default_position=3,
        min_stop_ticks=20,
        max_stop_ticks=100,
        default_stop_ticks=40,
        min_ob_move_ticks=15,
        min_pattern_score=6,
        min_volume_ratio=1.5,
        primary_timeframe='15m',
        htf_timeframe='1h',
        entry_timeframe='5m'
    ),
    
    # Standard E-mini S&P 500
    'ES': ContractSpec(
        symbol='ES',
        full_symbol='ESU25',
        contract_id='CON.F.US.ES.U25',
        tick_size=0.25,
        tick_value=12.50,
        volatility=1.0,  # Baseline volatility
        min_position=1,
        max_position=10,
        default_position=1,
        min_stop_ticks=20,
        max_stop_ticks=100,
        default_stop_ticks=40,
        min_ob_move_ticks=15,
        min_pattern_score=6,
        min_volume_ratio=1.5,
        primary_timeframe='15m',
        htf_timeframe='1h',
        entry_timeframe='5m'
    ),
    
    # Micro Gold Futures (Commodity with moderate volatility)
    'MGC': ContractSpec(
        symbol='MGC',
        full_symbol='MGCM25',
        contract_id='CON.F.US.MGC.M25',
        tick_size=0.10,
        tick_value=1.0,
        volatility=1.2,  # Moderate volatility
        min_position=2,
        max_position=30,
        default_position=2,
        min_stop_ticks=30,
        max_stop_ticks=150,
        default_stop_ticks=50,
        min_ob_move_ticks=20,
        min_pattern_score=5.5,
        min_volume_ratio=1.3,
        primary_timeframe='15m',
        htf_timeframe='1h',
        entry_timeframe='5m'
    ),
    
    # Standard Gold Futures
    'GC': ContractSpec(
        symbol='GC',
        full_symbol='GCM25',
        contract_id='CON.F.US.GC.M25',
        tick_size=0.10,
        tick_value=10.0,
        volatility=1.2,  # Moderate volatility
        min_position=1,
        max_position=5,
        default_position=1,
        min_stop_ticks=30,
        max_stop_ticks=150,
        default_stop_ticks=50,
        min_ob_move_ticks=20,
        min_pattern_score=5.5,
        min_volume_ratio=1.3,
        primary_timeframe='15m',
        htf_timeframe='1h',
        entry_timeframe='5m'
    )
}


def get_contract(symbol: str) -> ContractSpec:
    """Get contract specification by symbol"""
    if symbol not in CONTRACTS:
        raise ValueError(f"Unknown contract symbol: {symbol}")
    return CONTRACTS[symbol]


def calculate_position_size(contract: ContractSpec, account_balance: float, risk_per_trade: float) -> int:
    """Calculate position size based on contract and risk parameters"""
    # Calculate maximum position based on risk
    risk_position = int(risk_per_trade / (contract.default_stop_ticks * contract.tick_value))
    
    # Apply contract limits
    position_size = max(contract.min_position, min(risk_position, contract.max_position))
    
    # Adjust for high volatility contracts
    if contract.volatility > 1.3:
        position_size = max(contract.min_position, int(position_size * 0.8))
    
    return position_size


def adjust_pattern_parameters(contract: ContractSpec) -> Dict[str, Any]:
    """Adjust pattern detection parameters based on contract volatility"""
    base_lookback = 100
    
    # High volatility contracts need shorter lookback
    if contract.volatility > 1.3:
        lookback = int(base_lookback * 0.8)
    # Low volatility contracts benefit from longer lookback
    elif contract.volatility < 1.0:
        lookback = int(base_lookback * 1.2)
    else:
        lookback = base_lookback
    
    return {
        'lookback_candles': lookback,
        'min_pattern_score': contract.min_pattern_score,
        'min_volume_ratio': contract.min_volume_ratio,
        'min_ob_move_ticks': contract.min_ob_move_ticks,
        'pattern_violation_tolerance': 0.002 * contract.volatility
    }


# Export all necessary items
__all__ = ['CONTRACTS', 'ContractSpec', 'get_contract', 'calculate_position_size', 'adjust_pattern_parameters']