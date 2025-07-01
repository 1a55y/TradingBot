"""
TopStepX WebSocket Client - Production Implementation
Based on successful raw WebSocket approach that bypasses signalrcore issues
"""

import asyncio
import websockets
import json
from typing import Dict, Optional, Callable, List, Any
from datetime import datetime, timezone
from collections import defaultdict
import logging
from src.utils.logger_setup import logger
from src.config import Config


class TopStepXWebSocketClient:
    """Production WebSocket client for TopStepX real-time data"""
    
    def __init__(self, jwt_token: str):
        self.jwt_token = jwt_token
        self.market_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.user_ws: Optional[websockets.WebSocketClientProtocol] = None
        
        # Message ID counter for SignalR protocol
        self.invocation_id = 0
        
        # Callbacks for different data types
        self.callbacks = {
            'quote': [],
            'trade': [],
            'depth': [],
            'order': [],
            'position': [],
            'account': []
        }
        
        # Latest data cache
        self.latest_quotes = {}
        self.latest_trades = defaultdict(list)
        self.market_depth = {}
        
        # Connection state
        self.is_connected = False
        self.reconnect_task = None
        
        logger.info("TopStepX WebSocket Client initialized")
    
    async def connect(self) -> bool:
        """Connect to both market and user hubs"""
        try:
            # Connect to market hub for quotes
            await self._connect_market_hub()
            
            # Connect to user hub for positions/orders
            await self._connect_user_hub()
            
            self.is_connected = True
            logger.info("Successfully connected to TopStepX WebSocket hubs")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def _connect_market_hub(self):
        """Connect to market data hub"""
        url = f"wss://rtc.topstepx.com/hubs/market?access_token={self.jwt_token}"
        
        try:
            self.market_ws = await websockets.connect(url, subprotocols=["signalr"])
            logger.info("Market WebSocket connected")
            
            # Send SignalR handshake
            await self._send_handshake(self.market_ws)
            
            # Start listening task
            asyncio.create_task(self._listen_market_hub())
            
        except Exception as e:
            logger.error(f"Market hub connection error: {e}")
            raise
    
    async def _connect_user_hub(self):
        """Connect to user data hub"""
        url = f"wss://rtc.topstepx.com/hubs/user?access_token={self.jwt_token}"
        
        try:
            self.user_ws = await websockets.connect(url, subprotocols=["signalr"])
            logger.info("User WebSocket connected")
            
            # Send SignalR handshake
            await self._send_handshake(self.user_ws)
            
            # Start listening task
            asyncio.create_task(self._listen_user_hub())
            
        except Exception as e:
            logger.error(f"User hub connection error: {e}")
            raise
    
    async def _send_handshake(self, ws):
        """Send SignalR handshake"""
        handshake = {"protocol": "json", "version": 1}
        await ws.send(json.dumps(handshake) + "\x1e")
        
        # Wait for response
        response = await ws.recv()
        if response.endswith('\x1e'):
            response = response[:-1]
        
        # Empty response {} is valid for TopStepX
        logger.debug(f"Handshake response: {response}")
    
    async def _listen_market_hub(self):
        """Listen for market data messages"""
        try:
            while self.market_ws:
                message = await self.market_ws.recv()
                await self._process_message(message, "market")
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Market hub connection closed")
            await self._handle_disconnect("market")
        except Exception as e:
            logger.error(f"Market hub error: {e}")
    
    async def _listen_user_hub(self):
        """Listen for user data messages"""
        try:
            while self.user_ws:
                message = await self.user_ws.recv()
                await self._process_message(message, "user")
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("User hub connection closed")
            await self._handle_disconnect("user")
        except Exception as e:
            logger.error(f"User hub error: {e}")
    
    async def _process_message(self, message: str, hub_type: str):
        """Process SignalR messages"""
        # Remove delimiter
        if message.endswith('\x1e'):
            message = message[:-1]
        
        # Handle multiple messages
        messages = message.split('\x1e')
        
        for msg in messages:
            if not msg:
                continue
                
            try:
                data = json.loads(msg)
                msg_type = data.get('type')
                
                if msg_type == 1:  # Invocation
                    await self._handle_invocation(data, hub_type)
                elif msg_type == 3:  # Completion
                    if data.get('error'):
                        logger.error(f"Hub error: {data['error']}")
                elif msg_type == 6:  # Ping
                    # Send pong
                    pong = json.dumps({"type": 6}) + "\x1e"
                    ws = self.market_ws if hub_type == "market" else self.user_ws
                    await ws.send(pong)
                    
            except json.JSONDecodeError:
                logger.debug(f"Non-JSON message: {msg}")
    
    async def _handle_invocation(self, data: Dict, hub_type: str):
        """Handle SignalR invocation messages"""
        target = data.get('target')
        arguments = data.get('arguments', [])
        
        if target == 'GatewayQuote' and len(arguments) >= 2:
            contract_id = arguments[0]
            quote_data = arguments[1]
            await self._handle_quote(contract_id, quote_data)
            
        elif target == 'GatewayTrade' and len(arguments) >= 2:
            contract_id = arguments[0]
            trades = arguments[1]
            await self._handle_trades(contract_id, trades)
            
        elif target == 'GatewayDepth' and len(arguments) >= 2:
            contract_id = arguments[0]
            depth_data = arguments[1]
            await self._handle_depth(contract_id, depth_data)
            
        elif target == 'GatewayUserOrder' and len(arguments) >= 1:
            await self._handle_order(arguments[0])
            
        elif target == 'GatewayUserPosition' and len(arguments) >= 1:
            await self._handle_position(arguments[0])
    
    async def _handle_quote(self, contract_id: str, quote_data: Dict):
        """Handle quote updates"""
        # Update cache
        self.latest_quotes[contract_id] = {
            **quote_data,
            'timestamp_local': datetime.now(timezone.utc)
        }
        
        # Call callbacks
        for callback in self.callbacks['quote']:
            try:
                # Check if callback is async
                if asyncio.iscoroutinefunction(callback):
                    await callback(contract_id, quote_data)
                else:
                    callback(contract_id, quote_data)
            except Exception as e:
                logger.error(f"Quote callback error: {e}")
    
    async def _handle_trades(self, contract_id: str, trades: List[Dict]):
        """Handle trade updates"""
        # Update cache
        self.latest_trades[contract_id].extend(trades)
        
        # Keep only last 1000 trades
        if len(self.latest_trades[contract_id]) > 1000:
            self.latest_trades[contract_id] = self.latest_trades[contract_id][-1000:]
        
        # Call callbacks
        for callback in self.callbacks['trade']:
            try:
                # Check if callback is async
                if asyncio.iscoroutinefunction(callback):
                    await callback(contract_id, trades)
                else:
                    callback(contract_id, trades)
            except Exception as e:
                logger.error(f"Trade callback error: {e}")
    
    async def _handle_depth(self, contract_id: str, depth_data: Dict):
        """Handle market depth updates"""
        # Update cache
        self.market_depth[contract_id] = depth_data
        
        # Call callbacks
        for callback in self.callbacks['depth']:
            try:
                await callback(contract_id, depth_data)
            except Exception as e:
                logger.error(f"Depth callback error: {e}")
    
    async def _handle_order(self, order_data: Dict):
        """Handle order updates"""
        for callback in self.callbacks['order']:
            try:
                await callback(order_data)
            except Exception as e:
                logger.error(f"Order callback error: {e}")
    
    async def _handle_position(self, position_data: Dict):
        """Handle position updates"""
        for callback in self.callbacks['position']:
            try:
                await callback(position_data)
            except Exception as e:
                logger.error(f"Position callback error: {e}")
    
    async def subscribe_quotes(self, contract_id: str):
        """Subscribe to quote updates for a contract"""
        if not self.market_ws:
            logger.error("Market hub not connected")
            return False
            
        try:
            await self._invoke(self.market_ws, "SubscribeContractQuotes", contract_id)
            logger.info(f"Subscribed to quotes for {contract_id}")
            return True
        except Exception as e:
            logger.error(f"Quote subscription error: {e}")
            return False
    
    async def subscribe_trades(self, contract_id: str):
        """Subscribe to trade updates for a contract"""
        if not self.market_ws:
            logger.error("Market hub not connected")
            return False
            
        try:
            await self._invoke(self.market_ws, "SubscribeContractTrades", contract_id)
            logger.info(f"Subscribed to trades for {contract_id}")
            return True
        except Exception as e:
            logger.error(f"Trade subscription error: {e}")
            return False
    
    async def subscribe_market_depth(self, contract_id: str):
        """Subscribe to market depth for a contract"""
        if not self.market_ws:
            logger.error("Market hub not connected")
            return False
            
        try:
            await self._invoke(self.market_ws, "SubscribeContractMarketDepth", contract_id)
            logger.info(f"Subscribed to market depth for {contract_id}")
            return True
        except Exception as e:
            logger.error(f"Depth subscription error: {e}")
            return False
    
    async def subscribe_orders(self, account_id: int):
        """Subscribe to order updates"""
        if not self.user_ws:
            logger.error("User hub not connected")
            return False
            
        try:
            await self._invoke(self.user_ws, "SubscribeOrders", account_id)
            logger.info(f"Subscribed to orders for account {account_id}")
            return True
        except Exception as e:
            logger.error(f"Order subscription error: {e}")
            return False
    
    async def subscribe_positions(self, account_id: int):
        """Subscribe to position updates"""
        if not self.user_ws:
            logger.error("User hub not connected")
            return False
            
        try:
            await self._invoke(self.user_ws, "SubscribePositions", account_id)
            logger.info(f"Subscribed to positions for account {account_id}")
            return True
        except Exception as e:
            logger.error(f"Position subscription error: {e}")
            return False
    
    async def _invoke(self, ws, method: str, *args):
        """Invoke a hub method"""
        self.invocation_id += 1
        
        message = {
            "type": 1,  # Invocation
            "invocationId": str(self.invocation_id),
            "target": method,
            "arguments": list(args)
        }
        
        await ws.send(json.dumps(message) + "\x1e")
    
    def on_quote(self, callback: Callable):
        """Register quote callback"""
        self.callbacks['quote'].append(callback)
    
    def on_trade(self, callback: Callable):
        """Register trade callback"""
        self.callbacks['trade'].append(callback)
    
    def on_order(self, callback: Callable):
        """Register order callback"""
        self.callbacks['order'].append(callback)
    
    def on_position(self, callback: Callable):
        """Register position callback"""
        self.callbacks['position'].append(callback)
    
    def get_latest_quote(self, contract_id: str) -> Optional[Dict]:
        """Get latest quote for a contract"""
        return self.latest_quotes.get(contract_id)
    
    def get_recent_trades(self, contract_id: str, limit: int = 100) -> List[Dict]:
        """Get recent trades for a contract"""
        trades = self.latest_trades.get(contract_id, [])
        return trades[-limit:] if len(trades) > limit else trades
    
    async def disconnect(self):
        """Disconnect from all hubs"""
        self.is_connected = False
        
        if self.market_ws:
            await self.market_ws.close()
            self.market_ws = None
            
        if self.user_ws:
            await self.user_ws.close()
            self.user_ws = None
            
        logger.info("Disconnected from TopStepX WebSocket")
    
    async def _handle_disconnect(self, hub_type: str):
        """Handle disconnection and attempt reconnect"""
        if not self.is_connected:
            return
            
        logger.warning(f"Attempting to reconnect {hub_type} hub...")
        
        # Exponential backoff
        for attempt in range(5):
            await asyncio.sleep(2 ** attempt)
            
            try:
                if hub_type == "market":
                    await self._connect_market_hub()
                    # Resubscribe to quotes
                    for contract_id in self.latest_quotes.keys():
                        await self.subscribe_quotes(contract_id)
                        await self.subscribe_trades(contract_id)
                else:
                    await self._connect_user_hub()
                    # Resubscribe to user data
                    account_id = Config.PRACTICE_ACCOUNT_ID if Config.PAPER_TRADING else Config.STEP1_ACCOUNT_ID
                    await self.subscribe_orders(account_id)
                    await self.subscribe_positions(account_id)
                    
                logger.info(f"Reconnected {hub_type} hub successfully")
                return
                
            except Exception as e:
                logger.error(f"Reconnect attempt {attempt + 1} failed: {e}")
        
        logger.error(f"Failed to reconnect {hub_type} hub after 5 attempts")