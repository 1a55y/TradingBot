"""TopStepX API Client Implementation"""
# Standard library imports
import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Third-party imports
import aiohttp

# Local imports
from src.config import Config
from src.utils.logger_setup import logger


class TopStepXClient:
    """Client for TopStepX API interactions"""
    
    def __init__(self):
        self.config = Config
        self.api_key = self.config.TOPSTEP_API_KEY
        self.username = self.config.TOPSTEP_USERNAME
        self.user_id = self.config.TOPSTEP_USER_ID
        
        # Use practice account for paper trading, Step 1 account for live
        if self.config.PAPER_TRADING:
            self.account_id = self.config.PRACTICE_ACCOUNT_ID
            logger.info(f"Using PRACTICE account: {self.account_id}")
        else:
            self.account_id = self.config.STEP1_ACCOUNT_ID
            logger.info(f"Using STEP 1 evaluation account: {self.account_id}")
            
        self.base_url = self.config.TOPSTEP_API_BASE_URL
        self.ws_data_url = self.config.TOPSTEP_WS_DATA_URL
        self.ws_trading_url = self.config.TOPSTEP_WS_TRADING_URL
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_data: Optional[aiohttp.ClientWebSocketResponse] = None
        self.ws_trading: Optional[aiohttp.ClientWebSocketResponse] = None
        
        # Authentication
        self.session_token: Optional[str] = None
        
        # Connection state
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        logger.info("TopStepX Client initialized")
    
    async def connect(self) -> bool:
        """Establish connection to TopStepX API"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Authenticate and get session token
            if await self._authenticate():
                logger.info("Authentication successful")
                
                # Skip WebSocket for now - use REST API only
                self.is_connected = True
                logger.info("Successfully connected to TopStepX (REST API mode)")
                logger.warning("WebSocket connections disabled - using polling mode")
                return True
            else:
                logger.error("Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from TopStepX API"""
        try:
            # Close WebSockets
            if self.ws_data and not self.ws_data.closed:
                await self.ws_data.close()
            if self.ws_trading and not self.ws_trading.closed:
                await self.ws_trading.close()
            
            # Close HTTP session
            if self.session and not self.session.closed:
                await self.session.close()
            
            self.is_connected = False
            logger.info("Disconnected from TopStepX")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authentication headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        
        # Add authorization header if we have a session token
        if self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
            
        return headers
    
    async def _authenticate(self) -> bool:
        """Authenticate and get session token"""
        try:
            auth_data = {
                "userName": self.username,
                "apiKey": self.api_key
            }
            
            async with self.session.post(
                f"{self.base_url}/api/Auth/loginKey",
                json=auth_data,
                headers={'Content-Type': 'application/json', 'Accept': 'text/plain'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success') and result.get('token'):
                        self.session_token = result['token']
                        self._last_auth_time = datetime.now()  # Track auth time
                        logger.info(f"Login successful, session token obtained")
                        return True
                    else:
                        error_msg = result.get('errorMessage', 'Unknown error')
                        logger.error(f"Login failed: {error_msg}")
                        return False
                else:
                    logger.error(f"Auth request failed: {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def _connect_websockets(self) -> bool:
        """Connect to WebSocket endpoints"""
        try:
            # Connect to market data WebSocket
            self.ws_data = await self.session.ws_connect(
                self.ws_data_url,
                headers=self._get_auth_headers()
            )
            logger.info("Connected to market data WebSocket")
            
            # Connect to trading WebSocket
            self.ws_trading = await self.session.ws_connect(
                self.ws_trading_url,
                headers=self._get_auth_headers()
            )
            logger.info("Connected to trading WebSocket")
            
            # Subscribe to MGC data
            await self._subscribe_to_market_data()
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return False
    
    async def _subscribe_to_market_data(self) -> None:
        """Subscribe to MGC market data"""
        subscribe_msg = {
            "action": "subscribe",
            "symbols": ["MGC"],
            "type": "quote",
            "market": self.config.TOPSTEP_MARKET
        }
        await self.ws_data.send_json(subscribe_msg)
        logger.info("Subscribed to MGC market data")
    
    async def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        try:
            # First validate the session
            if not await self._validate_session():
                logger.warning("Session invalid, re-authenticating...")
                if not await self._authenticate():
                    return None
                    
            # Search for user's accounts
            search_data = {
                "accountIds": [int(self.account_id)] if self.account_id else None
            }
            
            async with self.session.post(
                f"{self.base_url}/api/Account/search",
                json=search_data,
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    accounts = result.get('accounts', [])
                    if accounts and len(accounts) > 0:
                        # Find the account with matching ID or return first
                        for acc in accounts:
                            if str(acc.get('id')) == str(self.account_id):
                                return acc
                        return accounts[0]  # Return first if no match
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get account info: {response.status} - {error_text[:100]}")
                    return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    async def _validate_session(self) -> bool:
        """Validate current session token"""
        if not self.session_token:
            return False
        
        # Skip validation if we recently authenticated (within 5 minutes)
        if hasattr(self, '_last_auth_time'):
            time_since_auth = (datetime.now() - self._last_auth_time).seconds
            if time_since_auth < 300:  # 5 minutes
                return True
            
        try:
            async with self.session.post(
                f"{self.base_url}/api/Auth/validate",
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # TopStep API might return accounts instead of isValid
                    if 'accounts' in result:
                        return len(result.get('accounts', [])) > 0
                    return result.get('isValid', True)  # Default to True if field missing
                else:
                    return False
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
    
    async def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            search_data = {
                "accountId": int(self.account_id)
            }
            
            async with self.session.post(
                f"{self.base_url}/api/Position/searchOpen",
                json=search_data,
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    # Debug log
                    if result and len(result) > 0:
                        logger.debug(f"Found {len(result)} positions")
                    # Make sure we return a list
                    if isinstance(result, list):
                        return result
                    elif isinstance(result, dict):
                        # If it's wrapped in an object, extract the positions
                        return result.get('positions', [])
                    else:
                        return []
                else:
                    logger.error(f"Failed to get positions: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def place_order(self, order_data: Dict) -> Optional[Dict]:
        """Place an order"""
        try:
            # Map order types and sides to numeric values
            order_type_map = {
                "Market": 2,
                "Limit": 1,
                "Stop": 4,
                "StopLimit": 3
            }
            
            order_side_map = {
                "Buy": 0,   # Bid
                "Sell": 1   # Ask
            }
            
            # TopStepX order format
            # Use account_id from order_data if provided, otherwise use self.account_id
            account_id = order_data.get("account_id", self.account_id)
            topstep_order = {
                "accountId": int(account_id),
                "contractId": order_data.get("contractId"),
                "type": order_type_map.get(order_data.get("orderType", "Market"), 2),
                "side": order_side_map.get(order_data.get("side", "Buy"), 0),
                "size": order_data.get("quantity", 1),
                "limitPrice": order_data.get("limitPrice"),
                "stopPrice": order_data.get("stopPrice"),
                "trailPrice": order_data.get("trailPrice"),
                "customTag": order_data.get("customTag"),
                "linkedOrderId": order_data.get("linkedOrderId")
            }
            
            # Log the order we're sending for debugging
            logger.info(f"📤 Sending order to TopStep API: {topstep_order}")
            
            async with self.session.post(
                f"{self.base_url}/api/Order/place",
                json=topstep_order,
                headers=self._get_auth_headers()
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    logger.info(f"Order placed: {result.get('orderId', 'Unknown')}")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"Order failed: {response.status} - {error}")
                    return None
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            cancel_data = {
                "orderId": order_id,
                "accountId": int(self.account_id)
            }
            
            async with self.session.post(
                f"{self.base_url}/api/Order/cancel",
                json=cancel_data,
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    logger.info(f"Order {order_id} cancelled")
                    return True
                else:
                    logger.error(f"Failed to cancel order: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    async def get_market_data(self, symbol: str = "MGC") -> Optional[Dict]:
        """Get current market data"""
        try:
            # First get contract ID for symbol
            contract = await self._get_contract_by_symbol(symbol)
            if not contract:
                logger.error(f"Could not find contract for {symbol}")
                return None
                
            # For now, return contract info as market data
            # Real-time data would come from WebSocket
            return {
                "symbol": symbol,
                "contractId": contract.get("contractId"),
                "bid": 0,  # Would come from WebSocket
                "ask": 0,  # Would come from WebSocket
                "last": 0  # Would come from WebSocket
            }
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
    
    async def _get_contract_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Get contract details by symbol"""
        try:
            # Use live=False for practice accounts, live=True for real accounts
            is_practice = self.account_id == self.config.PRACTICE_ACCOUNT_ID
            
            search_data = {
                "searchText": symbol,
                "live": not is_practice  # Practice uses simulated contracts
            }
            
            async with self.session.post(
                f"{self.base_url}/api/Contract/search",
                json=search_data,
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success') and result.get('contracts'):
                        contracts = result['contracts']
                        # Find exact match or first contract
                        for contract in contracts:
                            if contract.get('id') == symbol or contract.get('name', '').startswith(symbol):
                                return contract
                        # Return first if no exact match
                        return contracts[0] if contracts else None
                    return None
                else:
                    logger.error(f"Contract search failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting contract: {e}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str = "MGC", 
        interval: str = "15m", 
        limit: int = 100
    ) -> Optional[List[Dict]]:
        """Get historical candle data"""
        try:
            # Get contract first
            contract = await self._get_contract_by_symbol(symbol)
            if not contract:
                logger.error(f"Could not find contract for {symbol}")
                return None
            
            # Map intervals to unit and unitNumber
            interval_map = {
                "1m": (2, 1),    # Minute, 1
                "5m": (2, 5),    # Minute, 5
                "15m": (2, 15),  # Minute, 15
                "30m": (2, 30),  # Minute, 30
                "1h": (3, 1),    # Hour, 1
                "1d": (4, 1)     # Day, 1
            }
            
            unit, unit_number = interval_map.get(interval, (2, 15))
            
            # Calculate date range
            from datetime import datetime, timedelta
            end_time = datetime.utcnow()
            
            # Calculate start time based on interval and limit
            minutes_map = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "1d": 1440}
            minutes = minutes_map.get(interval, 15)
            start_time = end_time - timedelta(minutes=minutes * limit * 1.5)  # Get extra data
            
            # Use live=False for practice accounts
            is_practice = self.account_id == self.config.PRACTICE_ACCOUNT_ID
            
            history_data = {
                "contractId": contract.get("id"),  # Use the ID field
                "live": not is_practice,
                "startTime": start_time.isoformat() + "Z",
                "endTime": end_time.isoformat() + "Z",
                "unit": unit,
                "unitNumber": unit_number,
                "limit": limit,
                "includePartialBar": True
            }
            
            async with self.session.post(
                f"{self.base_url}/api/History/retrieveBars",
                json=history_data,
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success') and result.get('bars'):
                        return result['bars']
                    else:
                        logger.error(f"Failed to get bars: {result.get('errorMessage', 'Unknown error')}")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get historical data: {response.status} - {error_text[:200]}")
                    return None
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None
    
    async def handle_market_data_stream(self) -> None:
        """Handle incoming market data from WebSocket"""
        try:
            async for msg in self.ws_data:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    yield data
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.ws_data.exception()}")
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.warning("Market data WebSocket closed")
                    break
        except Exception as e:
            logger.error(f"Error in market data stream: {e}")
    
    async def handle_trading_events(self) -> None:
        """Handle trading events from WebSocket"""
        try:
            async for msg in self.ws_trading:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    yield data
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"Trading WebSocket error: {self.ws_trading.exception()}")
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.warning("Trading WebSocket closed")
                    break
        except Exception as e:
            logger.error(f"Error in trading events stream: {e}")