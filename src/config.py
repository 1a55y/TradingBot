"""Configuration settings for Gold Futures Trading Bot"""
import os
from datetime import time
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Settings
    TOPSTEP_API_KEY = os.getenv('TOPSTEP_API_KEY')
    TOPSTEP_API_SECRET = os.getenv('TOPSTEP_API_SECRET')
    TOPSTEP_USERNAME = os.getenv('TOPSTEP_USERNAME')
    TOPSTEP_USER_ID = os.getenv('TOPSTEP_USER_ID')
    TOPSTEP_ACCOUNT_ID = os.getenv('TOPSTEP_ACCOUNT_ID')
    TOPSTEP_MARKET = os.getenv('TOPSTEP_MARKET', 'CME_TOB')
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
    
    # Account IDs
    STEP1_ACCOUNT_ID = 9203477  # S1JUL114911938 - Step 1 evaluation
    PRACTICE_ACCOUNT_ID = 9156522  # PRACTICEJUN3014889749 - Practice account
    
    # API URLs
    TOPSTEP_API_BASE_URL = os.getenv('TOPSTEP_API_BASE_URL', 'https://api.topstepx.com')
    TOPSTEP_RTC_BASE_URL = os.getenv('TOPSTEP_RTC_BASE_URL', 'https://rtc.topstepx.com')
    TOPSTEP_WS_DATA_URL = os.getenv('TOPSTEP_WS_DATA_URL', 'wss://rtc.topstepx.com/hubs/market')
    TOPSTEP_WS_TRADING_URL = os.getenv('TOPSTEP_WS_TRADING_URL', 'wss://rtc.topstepx.com/hubs/user')
    API_BASE_URL = os.getenv('TOPSTEP_API_BASE_URL', 'https://api.topstepx.com')
    RTC_BASE_URL = os.getenv('TOPSTEP_RTC_BASE_URL', 'https://rtc.topstepx.com')
    WS_DATA_URL = os.getenv('TOPSTEP_WS_DATA_URL', 'wss://rtc.topstepx.com/hubs/market')
    WS_TRADING_URL = os.getenv('TOPSTEP_WS_TRADING_URL', 'wss://rtc.topstepx.com/hubs/user')
    
    # Contract Specifications
    SYMBOL = 'MGC'  # Micro Gold base symbol
    FULL_SYMBOL = 'MGCQ25'  # Current active micro gold contract (display name)
    CONTRACT_ID_MGC = 'CON.F.US.MGC.Q25'  # TopStepX contract ID for MGC
    STANDARD_SYMBOL = 'GC'  # Standard Gold base symbol
    STANDARD_FULL_SYMBOL = 'GCQ25'  # Current active standard gold contract
    CONTRACT_ID_GC = 'CON.F.US.GC.Q25'  # TopStepX contract ID for GC
    TICK_SIZE = 0.10  # $0.10 price movement
    TICK_VALUE = 1.0  # $1 per tick (for MGC)
    TICK_VALUE_GC = 10.0  # $10 per tick (for GC)
    CONTRACT_MONTHS = ['G', 'J', 'M', 'Q', 'V', 'Z']  # Feb, Apr, Jun, Aug, Oct, Dec
    
    # Contract selection
    USE_MICRO_GOLD = True  # Use MGC (True) or GC (False)
    
    @classmethod
    def get_active_contract(cls) -> str:
        """Get the currently active contract symbol"""
        if cls.USE_MICRO_GOLD:
            return cls.FULL_SYMBOL
        else:
            return cls.STANDARD_FULL_SYMBOL
    
    @classmethod
    def get_contract_id(cls) -> str:
        """Get the TopStepX contract ID"""
        if cls.USE_MICRO_GOLD:
            return cls.CONTRACT_ID_MGC
        else:
            return cls.CONTRACT_ID_GC
    
    @classmethod
    def get_tick_value(cls) -> float:
        """Get tick value for current contract"""
        if cls.USE_MICRO_GOLD:
            return cls.TICK_VALUE
        else:
            return cls.TICK_VALUE_GC
    
    # Position Limits
    MAX_POSITION_MGC = 50  # Exchange limit
    MIN_POSITION_MGC = 5   # Our minimum
    DEFAULT_POSITION_MGC = 5  # Starting size (conservative)
    
    # Risk Parameters (TopStep Rules)
    ACCOUNT_SIZE = 50000
    DAILY_LOSS_LIMIT = 800  # Hard stop
    TRAILING_DRAWDOWN = 2000  # TopStep trailing
    MAX_RISK_PER_TRADE = 500
    WARNING_RISK_PER_TRADE = 400  # Alert level
    MAX_CONSECUTIVE_LOSSES = 2
    
    # Trading Hours (Helsinki Time - EET/EEST)
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
    MIN_STOP_TICKS = 25  # Absolute minimum ($2.50)
    MAX_STOP_TICKS = 100  # Risk limit constraint (allows up to $10.00 stop distance per contract)
    DEFAULT_STOP_TICKS = 35  # Starting point ($3.50)
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
    
    # Pattern Detection Enhancements
    MAX_PATTERN_AGE_CANDLES = 50  # Don't trade patterns older than this
    PATTERN_VIOLATION_TOLERANCE = 0.002  # 0.2% tolerance for pattern violations
    
    # Mock Trading Parameters
    MOCK_VOLATILITY = 0.001  # 0.1% volatility for mock price generation
    MOCK_TREND = 0.00001  # Slight upward bias in mock data
    MOCK_PRICE_RANGE_MIN = 1900  # Minimum gold price in mock mode
    MOCK_PRICE_RANGE_MAX = 2200  # Maximum gold price in mock mode
    MOCK_BASE_WIN_PROBABILITY = 0.45  # 45% base win rate for mock trades
    
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
    def get_active_contract(cls) -> str:
        """Get current active gold futures contract"""
        # TODO: Implement logic to determine current front month
        # For now, return a placeholder
        from datetime import datetime
        month_codes = {2: 'G', 4: 'J', 6: 'M', 8: 'Q', 10: 'V', 12: 'Z'}
        current_month = datetime.now().month
        
        # Find next contract month
        for month, code in month_codes.items():
            if month >= current_month:
                year = str(datetime.now().year)[-2:]
                return f"MGC{code}{year}"
        
        # If no future month found, use February of next year
        next_year = str(datetime.now().year + 1)[-2:]
        return f"MGCG{next_year}"
    
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