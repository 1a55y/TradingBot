"""WebSocket connection management with automatic reconnection - CRITICAL FIX #4"""
import asyncio
import websockets
import json
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta
from .logger_setup import logger

class ConnectionError(Exception):
    """WebSocket connection errors"""
    pass

class WebSocketReconnector:
    """Manages WebSocket connections with automatic reconnection"""
    
    def __init__(
        self,
        url: str,
        on_message: Optional[Callable] = None,
        on_connect: Optional[Callable] = None,
        on_disconnect: Optional[Callable] = None,
        heartbeat_interval: int = 30,
        max_reconnect_delay: int = 300,
        initial_reconnect_delay: float = 1.0
    ):
        self.url = url
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.heartbeat_interval = heartbeat_interval
        self.max_reconnect_delay = max_reconnect_delay
        self.initial_reconnect_delay = initial_reconnect_delay
        
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.should_run = True
        self.reconnect_delay = initial_reconnect_delay
        self.last_heartbeat = datetime.now()
        self.connection_lost_time: Optional[datetime] = None
        self.total_reconnect_attempts = 0
        self.consecutive_failures = 0
        
    async def connect(self) -> bool:
        """Establish WebSocket connection"""
        try:
            logger.info(f"Connecting to {self.url}")
            self.ws = await websockets.connect(
                self.url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.is_connected = True
            self.connection_lost_time = None
            self.consecutive_failures = 0
            self.reconnect_delay = self.initial_reconnect_delay
            
            logger.success(f"Connected to {self.url}")
            
            if self.on_connect:
                await self.on_connect()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.is_connected = False
            self.consecutive_failures += 1
            return False
    
    async def disconnect(self) -> None:
        """Gracefully disconnect"""
        self.should_run = False
        
        if self.ws and not self.ws.closed:
            try:
                await self.ws.close()
            except:
                pass
        
        self.is_connected = False
        
        if self.on_disconnect:
            await self.on_disconnect()
        
        logger.info("Disconnected")
    
    async def send(self, message: Dict[str, Any]) -> bool:
        """Send message with error handling"""
        if not self.is_connected or not self.ws:
            logger.warning("Cannot send - not connected")
            return False
        
        try:
            await self.ws.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Send failed: {e}")
            self.is_connected = False
            return False
    
    async def receive_loop(self) -> None:
        """Main receive loop with error handling"""
        while self.should_run:
            try:
                if not self.is_connected:
                    await self.reconnect()
                    continue
                
                # Receive with timeout
                message = await asyncio.wait_for(
                    self.ws.recv(),
                    timeout=self.heartbeat_interval
                )
                
                self.last_heartbeat = datetime.now()
                
                if self.on_message:
                    await self.on_message(json.loads(message))
                
            except asyncio.TimeoutError:
                # Check if we need to send heartbeat
                if (datetime.now() - self.last_heartbeat).seconds > self.heartbeat_interval:
                    if not await self.send_heartbeat():
                        self.is_connected = False
                        
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection closed by server")
                self.is_connected = False
                
            except Exception as e:
                logger.error(f"Receive error: {e}")
                self.is_connected = False
                await asyncio.sleep(1)
    
    async def send_heartbeat(self) -> bool:
        """Send heartbeat to keep connection alive"""
        return await self.send({"type": "heartbeat", "timestamp": datetime.now().isoformat()})
    
    async def reconnect(self) -> None:
        """Reconnect with exponential backoff"""
        if not self.connection_lost_time:
            self.connection_lost_time = datetime.now()
        
        downtime = (datetime.now() - self.connection_lost_time).total_seconds()
        
        logger.warning(
            f"Attempting reconnect #{self.total_reconnect_attempts + 1} "
            f"(down for {downtime:.1f}s, delay: {self.reconnect_delay:.1f}s)"
        )
        
        # Wait before reconnecting
        await asyncio.sleep(self.reconnect_delay)
        
        self.total_reconnect_attempts += 1
        
        # Try to reconnect
        if await self.connect():
            logger.success(f"Reconnected after {downtime:.1f} seconds")
        else:
            # Exponential backoff
            self.reconnect_delay = min(
                self.reconnect_delay * 2,
                self.max_reconnect_delay
            )
            
            # Check circuit breaker
            if self.consecutive_failures > 10:
                logger.error(f"Too many consecutive failures ({self.consecutive_failures}), waiting longer")
                await asyncio.sleep(60)  # Extra wait

class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED (normal), OPEN (failing), HALF_OPEN (testing)
    
    def record_success(self) -> None:
        """Record successful operation"""
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker recovering, closing circuit")
            self.state = "CLOSED"
            self.failure_count = 0
    
    def record_failure(self) -> None:
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            self.state = "OPEN"
    
    def can_execute(self) -> bool:
        """Check if operation should be attempted"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                if time_since_failure > self.recovery_timeout:
                    logger.info("Circuit breaker entering half-open state")
                    self.state = "HALF_OPEN"
                    return True
            return False
        
        return True  # HALF_OPEN - allow testing

class ConnectionManager:
    """Manages multiple WebSocket connections with monitoring"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketReconnector] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        
    def add_connection(
        self,
        name: str,
        url: str,
        on_message: Optional[Callable] = None,
        **kwargs
    ) -> WebSocketReconnector:
        """Add a managed connection"""
        conn = WebSocketReconnector(url, on_message=on_message, **kwargs)
        self.connections[name] = conn
        self.circuit_breakers[name] = CircuitBreaker()
        return conn
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect all managed connections"""
        results = {}
        
        for name, conn in self.connections.items():
            if self.circuit_breakers[name].can_execute():
                success = await conn.connect()
                results[name] = success
                
                if success:
                    self.circuit_breakers[name].record_success()
                else:
                    self.circuit_breakers[name].record_failure()
            else:
                logger.warning(f"Circuit breaker preventing connection to {name}")
                results[name] = False
        
        return results
    
    async def start_all(self) -> None:
        """Start all connection loops"""
        tasks = []
        
        for name, conn in self.connections.items():
            task = asyncio.create_task(conn.receive_loop())
            tasks.append(task)
        
        # Start monitoring
        self.monitoring_task = asyncio.create_task(self.monitor_connections())
        
        await asyncio.gather(*tasks)
    
    async def stop_all(self) -> None:
        """Stop all connections"""
        for conn in self.connections.values():
            await conn.disconnect()
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
    
    async def monitor_connections(self) -> None:
        """Monitor connection health"""
        while True:
            try:
                stats = {
                    name: {
                        "connected": conn.is_connected,
                        "reconnect_attempts": conn.total_reconnect_attempts,
                        "consecutive_failures": conn.consecutive_failures,
                        "circuit_breaker": self.circuit_breakers[name].state
                    }
                    for name, conn in self.connections.items()
                }
                
                # Log connection stats
                connected = sum(1 for s in stats.values() if s["connected"])
                total = len(stats)
                
                if connected < total:
                    logger.warning(f"Connections: {connected}/{total} active")
                    for name, stat in stats.items():
                        if not stat["connected"]:
                            logger.debug(f"{name}: {stat}")
                
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(30)