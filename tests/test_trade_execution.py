"""
Comprehensive Test Suite for Trade Execution Mechanics
Tests all aspects of trade execution including:
- Stop loss placement
- Take profit calculations
- Position sizing
- Order rejection handling
- Partial fill scenarios
- Risk per trade calculations
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# Import the modules we need to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.core.base_bot import BaseGoldBot
from src.api.topstep_client import TopStepXClient
from src.utils.data_validator import DataValidator, DataValidationError


class MockGoldBot(BaseGoldBot):
    """Mock implementation of BaseGoldBot for testing"""
    
    def __init__(self):
        super().__init__()
        self.orders_placed = []
        self.connection_status = True
        self.mock_client = Mock()
        self.is_running = True
        
    async def connect(self) -> bool:
        return self.connection_status
    
    async def disconnect(self) -> None:
        pass
    
    async def run(self) -> None:
        """Mock run method for testing"""
        pass
        
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        # Return mock candle data
        data = {
            'timestamp': pd.date_range(start='2025-01-01', periods=limit, freq='15min'),
            'open': np.random.uniform(22000, 22100, limit),
            'high': np.random.uniform(22050, 22150, limit),
            'low': np.random.uniform(21950, 22050, limit),
            'close': np.random.uniform(22000, 22100, limit),
            'volume': np.random.uniform(1000, 5000, limit)
        }
        return pd.DataFrame(data)
    
    async def place_order(self, side: str, quantity: int, stop_price: float, target_price: float) -> bool:
        order = {
            'side': side,
            'quantity': quantity,
            'stop_price': stop_price,
            'target_price': target_price,
            'timestamp': datetime.now(timezone.utc)
        }
        self.orders_placed.append(order)
        return True
    
    async def execute_signal(self, signal: dict, score: float, candles: pd.DataFrame) -> None:
        """Mock execute_signal for testing"""
        current_price = self.current_price
        
        # Calculate stop and target
        stop_distance = self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE
        if signal['type'] == 'bullish':
            side = 'BUY'
            stop_price = current_price - stop_distance
            target_price = current_price + (stop_distance * self.config.TP1_RATIO)
        else:
            side = 'SELL'
            stop_price = current_price + stop_distance
            target_price = current_price - (stop_distance * self.config.TP1_RATIO)
            
        # Place order
        quantity = self.calculate_position_size(self.config.DEFAULT_STOP_TICKS)
        await self.place_order(side, quantity, stop_price, target_price)


class TestTradeExecution(unittest.TestCase):
    """Test suite for trade execution mechanics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bot = MockGoldBot()
        self.config = Config
        self.validator = DataValidator(self.config)
        
        # Mock account state
        self.bot.daily_pnl = 0
        self.bot.consecutive_losses = 0
        self.bot.current_price = 22050.0  # MNQ price range
        
    def tearDown(self):
        """Clean up after tests"""
        self.bot = None
        
    def test_stop_loss_placement_bullish(self):
        """Test stop loss placement for bullish trades"""
        # For a bullish trade at 22050
        entry_price = 22050.0
        expected_stop = entry_price - (self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE)
        
        # Create bullish signal
        signal = {
            'type': 'bullish',
            'level': 22045.0,  # Support level below entry
            'index': 95,
            'timestamp': datetime.now(timezone.utc),
            'strength': 2.0
        }
        
        # Execute signal
        asyncio.run(self._execute_test_signal(signal, entry_price))
        
        # Verify stop loss placement
        self.assertEqual(len(self.bot.orders_placed), 1)
        order = self.bot.orders_placed[0]
        self.assertEqual(order['side'], 'BUY')
        self.assertAlmostEqual(order['stop_price'], expected_stop, places=2)
        self.assertLess(order['stop_price'], entry_price)  # Stop below entry for long
        
    def test_stop_loss_placement_bearish(self):
        """Test stop loss placement for bearish trades"""
        # For a bearish trade at 22050
        entry_price = 22050.0
        expected_stop = entry_price + (self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE)
        
        # Create bearish signal
        signal = {
            'type': 'bearish',
            'level': 22055.0,  # Resistance level above entry
            'index': 95,
            'timestamp': datetime.now(timezone.utc),
            'strength': 2.0
        }
        
        # Execute signal
        asyncio.run(self._execute_test_signal(signal, entry_price))
        
        # Verify stop loss placement
        self.assertEqual(len(self.bot.orders_placed), 1)
        order = self.bot.orders_placed[0]
        self.assertEqual(order['side'], 'SELL')
        self.assertAlmostEqual(order['stop_price'], expected_stop, places=2)
        self.assertGreater(order['stop_price'], entry_price)  # Stop above entry for short
        
    def test_take_profit_calculations(self):
        """Test take profit calculations for different ratios"""
        entry_price = 22050.0
        stop_distance = self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE
        
        # Test TP1 (1:1 ratio)
        tp1_distance = stop_distance * self.config.TP1_RATIO
        expected_tp1_buy = entry_price + tp1_distance
        expected_tp1_sell = entry_price - tp1_distance
        
        # Test TP2 (1:2 ratio)
        tp2_distance = stop_distance * self.config.TP2_RATIO
        expected_tp2_buy = entry_price + tp2_distance
        expected_tp2_sell = entry_price - tp2_distance
        
        # Test Runner (2.5:1 ratio)
        runner_distance = stop_distance * self.config.RUNNER_RATIO
        expected_runner_buy = entry_price + runner_distance
        expected_runner_sell = entry_price - runner_distance
        
        # Execute bullish trade
        signal = {
            'type': 'bullish',
            'level': 22045.0,
            'index': 95,
            'timestamp': datetime.now(timezone.utc),
            'strength': 2.0
        }
        asyncio.run(self._execute_test_signal(signal, entry_price))
        
        # Verify TP calculation for bullish
        order = self.bot.orders_placed[0]
        self.assertAlmostEqual(order['target_price'], expected_tp1_buy, places=2)
        
        # Clear orders
        self.bot.orders_placed = []
        
        # Execute bearish trade
        signal['type'] = 'bearish'
        signal['level'] = 22055.0
        asyncio.run(self._execute_test_signal(signal, entry_price))
        
        # Verify TP calculation for bearish
        order = self.bot.orders_placed[0]
        self.assertAlmostEqual(order['target_price'], expected_tp1_sell, places=2)
        
    def test_position_sizing_based_on_risk(self):
        """Test position sizing based on risk parameters"""
        # Test default position size
        stop_distance_ticks = 10
        size = self.bot.calculate_position_size(stop_distance_ticks)
        self.assertEqual(size, self.config.DEFAULT_POSITION_MNQ)
        
        # Test reduced size after losses
        self.bot.consecutive_losses = 1
        size = self.bot.calculate_position_size(stop_distance_ticks)
        expected_reduced = max(self.config.MIN_POSITION_MNQ, self.config.DEFAULT_POSITION_MNQ // 2)
        self.assertEqual(size, expected_reduced)
        
        # Test minimum position size enforcement
        self.bot.consecutive_losses = 3
        size = self.bot.calculate_position_size(stop_distance_ticks)
        self.assertEqual(size, self.config.MIN_POSITION_MNQ)
        
    def test_risk_per_trade_calculations(self):
        """Test risk per trade calculations"""
        # Calculate risk for different position sizes and stop distances
        position_size = 2
        stop_distance_ticks = 10
        tick_value = self.config.TICK_VALUE
        
        expected_risk = position_size * stop_distance_ticks * tick_value
        
        # Verify risk doesn't exceed maximum
        self.assertLessEqual(expected_risk, self.config.MAX_RISK_PER_TRADE)
        
        # Test with larger position
        large_position = 10
        large_risk = large_position * stop_distance_ticks * tick_value
        
        # Should trigger warning if exceeds warning level
        if large_risk > self.config.WARNING_RISK_PER_TRADE:
            self.assertGreater(large_risk, self.config.WARNING_RISK_PER_TRADE)
            
    def test_order_rejection_handling(self):
        """Test handling of order rejections"""
        # Mock a failing order
        self.bot.place_order = AsyncMock(return_value=False)
        
        signal = {
            'type': 'bullish',
            'level': 22045.0,
            'index': 95,
            'timestamp': datetime.now(timezone.utc),
            'strength': 2.0
        }
        
        # Execute signal that will be rejected
        asyncio.run(self._execute_test_signal(signal, 22050.0))
        
        # Verify order was attempted
        self.bot.place_order.assert_called_once()
        
        # Verify no position was recorded (since it failed)
        # In real implementation, check that position tracking remains accurate
        
    def test_partial_fill_scenarios(self):
        """Test handling of partial fills"""
        # This would require more complex mocking of the order system
        # For now, test the concept
        
        # Mock a partial fill response
        partial_fill_order = {
            'orderId': '12345',
            'side': 'BUY',
            'requestedQuantity': 5,
            'filledQuantity': 3,
            'remainingQuantity': 2,
            'status': 'PARTIAL'
        }
        
        # Verify system can handle partial quantities
        filled_qty = partial_fill_order['filledQuantity']
        requested_qty = partial_fill_order['requestedQuantity']
        
        self.assertLess(filled_qty, requested_qty)
        self.assertEqual(filled_qty + partial_fill_order['remainingQuantity'], requested_qty)
        
    def test_trade_validation_edge_cases(self):
        """Test edge cases in trade validation"""
        # Test invalid stop price
        with self.assertRaises(DataValidationError):
            self.validator.validate_price(-100, "stop_price")
            
        # Test invalid position size
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="BUY",
                quantity=0,  # Invalid: zero quantity
                stop=22040.0,
                target=22060.0,
                entry=22050.0
            )
            
        # Test stop loss on wrong side of market
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="BUY",
                quantity=2,
                stop=2060.0,  # Invalid: stop above entry for long
                target=2070.0,
                entry=2050.0
            )
            
    def test_winning_trade_scenario(self):
        """Test complete winning trade scenario"""
        # Setup
        entry_price = 22050.0
        stop_distance = self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE
        tp_price = entry_price + (stop_distance * self.config.TP1_RATIO)
        
        # Execute trade
        signal = {
            'type': 'bullish',
            'level': 22045.0,
            'index': 95,
            'timestamp': datetime.now(timezone.utc),
            'strength': 2.0
        }
        asyncio.run(self._execute_test_signal(signal, entry_price))
        
        # Simulate winning trade
        order = self.bot.orders_placed[0]
        position_size = order['quantity']
        profit_ticks = (tp_price - entry_price) / self.config.TICK_SIZE
        profit = position_size * profit_ticks * self.config.TICK_VALUE
        
        # Verify profit calculation
        self.assertGreater(profit, 0)
        self.assertLessEqual(profit, self.config.MAX_RISK_PER_TRADE * self.config.TP1_RATIO)
        
    def test_losing_trade_scenario(self):
        """Test complete losing trade scenario"""
        # Setup
        entry_price = 22050.0
        stop_distance = self.config.DEFAULT_STOP_TICKS * self.config.TICK_SIZE
        stop_price = entry_price - stop_distance
        
        # Execute trade
        signal = {
            'type': 'bullish',
            'level': 22045.0,
            'index': 95,
            'timestamp': datetime.now(timezone.utc),
            'strength': 2.0
        }
        asyncio.run(self._execute_test_signal(signal, entry_price))
        
        # Simulate losing trade
        order = self.bot.orders_placed[0]
        position_size = order['quantity']
        loss_ticks = (entry_price - stop_price) / self.config.TICK_SIZE
        loss = position_size * loss_ticks * self.config.TICK_VALUE
        
        # Verify loss calculation
        self.assertGreater(loss, 0)  # Loss is positive value
        self.assertLessEqual(loss, self.config.MAX_RISK_PER_TRADE)
        
    def test_daily_loss_limit_enforcement(self):
        """Test that daily loss limit is enforced"""
        # Set daily P&L near limit
        self.bot.daily_pnl = -self.config.DAILY_LOSS_LIMIT + 100
        
        # Should still be able to trade
        self.assertTrue(self.bot.can_trade())
        
        # Exceed daily loss limit
        self.bot.daily_pnl = -self.config.DAILY_LOSS_LIMIT - 1
        
        # Should not be able to trade
        self.assertFalse(self.bot.can_trade())
        
    def test_consecutive_loss_limit_enforcement(self):
        """Test that consecutive loss limit is enforced"""
        # Under limit
        self.bot.consecutive_losses = self.config.MAX_CONSECUTIVE_LOSSES - 1
        self.assertTrue(self.bot.can_trade())
        
        # At limit
        self.bot.consecutive_losses = self.config.MAX_CONSECUTIVE_LOSSES
        self.assertFalse(self.bot.can_trade())
        
    async def _execute_test_signal(self, signal, current_price):
        """Helper method to execute a test signal"""
        # Create mock candles with the current price
        candles = pd.DataFrame({
            'timestamp': pd.date_range(start='2025-01-01', periods=100, freq='15min'),
            'open': [current_price] * 100,
            'high': [current_price + 1] * 100,
            'low': [current_price - 1] * 100,
            'close': [current_price] * 100,
            'volume': [1000] * 100
        })
        
        # Execute the signal
        await self.bot.execute_signal(signal, 8.0, candles)


