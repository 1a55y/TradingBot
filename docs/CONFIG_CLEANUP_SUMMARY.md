# Configuration Cleanup Summary

## Changes Made

### 1. Removed Duplicate Settings
- Removed duplicate API URL variables (API_BASE_URL, RTC_BASE_URL, WS_DATA_URL, WS_TRADING_URL)
- Kept only the TOPSTEP_* prefixed versions for consistency

### 2. Removed Legacy Contract-Specific Variables
- Removed hardcoded CONTRACT_ID_MNQ and CONTRACT_ID_NQ
- Removed TICK_VALUE_NQ 
- Removed USE_MICRO_NASDAQ
- Removed legacy position limits (MAX_POSITION_MNQ, MIN_POSITION_MNQ, DEFAULT_POSITION_MNQ)
- Now using dynamic contract system from contracts.py

### 3. Made Account IDs Configurable
- STEP1_ACCOUNT_ID now reads from environment variable TOPSTEP_STEP1_ACCOUNT_ID
- PRACTICE_ACCOUNT_ID now reads from environment variable TOPSTEP_PRACTICE_ACCOUNT_ID
- Defaults are provided for backward compatibility

### 4. Dynamic Account Balance
- Replaced hardcoded ACCOUNT_SIZE with DEFAULT_ACCOUNT_SIZE (used as fallback)
- Added get_account_balance() method to fetch real account balance from API
- Position sizing now uses actual account balance when available
- Balance is cached for 5 minutes to reduce API calls

### 5. Separated Mock Trading Configuration
- Created new src/mock_config.py for mock-specific settings
- Moved MOCK_VOLATILITY, MOCK_TREND, MOCK_BASE_WIN_PROBABILITY to mock config
- Added contract-specific price ranges for mock trading
- Removed mock-specific settings from main config

### 6. Updated Position Sizing
- calculate_position_size() now uses dynamic account balance
- Uses calculate_dynamic_position_size() from config which considers:
  - Current account balance
  - Contract specifications
  - Risk per trade limits
  - Contract volatility adjustments

### 7. Environment Variables Added
These optional environment variables can now be set in .env:
- TOPSTEP_STEP1_ACCOUNT_ID
- TOPSTEP_PRACTICE_ACCOUNT_ID  
- DEFAULT_ACCOUNT_SIZE
- MOCK_VOLATILITY
- MOCK_TREND
- MOCK_BASE_WIN_PROBABILITY

## Benefits
1. **Cleaner Configuration**: No duplicate or obsolete settings
2. **Dynamic Contract Support**: Easy to switch between different contracts
3. **Accurate Risk Management**: Position sizing based on actual account balance
4. **Better Organization**: Mock settings separated from production config
5. **Environment-Based**: All hardcoded values can be overridden via environment

## Usage
The bot will automatically:
1. Fetch account balance on startup
2. Refresh balance every 5 minutes during operation
3. Use actual balance for position sizing calculations
4. Fall back to DEFAULT_ACCOUNT_SIZE if API is unavailable

No changes needed to existing .env files - all new variables have sensible defaults.