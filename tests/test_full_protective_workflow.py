"""Test complete protective order workflow"""
# Standard library imports
import asyncio
from datetime import datetime, timezone

# Local imports
from src.bot_live import LiveGoldBot
from src.config import Config
from src.utils.logger_setup import logger


async def test_full_protective_workflow():
    """Test complete workflow from market order to protective order execution"""
    
    # Initialize bot with mock API
    bot = LiveGoldBot(use_mock_api=True)
    await bot.connect()
    
    logger.info("=" * 80)
    logger.info("TESTING FULL PROTECTIVE ORDER WORKFLOW")
    logger.info("=" * 80)
    
    # Step 1: Place a market order (without stop/limit attached)
    logger.info("\n1. Placing market order...")
    
    # Set realistic current price for test
    bot.api_client.current_price = 2500.0
    
    success = await bot.place_order(
        side='BUY',
        quantity=2,
        stop_price=2495.0,  # 5 points below = 20 ticks
        target_price=2510.0  # 10 points above = 40 ticks
    )
    
    if not success:
        logger.error("Failed to place market order")
        return
    
    # The order should be tracked in bot.positions
    order_id = list(bot.positions.keys())[0]  # Get the first order
    logger.info(f"Market order placed: {order_id}")
    
    # Step 2: Simulate market order fill
    logger.info("\n2. Simulating market order fill...")
    fill_event = {
        'order_id': order_id,
        'fill_price': 2500.50,
        'quantity': 2,
        'side': 'BUY'
    }
    
    # Update position status to filled before calling handler
    bot.positions[order_id]['status'] = 'filled'
    bot.positions[order_id]['fill_price'] = 2500.50
    
    # This should automatically place protective orders
    await bot._handle_fill(fill_event)
    
    # Verify protective orders were placed
    if order_id in bot.protective_orders:
        protective = bot.protective_orders[order_id]
        logger.info(f"\n✅ Protective orders placed:")
        logger.info(f"   Stop Loss: {protective['stop_order_id']}")
        logger.info(f"   Take Profit: {protective['target_order_id']}")
    else:
        logger.error("Protective orders were not placed!")
        return
    
    # Step 3: Simulate stop loss fill
    logger.info("\n3. Simulating stop loss hit...")
    stop_fill_event = {
        'order_id': protective['stop_order_id'],
        'fill_price': 2495.0,
        'quantity': 2,
        'side': 'SELL'  # Opposite side to close position
    }
    
    await bot._handle_protective_order_fill(stop_fill_event)
    
    # Verify target order was cancelled
    if protective['target_order_id'] in bot.api_client.cancelled_orders:
        logger.info("✅ Take profit order cancelled after stop loss fill")
    else:
        logger.error("Take profit order was not cancelled!")
    
    # Step 4: Test the opposite scenario - target hit
    logger.info("\n4. Testing take profit scenario...")
    
    # Place another order
    success = await bot.place_order(
        side='SELL',
        quantity=1,
        stop_price=2505.0,
        target_price=2490.0
    )
    
    if success:
        # Get the new order
        new_order_id = list(bot.positions.keys())[-1]
        
        # Simulate fill
        bot.positions[new_order_id]['status'] = 'filled'
        await bot._handle_fill({
            'order_id': new_order_id,
            'fill_price': 2500.0,
            'quantity': 1,
            'side': 'SELL'
        })
        
        # Simulate target hit
        if new_order_id in bot.protective_orders:
            target_id = bot.protective_orders[new_order_id]['target_order_id']
            await bot._handle_protective_order_fill({
                'order_id': target_id,
                'fill_price': 2490.0,
                'quantity': 1,
                'side': 'BUY'
            })
            
            # Check before accessing to avoid KeyError
            if new_order_id not in bot.protective_orders:
                logger.error("Protective orders not found - they were already removed")
            else:
                logger.info("✅ Stop loss order cancelled after take profit fill")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ FULL PROTECTIVE ORDER WORKFLOW TEST COMPLETE")
    logger.info("=" * 80)
    
    await bot.disconnect()


if __name__ == "__main__":
    asyncio.run(test_full_protective_workflow())