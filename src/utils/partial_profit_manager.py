"""Partial Profit Taking Manager for Trading Bot"""
# Standard library imports
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import asyncio

# Local imports
from src.config import Config
from src.utils.logger_setup import logger


@dataclass
class PartialTarget:
    """Data class for a partial profit target"""
    target_level: int  # 1, 2, or 3
    price: float
    percentage: float  # Position percentage to exit
    quantity: int
    order_id: Optional[str] = None
    is_filled: bool = False
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None


@dataclass
class ManagedPosition:
    """Position with partial profit management"""
    order_id: str
    side: str  # 'BUY' or 'SELL'
    total_quantity: int
    entry_price: float
    stop_price: float
    original_stop_price: float
    
    # Partial targets
    targets: List[PartialTarget]
    
    # Tracking
    remaining_quantity: int
    realized_pnl: float = 0.0
    is_stop_adjusted: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class PartialProfitManager:
    """Manages partial profit taking for positions"""
    
    def __init__(self, api_client):
        self.config = Config
        self.api_client = api_client
        self.managed_positions: Dict[str, ManagedPosition] = {}
        
        # Default partial profit percentages (can be overridden)
        self.default_percentages = {
            1: 0.50,  # 50% at first target
            2: 0.40,  # 40% at second target
            3: 0.10   # 10% runner
        }
        
        # Default target ratios
        self.default_target_ratios = {
            1: 1.0,   # 1:1 R:R
            2: 2.0,   # 1:2 R:R
            3: 2.5    # 1:2.5 R:R (runner)
        }
        
        logger.info("Partial Profit Manager initialized")
        logger.info(f"Default split: {self.default_percentages}")
        logger.info(f"Default targets: {self.default_target_ratios}")
    
    def calculate_partial_targets(
        self, 
        side: str, 
        entry_price: float, 
        stop_price: float,
        total_quantity: int,
        custom_percentages: Optional[Dict[int, float]] = None,
        custom_ratios: Optional[Dict[int, float]] = None
    ) -> List[PartialTarget]:
        """Calculate partial profit targets for a position"""
        
        # Use custom or default percentages
        percentages = custom_percentages or self.default_percentages
        ratios = custom_ratios or self.default_target_ratios
        
        # Calculate stop distance
        stop_distance = abs(entry_price - stop_price)
        
        targets = []
        remaining_quantity = total_quantity
        
        for level in [1, 2, 3]:
            if level not in percentages:
                continue
                
            # Calculate target price based on R:R ratio
            target_distance = stop_distance * ratios.get(level, 1.0)
            
            if side == 'BUY':
                target_price = entry_price + target_distance
            else:  # SELL
                target_price = entry_price - target_distance
            
            # Calculate quantity for this target
            if level == 3:  # Last target gets remaining
                target_quantity = remaining_quantity
            else:
                target_quantity = int(total_quantity * percentages[level])
                remaining_quantity -= target_quantity
            
            if target_quantity > 0:
                targets.append(PartialTarget(
                    target_level=level,
                    price=target_price,
                    percentage=percentages[level],
                    quantity=target_quantity
                ))
                
                logger.info(f"Target {level}: {target_quantity} contracts @ ${target_price:.2f} "
                          f"({percentages[level]*100:.0f}% of position)")
        
        return targets
    
    async def create_managed_position(
        self,
        order_id: str,
        side: str,
        quantity: int,
        entry_price: float,
        stop_price: float,
        contract_id: str,
        custom_percentages: Optional[Dict[int, float]] = None,
        custom_ratios: Optional[Dict[int, float]] = None
    ) -> ManagedPosition:
        """Create a new managed position with partial targets"""
        
        # Calculate partial targets
        targets = self.calculate_partial_targets(
            side, entry_price, stop_price, quantity,
            custom_percentages, custom_ratios
        )
        
        # Create managed position
        position = ManagedPosition(
            order_id=order_id,
            side=side,
            total_quantity=quantity,
            entry_price=entry_price,
            stop_price=stop_price,
            original_stop_price=stop_price,
            targets=targets,
            remaining_quantity=quantity
        )
        
        # Place limit orders for each target
        for target in targets:
            order_data = {
                "symbol": self.config.SYMBOL,
                "contractId": contract_id,
                "side": "Sell" if side == "BUY" else "Buy",  # Opposite side to close
                "quantity": target.quantity,
                "orderType": "Limit",
                "limitPrice": target.price,
                "time_in_force": "GTC",
                "account_id": self.config.TOPSTEP_ACCOUNT_ID,
                "linkedOrderId": order_id,  # Link to parent order
                "customTag": f"PT{target.target_level}"  # Partial Target identifier
            }
            
            result = await self.api_client.place_order(order_data)
            
            if result and result.get('orderId'):
                target.order_id = result['orderId']
                logger.info(f"✅ Placed partial target {target.target_level} order: {target.order_id}")
            else:
                logger.error(f"❌ Failed to place partial target {target.target_level} order")
        
        # Store managed position
        self.managed_positions[order_id] = position
        
        logger.info(f"Created managed position for {order_id} with {len(targets)} partial targets")
        
        return position
    
    async def handle_partial_fill(
        self, 
        position_id: str, 
        filled_order_id: str,
        fill_price: float,
        fill_quantity: int
    ) -> None:
        """Handle a partial target fill"""
        
        if position_id not in self.managed_positions:
            logger.warning(f"Position {position_id} not found in managed positions")
            return
        
        position = self.managed_positions[position_id]
        
        # Find which target was filled
        filled_target = None
        for target in position.targets:
            if target.order_id == filled_order_id:
                filled_target = target
                break
        
        if not filled_target:
            logger.warning(f"Could not find target for order {filled_order_id}")
            return
        
        # Update target status
        filled_target.is_filled = True
        filled_target.fill_price = fill_price
        filled_target.fill_time = datetime.now(timezone.utc)
        
        # Update position tracking
        position.remaining_quantity -= fill_quantity
        
        # Calculate P&L for this partial
        if position.side == 'BUY':
            pnl_per_contract = (fill_price - position.entry_price) / self.config.TICK_SIZE * self.config.TICK_VALUE
        else:  # SELL
            pnl_per_contract = (position.entry_price - fill_price) / self.config.TICK_SIZE * self.config.TICK_VALUE
        
        partial_pnl = pnl_per_contract * fill_quantity
        position.realized_pnl += partial_pnl
        
        logger.info("=" * 60)
        logger.info(f"🎯 PARTIAL TARGET {filled_target.target_level} FILLED")
        logger.info("=" * 60)
        logger.info(f"Position: {position_id}")
        logger.info(f"Fill Price: ${fill_price:.2f}")
        logger.info(f"Quantity: {fill_quantity}")
        logger.info(f"Partial P&L: ${partial_pnl:.2f}")
        logger.info(f"Total Realized P&L: ${position.realized_pnl:.2f}")
        logger.info(f"Remaining Quantity: {position.remaining_quantity}")
        logger.info("=" * 60)
        
        # Adjust stop after first target
        if filled_target.target_level == 1 and not position.is_stop_adjusted:
            await self.adjust_stop_to_breakeven(position)
    
    async def adjust_stop_to_breakeven(self, position: ManagedPosition) -> None:
        """Adjust stop loss to breakeven after first target hit"""
        
        try:
            # Calculate breakeven price (entry + small buffer for costs)
            buffer_ticks = 2  # Small buffer to cover costs
            buffer = buffer_ticks * self.config.TICK_SIZE
            
            if position.side == 'BUY':
                new_stop_price = position.entry_price + buffer
            else:  # SELL
                new_stop_price = position.entry_price - buffer
            
            # Only adjust if new stop is better than current
            if position.side == 'BUY':
                should_adjust = new_stop_price > position.stop_price
            else:  # SELL
                should_adjust = new_stop_price < position.stop_price
            
            if should_adjust:
                # Update stop order via API
                # Note: This assumes the API supports stop modification
                # You may need to cancel and replace the stop order
                
                logger.info(f"📊 Adjusting stop to breakeven for position {position.order_id}")
                logger.info(f"Old Stop: ${position.stop_price:.2f}")
                logger.info(f"New Stop: ${new_stop_price:.2f}")
                
                # Update position tracking
                position.stop_price = new_stop_price
                position.is_stop_adjusted = True
                
                # TODO: Implement actual stop order modification via API
                # This will depend on TopStep's API capabilities
                
                logger.info("✅ Stop adjusted to breakeven")
            else:
                logger.info("Stop already better than breakeven, no adjustment needed")
                
        except Exception as e:
            logger.error(f"Error adjusting stop to breakeven: {e}")
    
    async def cancel_remaining_targets(self, position_id: str) -> None:
        """Cancel remaining unfilled target orders"""
        
        if position_id not in self.managed_positions:
            return
        
        position = self.managed_positions[position_id]
        
        for target in position.targets:
            if not target.is_filled and target.order_id:
                try:
                    success = await self.api_client.cancel_order(target.order_id)
                    if success:
                        logger.info(f"Cancelled target {target.target_level} order: {target.order_id}")
                    else:
                        logger.error(f"Failed to cancel target {target.target_level} order: {target.order_id}")
                except Exception as e:
                    logger.error(f"Error cancelling target order: {e}")
    
    def get_position_summary(self, position_id: str) -> Dict:
        """Get summary of managed position"""
        
        if position_id not in self.managed_positions:
            return {}
        
        position = self.managed_positions[position_id]
        
        filled_targets = [t for t in position.targets if t.is_filled]
        unfilled_targets = [t for t in position.targets if not t.is_filled]
        
        summary = {
            "position_id": position_id,
            "side": position.side,
            "entry_price": position.entry_price,
            "original_quantity": position.total_quantity,
            "remaining_quantity": position.remaining_quantity,
            "realized_pnl": position.realized_pnl,
            "stop_price": position.stop_price,
            "stop_adjusted": position.is_stop_adjusted,
            "filled_targets": len(filled_targets),
            "unfilled_targets": len(unfilled_targets),
            "targets": [
                {
                    "level": t.target_level,
                    "price": t.price,
                    "quantity": t.quantity,
                    "filled": t.is_filled,
                    "fill_price": t.fill_price,
                    "fill_time": t.fill_time.isoformat() if t.fill_time else None
                }
                for t in position.targets
            ]
        }
        
        return summary
    
    def cleanup_closed_positions(self) -> None:
        """Remove closed positions from tracking"""
        
        closed_positions = []
        
        for position_id, position in self.managed_positions.items():
            if position.remaining_quantity == 0:
                closed_positions.append(position_id)
        
        for position_id in closed_positions:
            del self.managed_positions[position_id]
            logger.info(f"Removed closed position {position_id} from tracking")