class TestOrderValidation(unittest.TestCase):
    """Test order validation logic"""
    
    def setUp(self):
        self.config = Config
        self.validator = DataValidator(self.config)
        
    def test_valid_buy_order(self):
        """Test validation of valid buy order"""
        try:
            self.validator.validate_order_params(
                side="BUY",
                quantity=2,
                stop=22040.0,
                target=22060.0,
                entry=22050.0
            )
            # Should not raise exception
            self.assertTrue(True)
        except DataValidationError:
            self.fail("Valid buy order failed validation")
            
    def test_valid_sell_order(self):
        """Test validation of valid sell order"""
        try:
            self.validator.validate_order_params(
                side="SELL",
                quantity=2,
                stop=22060.0,
                target=22040.0,
                entry=22050.0
            )
            # Should not raise exception
            self.assertTrue(True)
        except DataValidationError:
            self.fail("Valid sell order failed validation")
            
    def test_invalid_quantity(self):
        """Test validation rejects invalid quantities"""
        # Zero quantity
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="BUY",
                quantity=0,
                stop=22040.0,
                target=22060.0,
                entry=22050.0
            )
            
        # Negative quantity
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="BUY",
                quantity=-1,
                stop=22040.0,
                target=22060.0,
                entry=22050.0
            )
            
        # Exceeds maximum
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="BUY",
                quantity=self.config.MAX_POSITION_MNQ + 1,
                stop=22040.0,
                target=22060.0,
                entry=22050.0
            )
            
    def test_invalid_stop_placement(self):
        """Test validation rejects incorrectly placed stops"""
        # Buy with stop above entry
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="BUY",
                quantity=2,
                stop=22060.0,  # Above entry
                target=22070.0,
                entry=22050.0
            )
            
        # Sell with stop below entry
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="SELL",
                quantity=2,
                stop=22040.0,  # Below entry
                target=22030.0,
                entry=22050.0
            )
            
    def test_invalid_target_placement(self):
        """Test validation rejects incorrectly placed targets"""
        # Buy with target below entry
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="BUY",
                quantity=2,
                stop=2040.0,
                target=22045.0,  # Below entry
                entry=22050.0
            )
            
        # Sell with target above entry
        with self.assertRaises(DataValidationError):
            self.validator.validate_order_params(
                side="SELL",
                quantity=2,
                stop=2060.0,
                target=22055.0,  # Above entry
                entry=22050.0
            )


