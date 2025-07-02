"""Test script for partial profit taking system"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.partial_profit_manager import PartialProfitManager, PartialTarget, ManagedPosition
from src.config import Config
from src.utils.logger_setup import logger


class MockApiClient:
    """Mock API client for testing"""
    
    async def place_order(self, order_data):
        """Mock order placement"""
        logger.info(f"Mock placing order: {order_data}")
        return {
            'orderId': f"TEST_{order_data['customTag']}_{order_data['quantity']}",
            'success': True
        }
    
    async def cancel_order(self, order_id):
        """Mock order cancellation"""
        logger.info(f"Mock cancelling order: {order_id}")
        return True


async def test_partial_profit_calculations():
    """Test partial profit target calculations"""
    logger.info("=" * 80)
    logger.info("TESTING PARTIAL PROFIT CALCULATIONS")
    logger.info("=" * 80)
    
    # Create mock API client and manager
    api_client = MockApiClient()
    manager = PartialProfitManager(api_client)
    
    # Test BUY position
    logger.info("\n1. Testing BUY position targets:")
    logger.info("-" * 40)
    
    entry_price = 2650.00
    stop_price = 2645.00  # 5 points below entry
    total_quantity = 10
    
    targets = manager.calculate_partial_targets(
        side='BUY',
        entry_price=entry_price,
        stop_price=stop_price,
        total_quantity=total_quantity
    )
    
    logger.info(f"Entry: ${entry_price:.2f}")
    logger.info(f"Stop: ${stop_price:.2f} (Risk: ${entry_price - stop_price:.2f})")
    logger.info(f"Total Quantity: {total_quantity}")
    logger.info("\nTargets:")
    
    for target in targets:
        risk_reward = (target.price - entry_price) / (entry_price - stop_price)
        logger.info(f"  Target {target.target_level}: {target.quantity} @ ${target.price:.2f} "
                   f"(R:R = 1:{risk_reward:.1f}, {target.percentage*100:.0f}%)")
    
    # Test SELL position
    logger.info("\n2. Testing SELL position targets:")
    logger.info("-" * 40)
    
    entry_price = 2650.00
    stop_price = 2655.00  # 5 points above entry
    
    targets = manager.calculate_partial_targets(
        side='SELL',
        entry_price=entry_price,
        stop_price=stop_price,
        total_quantity=total_quantity
    )
    
    logger.info(f"Entry: ${entry_price:.2f}")
    logger.info(f"Stop: ${stop_price:.2f} (Risk: ${stop_price - entry_price:.2f})")
    logger.info(f"Total Quantity: {total_quantity}")
    logger.info("\nTargets:")
    
    for target in targets:
        risk_reward = (entry_price - target.price) / (stop_price - entry_price)
        logger.info(f"  Target {target.target_level}: {target.quantity} @ ${target.price:.2f} "
                   f"(R:R = 1:{risk_reward:.1f}, {target.percentage*100:.0f}%)")
    
    # Test custom percentages
    logger.info("\n3. Testing custom percentage split (60/30/10):")
    logger.info("-" * 40)
    
    custom_percentages = {1: 0.60, 2: 0.30, 3: 0.10}
    
    targets = manager.calculate_partial_targets(
        side='BUY',
        entry_price=2650.00,
        stop_price=2645.00,
        total_quantity=10,
        custom_percentages=custom_percentages
    )
    
    logger.info("Custom split targets:")
    for target in targets:
        logger.info(f"  Target {target.target_level}: {target.quantity} contracts ({target.percentage*100:.0f}%)")


async def test_managed_position_creation():
    """Test creating a managed position with partial orders"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING MANAGED POSITION CREATION")
    logger.info("=" * 80)
    
    api_client = MockApiClient()
    manager = PartialProfitManager(api_client)
    
    # Create a managed position
    position = await manager.create_managed_position(
        order_id="MAIN_001",
        side="BUY",
        quantity=10,
        entry_price=2650.00,
        stop_price=2645.00,
        contract_id="MNQ_123"
    )
    
    logger.info(f"\nCreated managed position: {position.order_id}")
    logger.info(f"Total Quantity: {position.total_quantity}")
    logger.info(f"Entry: ${position.entry_price:.2f}")
    logger.info(f"Stop: ${position.stop_price:.2f}")
    
    logger.info("\nPartial target orders placed:")
    for target in position.targets:
        logger.info(f"  Level {target.target_level}: {target.quantity} @ ${target.price:.2f} "
                   f"(Order ID: {target.order_id})")


async def test_partial_fill_handling():
    """Test handling of partial target fills"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING PARTIAL FILL HANDLING")
    logger.info("=" * 80)
    
    api_client = MockApiClient()
    manager = PartialProfitManager(api_client)
    
    # Create a managed position
    position = await manager.create_managed_position(
        order_id="MAIN_002",
        side="BUY",
        quantity=10,
        entry_price=2650.00,
        stop_price=2645.00,
        contract_id="MNQ_123"
    )
    
    # Simulate first target fill
    first_target = position.targets[0]
    logger.info(f"\nSimulating fill of Target 1...")
    
    await manager.handle_partial_fill(
        position_id="MAIN_002",
        filled_order_id=first_target.order_id,
        fill_price=first_target.price,
        fill_quantity=first_target.quantity
    )
    
    # Get position summary
    summary = manager.get_position_summary("MAIN_002")
    logger.info("\nPosition summary after first target:")
    logger.info(f"  Remaining Quantity: {summary['remaining_quantity']}")
    logger.info(f"  Realized P&L: ${summary['realized_pnl']:.2f}")
    logger.info(f"  Stop Adjusted: {summary['stop_adjusted']}")
    logger.info(f"  Filled Targets: {summary['filled_targets']}")
    logger.info(f"  Unfilled Targets: {summary['unfilled_targets']}")


async def test_stop_adjustment():
    """Test stop adjustment to breakeven"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING STOP ADJUSTMENT")
    logger.info("=" * 80)
    
    api_client = MockApiClient()
    manager = PartialProfitManager(api_client)
    
    # Test BUY position stop adjustment
    position = ManagedPosition(
        order_id="TEST_003",
        side="BUY",
        total_quantity=10,
        entry_price=2650.00,
        stop_price=2645.00,
        original_stop_price=2645.00,
        targets=[],
        remaining_quantity=5
    )
    
    manager.managed_positions["TEST_003"] = position
    
    logger.info("Before adjustment:")
    logger.info(f"  Entry: ${position.entry_price:.2f}")
    logger.info(f"  Stop: ${position.stop_price:.2f}")
    
    await manager.adjust_stop_to_breakeven(position)
    
    logger.info("After adjustment:")
    logger.info(f"  New Stop: ${position.stop_price:.2f}")
    logger.info(f"  Stop Adjusted: {position.is_stop_adjusted}")


async def main():
    """Run all tests"""
    try:
        await test_partial_profit_calculations()
        await test_managed_position_creation()
        await test_partial_fill_handling()
        await test_stop_adjustment()
        
        logger.info("\n" + "=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())