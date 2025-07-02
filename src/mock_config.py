"""Mock Trading Configuration - Separate from main config to keep it clean"""
import os
from dotenv import load_dotenv

load_dotenv()

class MockConfig:
    """Configuration specific to mock/simulation trading"""
    
    # Mock Data Generation
    MOCK_VOLATILITY = float(os.getenv('MOCK_VOLATILITY', '0.001'))  # 0.1% volatility
    MOCK_TREND = float(os.getenv('MOCK_TREND', '0.00001'))  # Slight upward bias
    MOCK_BASE_WIN_PROBABILITY = float(os.getenv('MOCK_BASE_WIN_PROBABILITY', '0.45'))  # 45% base win rate
    
    # Mock Price Ranges (per contract)
    MOCK_PRICE_RANGES = {
        'MNQ': {'min': 20000, 'max': 22000},
        'NQ': {'min': 20000, 'max': 22000},
        'MES': {'min': 5900, 'max': 6100},
        'ES': {'min': 5900, 'max': 6100},
        'MGC': {'min': 1900, 'max': 2200},
        'GC': {'min': 1900, 'max': 2200}
    }
    
    # Mock Order Execution
    MOCK_FILL_DELAY_MS = 100  # Simulated order fill delay
    MOCK_SLIPPAGE_TICKS = 1  # Simulated slippage
    
    @classmethod
    def get_price_range(cls, contract_symbol: str) -> tuple:
        """Get mock price range for a contract"""
        range_info = cls.MOCK_PRICE_RANGES.get(contract_symbol, {'min': 1000, 'max': 2000})
        return range_info['min'], range_info['max']