"""Mock TopStepX API Client for Testing"""
# Standard library imports
import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Third-party imports
import numpy as np

# Local imports
from src.config import Config
from src.utils.logger_setup import logger


class MockTopStepXClient:
    """Mock client for testing without real API"""
    
    def __init__(self):
        self.config = Config
        self.is_connected = False
        self.mock_balance = 50000.0
        self.mock_positions = []
        self.mock_orders = []
        self.current_price = 2050.0
        self.cancelled_orders = []  # Track cancelled orders for testing
        self.order_counter = 1000  # For generating order IDs
        
        logger.info("Mock TopStepX Client initialized")
    
    async def connect(self) -> bool:
        """Mock connection - always succeeds"""
        await asyncio.sleep(0.5)  # Simulate network delay
        self.is_connected = True
        logger.info("Mock connection successful")
        return True
    
    async def disconnect(self) -> None:
        """Mock disconnect"""
        self.is_connected = False
        logger.info("Mock disconnected")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Mock headers"""
        return {'Authorization': 'Bearer MOCK_TOKEN'}
    
    async def _test_auth(self) -> bool:
        """Mock auth test - always succeeds"""
        return True
    
    async def get_account_info(self) -> Optional[Dict]:
        """Mock account info"""
        return {
            'username': self.config.TOPSTEP_USERNAME or 'mock_user',
            'balance': self.mock_balance,
            'account_id': self.config.TOPSTEP_ACCOUNT_ID or '12345',
            'status': 'active',
            'daily_pnl': 0.0
        }
    
    async def get_positions(self) -> List[Dict]:
        """Mock positions"""
        return self.mock_positions
    
    async def place_order(self, order_data: Dict) -> Optional[Dict]:
        """Mock order placement"""
        # Generate unique order ID
        self.order_counter += 1
        order_id = f"MOCK_{self.order_counter}"
        
        # Determine fill price based on order type
        order_type = order_data.get('orderType', 'Market')
        if order_type == 'Market':
            fill_price = self.current_price
        elif order_type == 'Limit':
            fill_price = order_data.get('limitPrice', self.current_price)
        elif order_type == 'Stop':
            fill_price = order_data.get('stopPrice', self.current_price)
        else:
            fill_price = self.current_price
            
        order = {
            'order_id': order_id,
            'orderId': order_id,  # Support both formats
            'status': 'filled' if order_type == 'Market' else 'pending',
            'fill_price': fill_price,
            **order_data
        }
        self.mock_orders.append(order)
        
        # Create mock position for market orders
        if order_type == 'Market':
            position = {
                'position_id': f"POS_{order_id}",
                'symbol': order_data['symbol'],
                'side': order_data['side'],
                'quantity': order_data['quantity'],
                'entry_price': self.current_price,
                'unrealized_pnl': 0.0
            }
            self.mock_positions.append(position)
        
        logger.info(f"Mock {order_type} order placed: {order_id}")
        return order
    
    async def cancel_order(self, order_id: str) -> bool:
        """Mock order cancellation"""
        self.cancelled_orders.append(order_id)
        logger.info(f"Mock order cancelled: {order_id}")
        return True
    
    async def get_market_data(self, symbol: str = "MGC") -> Optional[Dict]:
        """Mock market data"""
        spread = 0.20  # $0.20 spread
        return {
            'symbol': symbol,
            'bid': self.current_price - spread/2,
            'ask': self.current_price + spread/2,
            'last': self.current_price,
            'bid_size': np.random.randint(10, 100),
            'ask_size': np.random.randint(10, 100),
            'volume': np.random.randint(5000, 20000)
        }
    
    async def _get_contract_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Mock contract lookup"""
        # Return mock contract data
        return {
            'id': f'mock-contract-{symbol}',
            'contractId': f'mock-contract-{symbol}',
            'symbol': symbol,
            'name': f'Mock {symbol} Contract',
            'tickSize': 0.25,
            'tickValue': 1.25
        }
    
    async def get_historical_data(
        self, 
        symbol: str = "MGC", 
        interval: str = "15m", 
        limit: int = 100
    ) -> Optional[List[Dict]]:
        """Mock historical data"""
        candles = []
        current_time = datetime.now(timezone.utc)
        interval_minutes = {'1m': 1, '5m': 5, '15m': 15, '1h': 60}.get(interval, 15)
        
        for i in range(limit):
            timestamp = current_time.timestamp() * 1000 - (i * interval_minutes * 60 * 1000)
            base_price = self.current_price - (i * 0.1)
            
            open_price = base_price + np.random.uniform(-2, 2)
            close_price = open_price + np.random.uniform(-3, 3)
            high_price = max(open_price, close_price) + np.random.uniform(0, 2)
            low_price = min(open_price, close_price) - np.random.uniform(0, 2)
            
            candles.append({
                'time': int(timestamp),
                'o': round(open_price, 2),
                'h': round(high_price, 2),
                'l': round(low_price, 2),
                'c': round(close_price, 2),
                'v': np.random.randint(100, 1000)
            })
        
        return list(reversed(candles))
    
    async def handle_market_data_stream(self):
        """Mock market data stream"""
        while self.is_connected:
            # Update price randomly
            self.current_price += np.random.uniform(-0.5, 0.5)
            
            yield {
                'type': 'quote',
                'symbol': 'MGC',
                'bid': self.current_price - 0.1,
                'ask': self.current_price + 0.1,
                'bid_size': np.random.randint(10, 100),
                'ask_size': np.random.randint(10, 100)
            }
            
            await asyncio.sleep(1)  # Update every second
    
    async def handle_trading_events(self):
        """Mock trading events"""
        while self.is_connected:
            # Simulate position updates
            for position in self.mock_positions:
                # Random P&L changes
                pnl_change = np.random.uniform(-50, 50)
                position['unrealized_pnl'] = position.get('unrealized_pnl', 0) + pnl_change
                
                yield {
                    'type': 'position_update',
                    'position': position
                }
            
            await asyncio.sleep(5)  # Update every 5 seconds