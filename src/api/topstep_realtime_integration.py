"""Integration module for TopStepX SignalR real-time data with the main bot"""
import asyncio
from typing import Dict, Optional, List, Callable, Any
from datetime import datetime, timedelta
from collections import deque

from src.api.topstep_signalr_client import TopStepXSignalRClient
from src.utils.logger_setup import logger


class TopStepXRealTimeDataManager:
    """Manages real-time data from TopStepX SignalR for bot integration"""
    
    def __init__(self, jwt_token: Optional[str] = None):
        self.signalr_client = TopStepXSignalRClient(jwt_token)
        
        # Data storage
        self.quotes: Dict[str, Dict] = {}
        self.trades: Dict[str, deque] = {}
        self.market_depth: Dict[str, Dict] = {}
        self.orders: Dict[str, Dict] = {}
        self.positions: Dict[str, Dict] = {}
        
        # Trade history settings
        self.max_trade_history = 1000
        
        # Callbacks for bot integration
        self.data_callbacks: Dict[str, List[Callable]] = {
            "quote_update": [],
            "trade_update": [],
            "depth_update": [],
            "order_update": [],
            "position_update": [],
            "fill_update": []
        }
        
        # Connection monitoring
        self.last_data_timestamp: Optional[datetime] = None
        self.data_timeout_seconds = 30
        
        # Subscribed contracts
        self.subscribed_contracts: List[str] = []
        
        self._setup_handlers()
        
    def _setup_handlers(self) -> None:
        """Setup SignalR event handlers"""
        self.signalr_client.on_quote(self._handle_quote)
        self.signalr_client.on_trade(self._handle_trade)
        self.signalr_client.on_market_depth(self._handle_depth)
        self.signalr_client.on_order_update(self._handle_order)
        self.signalr_client.on_position_update(self._handle_position)
        self.signalr_client.on_fill_update(self._handle_fill)
        self.signalr_client.on_connection_status(self._handle_connection_status)
    
    async def initialize(self, jwt_token: str) -> bool:
        """Initialize with JWT token and connect"""
        self.signalr_client.set_jwt_token(jwt_token)
        return await self.connect()
    
    async def connect(self) -> bool:
        """Connect to SignalR hubs"""
        try:
            connected = await self.signalr_client.connect()
            if connected:
                logger.info("Real-time data manager connected to SignalR")
                # Re-subscribe to previously subscribed contracts
                if self.subscribed_contracts:
                    await self.subscribe_to_contracts(self.subscribed_contracts)
            return connected
        except Exception as e:
            logger.error(f"Failed to connect real-time data manager: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from SignalR hubs"""
        await self.signalr_client.disconnect()
        logger.info("Real-time data manager disconnected")
    
    async def subscribe_to_contracts(self, contract_ids: List[str]) -> bool:
        """Subscribe to real-time data for contracts"""
        try:
            # Subscribe to all data types
            quote_sub = await self.signalr_client.subscribe_to_quotes(contract_ids)
            trade_sub = await self.signalr_client.subscribe_to_trades(contract_ids)
            depth_sub = await self.signalr_client.subscribe_to_market_depth(contract_ids, levels=10)
            
            if quote_sub and trade_sub and depth_sub:
                self.subscribed_contracts.extend(contract_ids)
                self.subscribed_contracts = list(set(self.subscribed_contracts))  # Remove duplicates
                logger.info(f"Subscribed to real-time data for: {contract_ids}")
                return True
            else:
                logger.error("Failed to subscribe to some data types")
                return False
                
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            return False
    
    async def unsubscribe_from_contracts(self, contract_ids: List[str]) -> bool:
        """Unsubscribe from real-time data for contracts"""
        try:
            result = await self.signalr_client.unsubscribe(contract_ids, "All")
            if result:
                for contract_id in contract_ids:
                    if contract_id in self.subscribed_contracts:
                        self.subscribed_contracts.remove(contract_id)
                logger.info(f"Unsubscribed from: {contract_ids}")
            return result
        except Exception as e:
            logger.error(f"Unsubscription error: {e}")
            return False
    
    # Data access methods for bot integration
    
    def get_latest_quote(self, contract_id: str) -> Optional[Dict]:
        """Get latest quote for a contract"""
        return self.quotes.get(contract_id)
    
    def get_bid_ask(self, contract_id: str) -> tuple:
        """Get current bid/ask prices"""
        quote = self.quotes.get(contract_id, {})
        return quote.get("bid", 0), quote.get("ask", 0)
    
    def get_spread(self, contract_id: str) -> float:
        """Get current bid-ask spread"""
        bid, ask = self.get_bid_ask(contract_id)
        return ask - bid if bid and ask else 0
    
    def get_recent_trades(self, contract_id: str, limit: int = 100) -> List[Dict]:
        """Get recent trades for a contract"""
        trades = self.trades.get(contract_id, deque())
        return list(trades)[-limit:]
    
    def get_volume_profile(self, contract_id: str, minutes: int = 5) -> Dict[float, int]:
        """Get volume profile for recent trades"""
        trades = self.get_recent_trades(contract_id, limit=1000)
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        volume_profile = {}
        for trade in trades:
            trade_time = datetime.fromisoformat(trade.get("timestamp", "").replace("Z", ""))
            if trade_time >= cutoff_time:
                price = trade.get("price", 0)
                size = trade.get("size", 0)
                volume_profile[price] = volume_profile.get(price, 0) + size
                
        return volume_profile
    
    def get_market_depth(self, contract_id: str) -> Optional[Dict]:
        """Get current market depth"""
        return self.market_depth.get(contract_id)
    
    def get_order_book_imbalance(self, contract_id: str) -> float:
        """Calculate order book imbalance (-1 to 1, negative = more sellers)"""
        depth = self.get_market_depth(contract_id)
        if not depth:
            return 0
            
        bids = depth.get("bids", [])
        asks = depth.get("asks", [])
        
        bid_volume = sum(level.get("size", 0) for level in bids)
        ask_volume = sum(level.get("size", 0) for level in asks)
        
        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            return 0
            
        return (bid_volume - ask_volume) / total_volume
    
    def get_positions(self) -> Dict[str, Dict]:
        """Get all current positions"""
        return self.positions.copy()
    
    def get_position(self, contract_id: str) -> Optional[Dict]:
        """Get position for specific contract"""
        for position in self.positions.values():
            if position.get("contractId") == contract_id:
                return position
        return None
    
    def get_orders(self, status: Optional[str] = None) -> List[Dict]:
        """Get orders, optionally filtered by status"""
        orders = list(self.orders.values())
        if status:
            orders = [o for o in orders if o.get("status") == status]
        return orders
    
    def is_data_stale(self) -> bool:
        """Check if real-time data is stale"""
        if not self.last_data_timestamp:
            return True
        
        time_since_data = (datetime.utcnow() - self.last_data_timestamp).total_seconds()
        return time_since_data > self.data_timeout_seconds
    
    # Callback registration for bot integration
    
    def on_quote_update(self, callback: Callable[[str, Dict], None]) -> None:
        """Register callback for quote updates"""
        self.data_callbacks["quote_update"].append(callback)
    
    def on_trade_update(self, callback: Callable[[str, Dict], None]) -> None:
        """Register callback for trade updates"""
        self.data_callbacks["trade_update"].append(callback)
    
    def on_depth_update(self, callback: Callable[[str, Dict], None]) -> None:
        """Register callback for market depth updates"""
        self.data_callbacks["depth_update"].append(callback)
    
    def on_order_update(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for order updates"""
        self.data_callbacks["order_update"].append(callback)
    
    def on_position_update(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for position updates"""
        self.data_callbacks["position_update"].append(callback)
    
    # Internal handlers
    
    def _handle_quote(self, quote: Dict) -> None:
        """Handle incoming quote data"""
        contract_id = quote.get("contractId")
        if contract_id:
            self.quotes[contract_id] = quote
            self.last_data_timestamp = datetime.utcnow()
            
            # Notify callbacks
            for callback in self.data_callbacks["quote_update"]:
                try:
                    callback(contract_id, quote)
                except Exception as e:
                    logger.error(f"Quote callback error: {e}")
    
    def _handle_trade(self, trade: Dict) -> None:
        """Handle incoming trade data"""
        contract_id = trade.get("contractId")
        if contract_id:
            if contract_id not in self.trades:
                self.trades[contract_id] = deque(maxlen=self.max_trade_history)
            
            self.trades[contract_id].append(trade)
            self.last_data_timestamp = datetime.utcnow()
            
            # Notify callbacks
            for callback in self.data_callbacks["trade_update"]:
                try:
                    callback(contract_id, trade)
                except Exception as e:
                    logger.error(f"Trade callback error: {e}")
    
    def _handle_depth(self, depth: Dict) -> None:
        """Handle incoming market depth data"""
        contract_id = depth.get("contractId")
        if contract_id:
            self.market_depth[contract_id] = depth
            self.last_data_timestamp = datetime.utcnow()
            
            # Notify callbacks
            for callback in self.data_callbacks["depth_update"]:
                try:
                    callback(contract_id, depth)
                except Exception as e:
                    logger.error(f"Depth callback error: {e}")
    
    def _handle_order(self, order: Dict) -> None:
        """Handle order updates"""
        order_id = order.get("orderId")
        if order_id:
            self.orders[order_id] = order
            
            # Remove cancelled/filled orders after some time
            status = order.get("status", "").lower()
            if status in ["filled", "cancelled", "rejected"]:
                asyncio.create_task(self._cleanup_order(order_id))
            
            # Notify callbacks
            for callback in self.data_callbacks["order_update"]:
                try:
                    callback(order)
                except Exception as e:
                    logger.error(f"Order callback error: {e}")
    
    def _handle_position(self, position: Dict) -> None:
        """Handle position updates"""
        position_id = position.get("positionId")
        if position_id:
            # Update or remove position based on quantity
            if position.get("quantity", 0) == 0:
                self.positions.pop(position_id, None)
            else:
                self.positions[position_id] = position
            
            # Notify callbacks
            for callback in self.data_callbacks["position_update"]:
                try:
                    callback(position)
                except Exception as e:
                    logger.error(f"Position callback error: {e}")
    
    def _handle_fill(self, fill: Dict) -> None:
        """Handle fill updates"""
        # Notify callbacks
        for callback in self.data_callbacks["fill_update"]:
            try:
                callback(fill)
            except Exception as e:
                logger.error(f"Fill callback error: {e}")
    
    def _handle_connection_status(self, status: str) -> None:
        """Handle connection status changes"""
        logger.info(f"SignalR connection status: {status}")
        
        if status == "disconnected":
            # Clear real-time data on disconnect
            self.last_data_timestamp = None
    
    async def _cleanup_order(self, order_id: str, delay: int = 300) -> None:
        """Remove completed orders after delay"""
        await asyncio.sleep(delay)
        self.orders.pop(order_id, None)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information"""
        return {
            "connected": self.signalr_client.is_connected,
            "connection_status": self.signalr_client.get_connection_status(),
            "subscribed_contracts": self.subscribed_contracts,
            "data_counts": {
                "quotes": len(self.quotes),
                "trades": sum(len(trades) for trades in self.trades.values()),
                "depth": len(self.market_depth),
                "orders": len(self.orders),
                "positions": len(self.positions)
            },
            "last_data_timestamp": self.last_data_timestamp.isoformat() if self.last_data_timestamp else None,
            "data_stale": self.is_data_stale()
        }


# Example bot integration
class BotRealTimeIntegration:
    """Example of integrating real-time data into bot logic"""
    
    def __init__(self, realtime_manager: TopStepXRealTimeDataManager):
        self.rtm = realtime_manager
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup real-time data callbacks"""
        self.rtm.on_quote_update(self._on_quote)
        self.rtm.on_trade_update(self._on_trade)
        self.rtm.on_order_update(self._on_order)
        self.rtm.on_position_update(self._on_position)
    
    def _on_quote(self, contract_id: str, quote: Dict) -> None:
        """Handle quote updates for trading decisions"""
        bid = quote.get("bid", 0)
        ask = quote.get("ask", 0)
        spread = ask - bid if bid and ask else 0
        
        # Example: Check for tight spreads for scalping
        if spread <= 0.10:  # $0.10 spread on micro gold
            logger.debug(f"Tight spread opportunity: {contract_id} - Spread: ${spread:.2f}")
    
    def _on_trade(self, contract_id: str, trade: Dict) -> None:
        """Handle trade updates for volume analysis"""
        # Example: Detect large trades
        size = trade.get("size", 0)
        if size >= 10:  # Large trade for micro gold
            logger.info(f"Large trade detected: {contract_id} - Size: {size} @ {trade.get('price')}")
    
    def _on_order(self, order: Dict) -> None:
        """Handle order updates"""
        status = order.get("status")
        order_id = order.get("orderId")
        
        if status == "filled":
            logger.info(f"Order filled: {order_id}")
        elif status == "rejected":
            logger.warning(f"Order rejected: {order_id}")
    
    def _on_position(self, position: Dict) -> None:
        """Handle position updates"""
        pnl = position.get("unrealizedPnL", 0)
        contract_id = position.get("contractId")
        
        # Example: Monitor P&L
        if pnl < -50:  # Loss exceeds $50
            logger.warning(f"Position loss alert: {contract_id} - PnL: ${pnl:.2f}")
    
    async def get_trading_signal(self, contract_id: str) -> Optional[str]:
        """Example of using real-time data for trading signals"""
        # Get current market data
        quote = self.rtm.get_latest_quote(contract_id)
        if not quote:
            return None
        
        # Check order book imbalance
        imbalance = self.rtm.get_order_book_imbalance(contract_id)
        
        # Get recent trade momentum
        recent_trades = self.rtm.get_recent_trades(contract_id, limit=50)
        if len(recent_trades) > 10:
            buy_volume = sum(t.get("size", 0) for t in recent_trades if t.get("side") == "Buy")
            sell_volume = sum(t.get("size", 0) for t in recent_trades if t.get("side") == "Sell")
            
            # Simple signal based on order flow
            if imbalance > 0.3 and buy_volume > sell_volume * 1.5:
                return "BUY"
            elif imbalance < -0.3 and sell_volume > buy_volume * 1.5:
                return "SELL"
        
        return None