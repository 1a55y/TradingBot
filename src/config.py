"""Configuration settings for Multi-Contract Trading Bot"""
# Standard library imports
import os
from datetime import time
from typing import Dict, List

# Third-party imports
from dotenv import load_dotenv

# Local imports
from .contracts import CONTRACTS, adjust_pattern_parameters, calculate_position_size, get_contract

# Load environment variables
load_dotenv()

# Get the selected contract early to avoid initialization issues
_TRADING_CONTRACT = os.getenv('TRADING_CONTRACT', 'MNQ')
_selected_contract = get_contract(_TRADING_CONTRACT)

class Config:
    # API Settings
    TOPSTEP_API_KEY = os.getenv('TOPSTEP_API_KEY')
    TOPSTEP_API_SECRET = os.getenv('TOPSTEP_API_SECRET')
    TOPSTEP_USERNAME = os.getenv('TOPSTEP_USERNAME')
    TOPSTEP_USER_ID = os.getenv('TOPSTEP_USER_ID')
    TOPSTEP_ACCOUNT_ID = os.getenv('TOPSTEP_ACCOUNT_ID')
    TOPSTEP_MARKET = os.getenv('TOPSTEP_MARKET', 'CME_TOB')
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
    
    # Trading Contract Selection
    TRADING_CONTRACT = _TRADING_CONTRACT
    _contract = _selected_contract
    
    # Account IDs (from environment variables)
    STEP1_ACCOUNT_ID = int(os.getenv('TOPSTEP_STEP1_ACCOUNT_ID', '9203477'))  # Step 1 evaluation
    PRACTICE_ACCOUNT_ID = int(os.getenv('TOPSTEP_PRACTICE_ACCOUNT_ID', '9156522'))  # Practice account
    
    # API URLs
    TOPSTEP_API_BASE_URL = os.getenv('TOPSTEP_API_BASE_URL', 'https://api.topstepx.com')
    TOPSTEP_RTC_BASE_URL = os.getenv('TOPSTEP_RTC_BASE_URL', 'https://rtc.topstepx.com')
    TOPSTEP_WS_DATA_URL = os.getenv('TOPSTEP_WS_DATA_URL', 'wss://rtc.topstepx.com/hubs/market')
    TOPSTEP_WS_TRADING_URL = os.getenv('TOPSTEP_WS_TRADING_URL', 'wss://rtc.topstepx.com/hubs/user')
    
    # Contract Specifications (dynamically loaded from selected contract)
    SYMBOL = _selected_contract.symbol
    FULL_SYMBOL = _selected_contract.full_symbol
    CONTRACT_ID = _selected_contract.contract_id
    TICK_SIZE = _selected_contract.tick_size
    TICK_VALUE = _selected_contract.tick_value
    CONTRACT_VOLATILITY = _selected_contract.volatility
    CONTRACT_MONTHS = ['H', 'M', 'U', 'Z']  # Mar, Jun, Sep, Dec
    
    @classmethod
    def get_active_contract(cls) -> str:
        """Get the currently active contract symbol"""
        return cls.FULL_SYMBOL
    
    @classmethod
    def get_contract_id(cls) -> str:
        """Get the TopStepX contract ID"""
        return cls.CONTRACT_ID
    
    @classmethod
    def get_tick_value(cls) -> float:
        """Get tick value for current contract"""
        return cls.TICK_VALUE
    
    # Position Limits (dynamically loaded from selected contract)
    MAX_POSITION = _selected_contract.max_position
    MIN_POSITION = _selected_contract.min_position
    DEFAULT_POSITION = _selected_contract.default_position
    
    # Risk Parameters (TopStep Rules)
    DEFAULT_ACCOUNT_SIZE = float(os.getenv('DEFAULT_ACCOUNT_SIZE', '150000'))  # Default if API unavailable
    DAILY_LOSS_LIMIT = 800  # Hard stop
    TRAILING_DRAWDOWN = 2000  # TopStep trailing
    MAX_RISK_PER_TRADE = 500
    WARNING_RISK_PER_TRADE = 400  # Alert level
    MAX_CONSECUTIVE_LOSSES = 2
    
    # Trading Hours (Helsinki Time - EET/EEST)
    SESSION_START = time(2, 0)     # 2:00 AM
    SESSION_END = time(23, 0)      # 11:00 PM
    NEWS_BLACKOUT_START = time(22, 45)  # No new trades
    
    # Pattern Detection Settings (dynamically adjusted for contract volatility)
    _pattern_params = adjust_pattern_parameters(_selected_contract)
    MIN_PATTERN_SCORE = _pattern_params['min_pattern_score']
    LOOKBACK_CANDLES = _pattern_params['lookback_candles']
    MIN_VOLUME_RATIO = _pattern_params['min_volume_ratio']
    PATTERN_VIOLATION_TOLERANCE = _pattern_params['pattern_violation_tolerance']
    
    # Order Block Settings
    MIN_OB_MOVE_TICKS = _pattern_params['min_ob_move_ticks']
    MAX_OB_AGE_CANDLES = 50  # How old can OB be
    MIN_OB_TOUCHES = 1  # Before considering valid
    
    # Stop Loss Settings (dynamically loaded from selected contract)
    MIN_STOP_TICKS = _selected_contract.min_stop_ticks
    MAX_STOP_TICKS = _selected_contract.max_stop_ticks
    DEFAULT_STOP_TICKS = _selected_contract.default_stop_ticks
    ATR_STOP_MULTIPLIER = 1.5  # For volatility adjustment
    
    # Take Profit Settings
    TP1_RATIO = 1.0  # 1:1 (50% exit)
    TP2_RATIO = 2.0  # 1:2 (40% exit)
    RUNNER_RATIO = 2.5  # Max runner target
    
    # Timeframes (dynamically loaded from selected contract)
    PRIMARY_TIMEFRAME = _selected_contract.primary_timeframe
    HTF_TIMEFRAME = _selected_contract.htf_timeframe
    ENTRY_TIMEFRAME = _selected_contract.entry_timeframe
    ANALYSIS_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h']  # Extended multi-timeframe analysis
    
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
    
    # Pattern Detection Enhancements
    MAX_PATTERN_AGE_CANDLES = 50  # Don't trade patterns older than this
    
    
    # Timing Parameters
    SIGNAL_COOLDOWN_SECONDS = 300  # Wait 5 minutes after placing a trade
    MAIN_LOOP_DELAY_SECONDS = 30  # Main trading loop iteration delay
    MONITORING_UPDATE_INTERVAL = 30  # Update status files every 30 seconds
    
    # File Operation Parameters
    MAX_FILE_RETRY_ATTEMPTS = 3  # Retry file operations this many times
    FILE_RETRY_DELAY = 0.1  # Delay between file operation retries
    
    # Connection Parameters
    WEBSOCKET_HEARTBEAT_INTERVAL = 30  # Send heartbeat every 30 seconds
    WEBSOCKET_RECONNECT_DELAY = 1.0  # Initial reconnect delay
    WEBSOCKET_MAX_RECONNECT_DELAY = 300  # Max reconnect delay (5 minutes)
    CIRCUIT_BREAKER_THRESHOLD = 5  # Open circuit after 5 failures
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60  # Try again after 60 seconds
    
    @classmethod
    def calculate_dynamic_position_size(cls, account_balance: float = None) -> int:
        """Calculate position size based on contract and account balance"""
        # Use provided balance or default
        balance = account_balance if account_balance is not None else cls.DEFAULT_ACCOUNT_SIZE
        return calculate_position_size(cls._contract, balance, cls.MAX_RISK_PER_TRADE)
    
    @classmethod
    def get_contract_details(cls) -> Dict:
        """Get full contract details"""
        return {
            'symbol': cls.SYMBOL,
            'full_symbol': cls.FULL_SYMBOL,
            'contract_id': cls.CONTRACT_ID,
            'tick_size': cls.TICK_SIZE,
            'tick_value': cls.TICK_VALUE,
            'volatility': cls.CONTRACT_VOLATILITY,
            'position_limits': {
                'min': cls.MIN_POSITION,
                'max': cls.MAX_POSITION,
                'default': cls.DEFAULT_POSITION
            },
            'timeframes': {
                'primary': cls.PRIMARY_TIMEFRAME,
                'htf': cls.HTF_TIMEFRAME,
                'entry': cls.ENTRY_TIMEFRAME,
                'analysis': cls.ANALYSIS_TIMEFRAMES
            }
        }
    
    @classmethod
    def get_all_config_values(cls) -> Dict:
        """Get all configuration values as a dictionary"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate critical configuration settings"""
        if not cls.TOPSTEP_API_KEY or cls.TOPSTEP_API_KEY == 'your_api_key_here':
            raise ValueError("TOPSTEP_API_KEY not configured in .env file")
        
        if not cls.TOPSTEP_API_SECRET or cls.TOPSTEP_API_SECRET == 'your_api_secret_here':
            raise ValueError("TOPSTEP_API_SECRET not configured in .env file")
        
        if not cls.TOPSTEP_ACCOUNT_ID or cls.TOPSTEP_ACCOUNT_ID == 'your_account_id_here':
            raise ValueError("TOPSTEP_ACCOUNT_ID not configured in .env file")
        
        return True