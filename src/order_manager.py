"""
Order Manager for T-BOT
Handles bracket orders, OCO logic, order state tracking, and partial fills
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import asyncio
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class OrderState(Enum):
    """Order state enumeration"""
    PENDING = "pending"
    WORKING = "working"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Order data structure"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    state: OrderState = OrderState.PENDING
    filled_quantity: int = 0
    average_fill_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    parent_order_id: Optional[str] = None
    linked_orders: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BracketOrder:
    """Bracket order structure containing entry, stop loss, and target orders"""
    entry_order: Order
    stop_loss_order: Order
    target_order: Order
    is_oco_active: bool = True


class OrderManager:
    """Manages orders, bracket orders, and OCO relationships"""
    
    def __init__(self, api_client):
        """
        Initialize OrderManager
        
        Args:
            api_client: TopstepClient instance for order execution
        """
        self.api_client = api_client
        self.orders: Dict[str, Order] = {}
        self.bracket_orders: Dict[str, BracketOrder] = {}
        self.oco_groups: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()
        logger.info("OrderManager initialized")
    
    async def place_bracket_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        entry_type: OrderType = OrderType.MARKET,
        entry_price: Optional[float] = None,
        stop_loss_price: float = None,
        target_price: float = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[BracketOrder], Optional[str]]:
        """
        Place a bracket order (entry + stop loss + target)
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY/SELL)
            quantity: Order quantity
            entry_type: Entry order type
            entry_price: Entry limit price (if limit order)
            stop_loss_price: Stop loss price
            target_price: Target/take profit price
            metadata: Additional order metadata
            
        Returns:
            Tuple of (success, BracketOrder or None, error_message or None)
        """
        async with self._lock:
            try:
                # Create entry order
                entry_order = Order(
                    order_id=self._generate_order_id(),
                    symbol=symbol,
                    side=side,
                    order_type=entry_type,
                    quantity=quantity,
                    price=entry_price,
                    metadata=metadata or {}
                )
                
                # Determine opposite side for exit orders
                exit_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
                
                # Create stop loss order
                stop_loss_order = Order(
                    order_id=self._generate_order_id(),
                    symbol=symbol,
                    side=exit_side,
                    order_type=OrderType.STOP,
                    quantity=quantity,
                    stop_price=stop_loss_price,
                    parent_order_id=entry_order.order_id,
                    metadata=metadata or {}
                )
                
                # Create target order
                target_order = Order(
                    order_id=self._generate_order_id(),
                    symbol=symbol,
                    side=exit_side,
                    order_type=OrderType.LIMIT,
                    quantity=quantity,
                    price=target_price,
                    parent_order_id=entry_order.order_id,
                    metadata=metadata or {}
                )
                
                # Link orders together
                entry_order.linked_orders = [stop_loss_order.order_id, target_order.order_id]
                stop_loss_order.linked_orders = [target_order.order_id]
                target_order.linked_orders = [stop_loss_order.order_id]
                
                # Create bracket order structure
                bracket_order = BracketOrder(
                    entry_order=entry_order,
                    stop_loss_order=stop_loss_order,
                    target_order=target_order
                )
                
                # Place entry order
                success, result = await self._place_order(entry_order)
                if not success:
                    return False, None, f"Failed to place entry order: {result}"
                
                # Store orders
                self.orders[entry_order.order_id] = entry_order
                self.orders[stop_loss_order.order_id] = stop_loss_order
                self.orders[target_order.order_id] = target_order
                
                # Store bracket order
                self.bracket_orders[entry_order.order_id] = bracket_order
                
                # Create OCO group for exit orders
                oco_group_id = f"oco_{entry_order.order_id}"
                self.oco_groups[oco_group_id] = [stop_loss_order.order_id, target_order.order_id]
                
                logger.info(f"Bracket order placed successfully: {entry_order.order_id}")
                return True, bracket_order, None
                
            except Exception as e:
                logger.error(f"Error placing bracket order: {e}")
                return False, None, str(e)
    
    async def update_order_state(
        self,
        order_id: str,
        new_state: OrderState,
        filled_quantity: Optional[int] = None,
        average_fill_price: Optional[float] = None
    ) -> bool:
        """
        Update order state and handle OCO logic
        
        Args:
            order_id: Order ID to update
            new_state: New order state
            filled_quantity: Filled quantity (for partial/full fills)
            average_fill_price: Average fill price
            
        Returns:
            Success status
        """
        async with self._lock:
            if order_id not in self.orders:
                logger.warning(f"Order not found: {order_id}")
                return False
            
            order = self.orders[order_id]
            old_state = order.state
            order.state = new_state
            order.updated_at = datetime.now()
            
            # Update fill information
            if filled_quantity is not None:
                order.filled_quantity = filled_quantity
            if average_fill_price is not None:
                order.average_fill_price = average_fill_price
            
            logger.info(f"Order {order_id} state updated: {old_state} -> {new_state}")
            
            # Handle state-specific logic
            if new_state == OrderState.FILLED:
                await self._handle_order_filled(order)
            elif new_state == OrderState.PARTIALLY_FILLED:
                await self._handle_partial_fill(order)
            elif new_state in [OrderState.CANCELLED, OrderState.REJECTED]:
                await self._handle_order_cancelled(order)
            
            return True
    
    async def _handle_order_filled(self, order: Order):
        """Handle order filled event"""
        # Check if this is an entry order
        if order.order_id in self.bracket_orders:
            bracket = self.bracket_orders[order.order_id]
            # Place exit orders (stop loss and target)
            await self._place_order(bracket.stop_loss_order)
            await self._place_order(bracket.target_order)
            logger.info(f"Exit orders placed for filled entry order: {order.order_id}")
        
        # Check if this is an exit order with OCO
        await self._handle_oco_fill(order)
    
    async def _handle_partial_fill(self, order: Order):
        """Handle partial fill event"""
        logger.info(f"Partial fill for order {order.order_id}: {order.filled_quantity}/{order.quantity}")
        
        # Update linked orders quantities if this is an entry order
        if order.order_id in self.bracket_orders:
            bracket = self.bracket_orders[order.order_id]
            remaining_quantity = order.quantity - order.filled_quantity
            
            # Update exit order quantities
            bracket.stop_loss_order.quantity = order.filled_quantity
            bracket.target_order.quantity = order.filled_quantity
            
            logger.info(f"Updated exit order quantities to {order.filled_quantity}")
    
    async def _handle_order_cancelled(self, order: Order):
        """Handle order cancelled event"""
        logger.info(f"Order cancelled: {order.order_id}")
        
        # If entry order cancelled, cancel exit orders
        if order.order_id in self.bracket_orders:
            bracket = self.bracket_orders[order.order_id]
            await self.cancel_order(bracket.stop_loss_order.order_id)
            await self.cancel_order(bracket.target_order.order_id)
    
    async def _handle_oco_fill(self, filled_order: Order):
        """Handle OCO (One-Cancels-Other) logic when an order is filled"""
        # Find OCO group containing this order
        for group_id, order_ids in self.oco_groups.items():
            if filled_order.order_id in order_ids:
                # Cancel other orders in the group
                for other_order_id in order_ids:
                    if other_order_id != filled_order.order_id:
                        other_order = self.orders.get(other_order_id)
                        if other_order and other_order.state in [OrderState.PENDING, OrderState.WORKING]:
                            await self.cancel_order(other_order_id)
                            logger.info(f"OCO: Cancelled order {other_order_id} due to fill of {filled_order.order_id}")
                
                # Remove OCO group
                del self.oco_groups[group_id]
                break
    
    async def cancel_order(self, order_id: str) -> Tuple[bool, Optional[str]]:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Tuple of (success, error_message or None)
        """
        async with self._lock:
            if order_id not in self.orders:
                return False, f"Order not found: {order_id}"
            
            order = self.orders[order_id]
            if order.state in [OrderState.FILLED, OrderState.CANCELLED]:
                return False, f"Cannot cancel order in state: {order.state}"
            
            # Call API to cancel order
            success, result = await self._cancel_order_api(order)
            if success:
                order.state = OrderState.CANCELLED
                order.updated_at = datetime.now()
                logger.info(f"Order cancelled: {order_id}")
                return True, None
            else:
                return False, result
    
    async def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get current order status"""
        return self.orders.get(order_id)
    
    async def get_bracket_order_status(self, entry_order_id: str) -> Optional[BracketOrder]:
        """Get bracket order status"""
        return self.bracket_orders.get(entry_order_id)
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders, optionally filtered by symbol"""
        open_states = [OrderState.PENDING, OrderState.WORKING, OrderState.PARTIALLY_FILLED]
        orders = [
            order for order in self.orders.values()
            if order.state in open_states and (symbol is None or order.symbol == symbol)
        ]
        return orders
    
    async def modify_order(
        self,
        order_id: str,
        new_quantity: Optional[int] = None,
        new_price: Optional[float] = None,
        new_stop_price: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Modify an existing order
        
        Args:
            order_id: Order ID to modify
            new_quantity: New quantity
            new_price: New limit price
            new_stop_price: New stop price
            
        Returns:
            Tuple of (success, error_message or None)
        """
        async with self._lock:
            if order_id not in self.orders:
                return False, f"Order not found: {order_id}"
            
            order = self.orders[order_id]
            if order.state not in [OrderState.PENDING, OrderState.WORKING]:
                return False, f"Cannot modify order in state: {order.state}"
            
            # Update order fields
            if new_quantity is not None:
                order.quantity = new_quantity
            if new_price is not None:
                order.price = new_price
            if new_stop_price is not None:
                order.stop_price = new_stop_price
            
            order.updated_at = datetime.now()
            
            # Call API to modify order
            success, result = await self._modify_order_api(order)
            if success:
                logger.info(f"Order modified: {order_id}")
                return True, None
            else:
                return False, result
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        import uuid
        return f"order_{uuid.uuid4().hex[:8]}"
    
    async def _place_order(self, order: Order) -> Tuple[bool, Any]:
        """Place order via API"""
        try:
            # Map internal order to API format
            api_order = {
                "symbol": order.symbol,
                "side": order.side.value,
                "quantity": order.quantity,
                "orderType": order.order_type.value,
                "price": order.price,
                "stopPrice": order.stop_price
            }
            
            # Call API
            result = await self.api_client.place_order(api_order)
            
            if result and "orderId" in result:
                # Update order with API order ID
                order.metadata["api_order_id"] = result["orderId"]
                order.state = OrderState.WORKING
                return True, result
            else:
                order.state = OrderState.REJECTED
                return False, "Order rejected by API"
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            order.state = OrderState.REJECTED
            return False, str(e)
    
    async def _cancel_order_api(self, order: Order) -> Tuple[bool, Any]:
        """Cancel order via API"""
        try:
            api_order_id = order.metadata.get("api_order_id")
            if not api_order_id:
                return False, "No API order ID found"
            
            result = await self.api_client.cancel_order(api_order_id)
            return True, result
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False, str(e)
    
    async def _modify_order_api(self, order: Order) -> Tuple[bool, Any]:
        """Modify order via API"""
        try:
            api_order_id = order.metadata.get("api_order_id")
            if not api_order_id:
                return False, "No API order ID found"
            
            # Map internal order to API format
            api_updates = {
                "quantity": order.quantity,
                "price": order.price,
                "stopPrice": order.stop_price
            }
            
            result = await self.api_client.modify_order(api_order_id, api_updates)
            return True, result
            
        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            return False, str(e)
    
    def get_integration_interface(self):
        """
        Get integration interface for bot_live.py
        
        Returns dict with methods for bot integration
        """
        return {
            "place_bracket_order": self.place_bracket_order,
            "cancel_order": self.cancel_order,
            "update_order_state": self.update_order_state,
            "get_order_status": self.get_order_status,
            "get_open_orders": self.get_open_orders,
            "modify_order": self.modify_order,
            "get_bracket_order_status": self.get_bracket_order_status
        }