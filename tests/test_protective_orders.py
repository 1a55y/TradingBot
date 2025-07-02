"""Test protective order placement functionality"""
# Standard library imports
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Third-party imports
import pytest

# Local imports
from src.api.mock_topstep_client import MockTopStepXClient
from src.bot_live import LiveGoldBot
from src.config import Config
from src.utils.logger_setup import logger


class TestProtectiveOrders:
    """Test protective order placement for stop loss and take profit"""
    
    def setup_method(self):
        """Setup test environment"""
        self.bot = LiveGoldBot(use_mock_api=True)
        self.bot.config = Config
        
    async def test_place_protective_orders_after_fill(self):
        """Test placing separate stop and limit orders after market order fills"""
        # Setup mock connection
        await self.bot.connect()
        
        # Simulate a market order fill
        fill_event = {
            'order_id': 'TEST123',
            'fill_price': 2500.50,
            'quantity': 1,
            'side': 'BUY'
        }
        
        # Calculate stop and target prices
        stop_price = 2495.50  # 5 points below
        target_price = 2510.50  # 10 points above
        
        # Track the position
        self.bot.positions['TEST123'] = {
            'order_id': 'TEST123',
            'side': 'BUY',
            'quantity': 1,
            'entry_price': 2500.50,
            'stop_price': stop_price,
            'target_price': target_price,
            'status': 'pending',
            'entry_timestamp': datetime.now(timezone.utc),
            'risk_amount': 25.00,  # Mock risk amount
            'expected_entry': 2500.50
        }
        
        # Handle the fill
        await self.bot._handle_fill(fill_event)
        
        # Now place protective orders
        success = await self.bot.place_protective_orders('TEST123')
        
        assert success is True
        
        # Check that protective orders were tracked
        assert 'TEST123' in self.bot.protective_orders
        protective_orders = self.bot.protective_orders['TEST123']
        
        assert 'stop_order_id' in protective_orders
        assert 'target_order_id' in protective_orders
        
        logger.info(f"Protective orders placed: {protective_orders}")
        
        # Cleanup
        await self.bot.disconnect()
        
    async def test_cancel_protective_orders_on_stop_fill(self):
        """Test canceling target order when stop order fills"""
        await self.bot.connect()
        
        # Setup a position with protective orders
        position_id = 'TEST456'
        self.bot.positions[position_id] = {
            'order_id': position_id,
            'side': 'SELL',
            'quantity': 2,
            'entry_price': 2600.00,
            'stop_price': 2605.00,
            'target_price': 2590.00,
            'status': 'filled'
        }
        
        # Track protective orders
        self.bot.protective_orders[position_id] = {
            'stop_order_id': 'STOP789',
            'target_order_id': 'TARGET789'
        }
        
        # Simulate stop order fill
        stop_fill_event = {
            'order_id': 'STOP789',
            'fill_price': 2605.00,
            'quantity': 2,
            'side': 'BUY'  # Opposite side to close position
        }
        
        # Handle stop fill
        await self.bot._handle_protective_order_fill(stop_fill_event)
        
        # Check that target order was cancelled
        assert self.bot.api_client.cancelled_orders
        assert 'TARGET789' in self.bot.api_client.cancelled_orders
        
        await self.bot.disconnect()
        
    async def test_handle_market_order_without_brackets(self):
        """Test handling when market order stop/limit don't work"""
        await self.bot.connect()
        
        # Place a regular market order
        order_data = {
            "symbol": Config.SYMBOL,
            "contractId": "test-contract-id",
            "side": "Buy",
            "quantity": 1,
            "orderType": "Market",
            "time_in_force": "GTC",
            "account_id": Config.PRACTICE_ACCOUNT_ID
        }
        
        # Note: NOT including stopPrice or limitPrice in market order
        # These will be placed as separate orders after fill
        
        result = await self.bot.api_client.place_order(order_data)
        assert result is not None
        assert 'order_id' in result
        
        await self.bot.disconnect()


async def run_tests():
    """Run all tests"""
    test_class = TestProtectiveOrders()
    
    # Run each test
    logger.info("Testing protective order placement...")
    test_class.setup_method()
    await test_class.test_place_protective_orders_after_fill()
    
    logger.info("\nTesting protective order cancellation...")
    test_class.setup_method()
    await test_class.test_cancel_protective_orders_on_stop_fill()
    
    logger.info("\nTesting market order without brackets...")
    test_class.setup_method()
    await test_class.test_handle_market_order_without_brackets()
    
    logger.info("\n✅ All protective order tests passed!")


if __name__ == "__main__":
    asyncio.run(run_tests())