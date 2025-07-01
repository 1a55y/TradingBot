"""TopStepX SignalR Client for Real-time Data"""
import asyncio
import json
import logging
from typing import Dict, Optional, List, Any, Callable
from datetime import datetime
from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.protocol.messagepack_protocol import MessagePackHubProtocol
from signalrcore.subject import Subject

from src.utils.logger_setup import logger
from src.config import Config


class TopStepXSignalRClient:
    """SignalR client for TopStepX real-time market and trading data"""
    
    def __init__(self, jwt_token: Optional[str] = None):
        self.config = Config
        self.jwt_token = jwt_token
        
        # SignalR hub URLs
        self.market_hub_url = "wss://rtc.topstepx.com/hubs/market"
        self.user_hub_url = "wss://rtc.topstepx.com/hubs/user"
        
        # Hub connections
        self.market_hub: Optional[Any] = None
        self.user_hub: Optional[Any] = None
        
        # Connection state
        self.is_connected = False
        self.market_connected = False
        self.user_connected = False
        
        # Subscriptions
        self.market_subscriptions: Dict[str, List[str]] = {
            "quotes": [],
            "trades": [],
            "depth": []
        }
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "quote": [],
            "trade": [],
            "depth": [],
            "order": [],
            "position": [],
            "fill": [],
            "connection_status": []
        }
        
        # Reconnection settings
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # seconds
        
        logger.info("TopStepX SignalR Client initialized")
    
    def set_jwt_token(self, token: str) -> None:
        """Set or update JWT token for authentication"""
        self.jwt_token = token
        logger.info("JWT token updated")
    
    async def connect(self) -> bool:
        """Connect to SignalR hubs"""
        try:
            if not self.jwt_token:
                logger.error("No JWT token provided for SignalR connection")
                return False
            
            # Connect to market hub
            market_connected = await self._connect_market_hub()
            
            # Connect to user hub
            user_connected = await self._connect_user_hub()
            
            self.is_connected = market_connected or user_connected
            
            if self.is_connected:
                logger.info("Successfully connected to SignalR hubs")
                await self._notify_connection_status("connected")
            else:
                logger.error("Failed to connect to any SignalR hub")
                
            return self.is_connected
            
        except Exception as e:
            logger.error(f"SignalR connection error: {e}")
            return False
    
    async def _connect_market_hub(self) -> bool:
        """Connect to market data hub"""
        try:
            # Build connection with JWT token in query string
            self.market_hub = HubConnectionBuilder()\
                .with_url(
                    f"{self.market_hub_url}?access_token={self.jwt_token}",
                    options={
                        "skip_negotiation": True,
                        "headers": {
                            "User-Agent": "TopStepX-Python-Client/1.0"
                        }
                    }
                )\
                .configure_logging(logging.INFO)\
                .with_automatic_reconnect({
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 20
                })\
                .build()
            
            # Register event handlers
            self.market_hub.on_open(self._on_market_open)
            self.market_hub.on_close(self._on_market_close)
            self.market_hub.on_error(self._on_market_error)
            
            # Register market data handlers
            self.market_hub.on("Quote", self._on_quote)
            self.market_hub.on("Trade", self._on_trade)
            self.market_hub.on("MarketDepth", self._on_market_depth)
            self.market_hub.on("MarketStatus", self._on_market_status)
            
            # Start connection
            self.market_hub.start()
            
            # Wait for connection
            await asyncio.sleep(2)
            
            if self.market_hub and hasattr(self.market_hub, 'transport') and self.market_hub.transport:
                self.market_connected = True
                logger.info("Connected to market data hub")
                return True
            else:
                logger.error("Failed to establish market hub connection")
                return False
                
        except Exception as e:
            logger.error(f"Market hub connection error: {e}")
            return False
    
    async def _connect_user_hub(self) -> bool:
        """Connect to user/trading hub"""
        try:
            # Build connection with JWT token
            self.user_hub = HubConnectionBuilder()\
                .with_url(
                    f"{self.user_hub_url}?access_token={self.jwt_token}",
                    options={
                        "skip_negotiation": True,
                        "headers": {
                            "User-Agent": "TopStepX-Python-Client/1.0"
                        }
                    }
                )\
                .configure_logging(logging.INFO)\
                .with_automatic_reconnect({
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 20
                })\
                .build()
            
            # Register event handlers
            self.user_hub.on_open(self._on_user_open)
            self.user_hub.on_close(self._on_user_close)
            self.user_hub.on_error(self._on_user_error)
            
            # Register trading event handlers
            self.user_hub.on("OrderUpdate", self._on_order_update)
            self.user_hub.on("PositionUpdate", self._on_position_update)
            self.user_hub.on("FillUpdate", self._on_fill_update)
            self.user_hub.on("AccountUpdate", self._on_account_update)
            
            # Start connection
            self.user_hub.start()
            
            # Wait for connection
            await asyncio.sleep(2)
            
            if self.user_hub and hasattr(self.user_hub, 'transport') and self.user_hub.transport:
                self.user_connected = True
                logger.info("Connected to user/trading hub")
                return True
            else:
                logger.error("Failed to establish user hub connection")
                return False
                
        except Exception as e:
            logger.error(f"User hub connection error: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from SignalR hubs"""
        try:
            if self.market_hub:
                self.market_hub.stop()
                self.market_connected = False
                logger.info("Disconnected from market hub")
                
            if self.user_hub:
                self.user_hub.stop()
                self.user_connected = False
                logger.info("Disconnected from user hub")
                
            self.is_connected = False
            await self._notify_connection_status("disconnected")
            
        except Exception as e:
            logger.error(f"Error during SignalR disconnect: {e}")
    
    # Market Data Subscription Methods
    
    async def subscribe_to_quotes(self, contract_ids: List[str]) -> bool:
        """Subscribe to real-time quotes for specified contracts"""
        try:
            if not self.market_connected:
                logger.error("Market hub not connected")
                return False
            
            # TopStepX uses CONTRACT_ID format like 'CON.F.US.MGC.Q25'
            subscribe_data = {
                "contractIds": contract_ids,
                "subscriptionType": "Quote"
            }
            
            self.market_hub.send("Subscribe", [subscribe_data])
            
            # Track subscriptions
            self.market_subscriptions["quotes"].extend(contract_ids)
            
            logger.info(f"Subscribed to quotes for: {contract_ids}")
            return True
            
        except Exception as e:
            logger.error(f"Quote subscription error: {e}")
            return False
    
    async def subscribe_to_trades(self, contract_ids: List[str]) -> bool:
        """Subscribe to real-time trades for specified contracts"""
        try:
            if not self.market_connected:
                logger.error("Market hub not connected")
                return False
            
            subscribe_data = {
                "contractIds": contract_ids,
                "subscriptionType": "Trade"
            }
            
            self.market_hub.send("Subscribe", [subscribe_data])
            
            # Track subscriptions
            self.market_subscriptions["trades"].extend(contract_ids)
            
            logger.info(f"Subscribed to trades for: {contract_ids}")
            return True
            
        except Exception as e:
            logger.error(f"Trade subscription error: {e}")
            return False
    
    async def subscribe_to_market_depth(self, contract_ids: List[str], levels: int = 5) -> bool:
        """Subscribe to market depth (order book) for specified contracts"""
        try:
            if not self.market_connected:
                logger.error("Market hub not connected")
                return False
            
            subscribe_data = {
                "contractIds": contract_ids,
                "subscriptionType": "MarketDepth",
                "depthLevels": levels
            }
            
            self.market_hub.send("Subscribe", [subscribe_data])
            
            # Track subscriptions
            self.market_subscriptions["depth"].extend(contract_ids)
            
            logger.info(f"Subscribed to market depth for: {contract_ids}")
            return True
            
        except Exception as e:
            logger.error(f"Market depth subscription error: {e}")
            return False
    
    async def unsubscribe(self, contract_ids: List[str], subscription_type: str = "All") -> bool:
        """Unsubscribe from market data"""
        try:
            if not self.market_connected:
                return False
            
            unsubscribe_data = {
                "contractIds": contract_ids,
                "subscriptionType": subscription_type
            }
            
            self.market_hub.send("Unsubscribe", [unsubscribe_data])
            
            logger.info(f"Unsubscribed from {subscription_type} for: {contract_ids}")
            return True
            
        except Exception as e:
            logger.error(f"Unsubscribe error: {e}")
            return False
    
    # Callback Registration
    
    def on_quote(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for quote updates"""
        self.callbacks["quote"].append(callback)
    
    def on_trade(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for trade updates"""
        self.callbacks["trade"].append(callback)
    
    def on_market_depth(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for market depth updates"""
        self.callbacks["depth"].append(callback)
    
    def on_order_update(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for order updates"""
        self.callbacks["order"].append(callback)
    
    def on_position_update(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for position updates"""
        self.callbacks["position"].append(callback)
    
    def on_fill_update(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for fill updates"""
        self.callbacks["fill"].append(callback)
    
    def on_connection_status(self, callback: Callable[[str], None]) -> None:
        """Register callback for connection status changes"""
        self.callbacks["connection_status"].append(callback)
    
    # Event Handlers - Market Hub
    
    def _on_market_open(self) -> None:
        """Handle market hub connection open"""
        logger.info("Market hub connection opened")
        self.market_connected = True
    
    def _on_market_close(self) -> None:
        """Handle market hub connection close"""
        logger.warning("Market hub connection closed")
        self.market_connected = False
        asyncio.create_task(self._handle_reconnect("market"))
    
    def _on_market_error(self, error: Any) -> None:
        """Handle market hub errors"""
        logger.error(f"Market hub error: {error}")
    
    def _on_quote(self, data: List[Any]) -> None:
        """Handle quote updates"""
        try:
            for quote in data:
                quote_data = {
                    "contractId": quote.get("contractId"),
                    "bid": quote.get("bid"),
                    "bidSize": quote.get("bidSize"),
                    "ask": quote.get("ask"),
                    "askSize": quote.get("askSize"),
                    "last": quote.get("last"),
                    "lastSize": quote.get("lastSize"),
                    "volume": quote.get("volume"),
                    "timestamp": quote.get("timestamp", datetime.utcnow().isoformat())
                }
                
                # Notify all registered callbacks
                for callback in self.callbacks["quote"]:
                    asyncio.create_task(self._safe_callback(callback, quote_data))
                    
        except Exception as e:
            logger.error(f"Error processing quote: {e}")
    
    def _on_trade(self, data: List[Any]) -> None:
        """Handle trade updates"""
        try:
            for trade in data:
                trade_data = {
                    "contractId": trade.get("contractId"),
                    "price": trade.get("price"),
                    "size": trade.get("size"),
                    "side": trade.get("side"),
                    "timestamp": trade.get("timestamp", datetime.utcnow().isoformat())
                }
                
                # Notify all registered callbacks
                for callback in self.callbacks["trade"]:
                    asyncio.create_task(self._safe_callback(callback, trade_data))
                    
        except Exception as e:
            logger.error(f"Error processing trade: {e}")
    
    def _on_market_depth(self, data: List[Any]) -> None:
        """Handle market depth updates"""
        try:
            for depth in data:
                depth_data = {
                    "contractId": depth.get("contractId"),
                    "bids": depth.get("bids", []),
                    "asks": depth.get("asks", []),
                    "timestamp": depth.get("timestamp", datetime.utcnow().isoformat())
                }
                
                # Notify all registered callbacks
                for callback in self.callbacks["depth"]:
                    asyncio.create_task(self._safe_callback(callback, depth_data))
                    
        except Exception as e:
            logger.error(f"Error processing market depth: {e}")
    
    def _on_market_status(self, data: Any) -> None:
        """Handle market status updates"""
        logger.info(f"Market status update: {data}")
    
    # Event Handlers - User Hub
    
    def _on_user_open(self) -> None:
        """Handle user hub connection open"""
        logger.info("User hub connection opened")
        self.user_connected = True
    
    def _on_user_close(self) -> None:
        """Handle user hub connection close"""
        logger.warning("User hub connection closed")
        self.user_connected = False
        asyncio.create_task(self._handle_reconnect("user"))
    
    def _on_user_error(self, error: Any) -> None:
        """Handle user hub errors"""
        logger.error(f"User hub error: {error}")
    
    def _on_order_update(self, data: Any) -> None:
        """Handle order updates"""
        try:
            order_data = {
                "orderId": data.get("orderId"),
                "accountId": data.get("accountId"),
                "contractId": data.get("contractId"),
                "status": data.get("status"),
                "side": data.get("side"),
                "type": data.get("type"),
                "quantity": data.get("quantity"),
                "price": data.get("price"),
                "filledQuantity": data.get("filledQuantity"),
                "averagePrice": data.get("averagePrice"),
                "timestamp": data.get("timestamp", datetime.utcnow().isoformat())
            }
            
            # Notify all registered callbacks
            for callback in self.callbacks["order"]:
                asyncio.create_task(self._safe_callback(callback, order_data))
                
        except Exception as e:
            logger.error(f"Error processing order update: {e}")
    
    def _on_position_update(self, data: Any) -> None:
        """Handle position updates"""
        try:
            position_data = {
                "positionId": data.get("positionId"),
                "accountId": data.get("accountId"),
                "contractId": data.get("contractId"),
                "side": data.get("side"),
                "quantity": data.get("quantity"),
                "averagePrice": data.get("averagePrice"),
                "marketPrice": data.get("marketPrice"),
                "unrealizedPnL": data.get("unrealizedPnL"),
                "realizedPnL": data.get("realizedPnL"),
                "timestamp": data.get("timestamp", datetime.utcnow().isoformat())
            }
            
            # Notify all registered callbacks
            for callback in self.callbacks["position"]:
                asyncio.create_task(self._safe_callback(callback, position_data))
                
        except Exception as e:
            logger.error(f"Error processing position update: {e}")
    
    def _on_fill_update(self, data: Any) -> None:
        """Handle fill updates"""
        try:
            fill_data = {
                "fillId": data.get("fillId"),
                "orderId": data.get("orderId"),
                "accountId": data.get("accountId"),
                "contractId": data.get("contractId"),
                "side": data.get("side"),
                "price": data.get("price"),
                "quantity": data.get("quantity"),
                "commission": data.get("commission"),
                "timestamp": data.get("timestamp", datetime.utcnow().isoformat())
            }
            
            # Notify all registered callbacks
            for callback in self.callbacks["fill"]:
                asyncio.create_task(self._safe_callback(callback, fill_data))
                
        except Exception as e:
            logger.error(f"Error processing fill update: {e}")
    
    def _on_account_update(self, data: Any) -> None:
        """Handle account updates"""
        logger.info(f"Account update: {data}")
    
    # Helper Methods
    
    async def _safe_callback(self, callback: Callable, data: Any) -> None:
        """Safely execute callback with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.error(f"Callback error: {e}")
    
    async def _handle_reconnect(self, hub_type: str) -> None:
        """Handle hub reconnection"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts reached for {hub_type} hub")
            await self._notify_connection_status("failed")
            return
        
        self.reconnect_attempts += 1
        logger.info(f"Attempting to reconnect {hub_type} hub (attempt {self.reconnect_attempts})")
        
        await asyncio.sleep(self.reconnect_delay)
        
        if hub_type == "market":
            await self._connect_market_hub()
        elif hub_type == "user":
            await self._connect_user_hub()
    
    async def _notify_connection_status(self, status: str) -> None:
        """Notify connection status to callbacks"""
        for callback in self.callbacks["connection_status"]:
            await self._safe_callback(callback, status)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "connected": self.is_connected,
            "market_hub": self.market_connected,
            "user_hub": self.user_connected,
            "subscriptions": self.market_subscriptions,
            "reconnect_attempts": self.reconnect_attempts
        }
    
    async def ping(self) -> bool:
        """Send ping to keep connection alive"""
        try:
            if self.market_connected and self.market_hub:
                self.market_hub.send("Ping", [])
            
            if self.user_connected and self.user_hub:
                self.user_hub.send("Ping", [])
                
            return True
        except Exception as e:
            logger.error(f"Ping error: {e}")
            return False


# Example usage and integration helper
class SignalRIntegration:
    """Helper class for integrating SignalR with the main bot"""
    
    def __init__(self, jwt_token: str):
        self.client = TopStepXSignalRClient(jwt_token)
        self.latest_quotes: Dict[str, Dict] = {}
        self.latest_trades: Dict[str, List[Dict]] = []
        
    async def start(self) -> bool:
        """Start SignalR client and register callbacks"""
        # Register callbacks
        self.client.on_quote(self._handle_quote)
        self.client.on_trade(self._handle_trade)
        self.client.on_position_update(self._handle_position)
        self.client.on_order_update(self._handle_order)
        
        # Connect
        connected = await self.client.connect()
        
        if connected:
            # Subscribe to MGC quotes and trades
            await self.client.subscribe_to_quotes(["CON.F.US.MGC.Q25"])
            await self.client.subscribe_to_trades(["CON.F.US.MGC.Q25"])
            
        return connected
    
    async def stop(self) -> None:
        """Stop SignalR client"""
        await self.client.disconnect()
    
    def _handle_quote(self, quote: Dict) -> None:
        """Handle incoming quote"""
        contract_id = quote.get("contractId")
        if contract_id:
            self.latest_quotes[contract_id] = quote
            logger.debug(f"Quote update: {contract_id} - Bid: {quote.get('bid')}, Ask: {quote.get('ask')}")
    
    def _handle_trade(self, trade: Dict) -> None:
        """Handle incoming trade"""
        contract_id = trade.get("contractId")
        if contract_id:
            if contract_id not in self.latest_trades:
                self.latest_trades[contract_id] = []
            self.latest_trades[contract_id].append(trade)
            # Keep only last 100 trades
            self.latest_trades[contract_id] = self.latest_trades[contract_id][-100:]
            logger.debug(f"Trade: {contract_id} - Price: {trade.get('price')}, Size: {trade.get('size')}")
    
    def _handle_position(self, position: Dict) -> None:
        """Handle position update"""
        logger.info(f"Position update: {position}")
    
    def _handle_order(self, order: Dict) -> None:
        """Handle order update"""
        logger.info(f"Order update: {order}")
    
    def get_latest_quote(self, contract_id: str) -> Optional[Dict]:
        """Get latest quote for a contract"""
        return self.latest_quotes.get(contract_id)
    
    def get_recent_trades(self, contract_id: str, limit: int = 10) -> List[Dict]:
        """Get recent trades for a contract"""
        trades = self.latest_trades.get(contract_id, [])
        return trades[-limit:] if trades else []