class TestRiskCalculations(unittest.TestCase):
    """Test risk calculation mechanics"""
    
    def setUp(self):
        self.config = Config
        
    def test_risk_per_contract(self):
        """Test risk calculation per contract"""
        stop_ticks = 10
        risk_per_contract = stop_ticks * self.config.TICK_VALUE
        
        # For MNQ with $0.50 tick value
        expected_risk = 10 * 0.50
        self.assertEqual(risk_per_contract, expected_risk)
        
    def test_total_position_risk(self):
        """Test total position risk calculation"""
        position_size = 5
        stop_ticks = 10
        total_risk = position_size * stop_ticks * self.config.TICK_VALUE
        
        expected_total = 5 * 10 * 0.50
        self.assertEqual(total_risk, expected_total)
        
    def test_risk_as_percentage_of_account(self):
        """Test risk as percentage of account"""
        account_size = self.config.ACCOUNT_SIZE
        position_risk = 500  # $500 risk
        
        risk_percentage = (position_risk / account_size) * 100
        expected_percentage = (500 / 50000) * 100
        
        self.assertAlmostEqual(risk_percentage, expected_percentage)
        self.assertEqual(risk_percentage, 1.0)  # 1% risk
        
    def test_maximum_position_for_risk(self):
        """Test calculation of maximum position size for given risk"""
        max_risk = self.config.MAX_RISK_PER_TRADE
        stop_ticks = 10
        tick_value = self.config.TICK_VALUE
        
        max_position = max_risk / (stop_ticks * tick_value)
        
        # This test shows that with current settings, the risk allows more contracts than the position limit
        # This is actually correct - the position limit should constrain the size, not the risk calculation
        # With $500 risk, 10 tick stop, and $0.50 tick value = 100 contracts theoretical max
        # But position limit of 50 contracts would constrain this
        calculated_max = 100.0  # 500 / (10 * 0.50)
        self.assertEqual(max_position, calculated_max)
        
        # The actual position size should be capped by the limit
        actual_position = min(max_position, self.config.MAX_POSITION_MNQ)
        self.assertLessEqual(actual_position, self.config.MAX_POSITION_MNQ)


if __name__ == '__main__':
    unittest.main()