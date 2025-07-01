# WebSocket Investigation Report: Real-Time Data for Practice Accounts

## Executive Summary

Investigation into whether TopStepX WebSocket connections can provide real-time data for practice accounts to solve the 15-minute delay issue with REST API calls.

## Key Findings

### 1. Current Configuration

**WebSocket URLs in config.py:**
- Market Data: `wss://api.topstepx.com/hubs/market`
- Trading Events: `wss://api.topstepx.com/hubs/user`

**Current Status:**
- WebSocket code exists but is **disabled** in `topstep_client.py` (line 62-66)
- REST API is used exclusively with `live: false` for practice accounts
- This causes 15-minute delayed data as documented in `topstepx_issues_resolved.md`

### 2. WebSocket Implementation Analysis

**Existing WebSocket Code (Lines 139-164 in topstep_client.py):**
```python
async def _connect_websockets(self) -> bool:
    """Connect to WebSocket endpoints"""
    # Connects to both market data and trading WebSockets
    # Subscribes to MGC (Micro Gold) data
    # Currently NOT called in connect() method
```

**Why It's Disabled:**
- Line 62-63: Skip WebSocket, use REST API only
- Line 65: Warning logged about using polling mode
- No attempt to establish WebSocket connections

### 3. Potential Solution

**WebSocket MAY provide real-time data for practice accounts because:**

1. **Different Data Path**: WebSockets typically bypass REST API caching/delay mechanisms
2. **Subscription Model**: Real-time push notifications vs. request/response polling
3. **No `live` Parameter**: WebSocket subscriptions don't appear to use the `live: false` flag

**Evidence Supporting Real-Time WebSocket Data:**
- WebSocket handlers exist for streaming market data (line 445-459)
- Subscription messages don't include account type discrimination
- Market data WebSocket is separate from account-specific endpoints

### 4. Implementation Requirements

To enable WebSocket and test if it provides real-time data:

1. **Modify `connect()` method** in `topstep_client.py`:
   ```python
   # After line 61, replace lines 62-66 with:
   if await self._connect_websockets():
       self.is_connected = True
       logger.info("Connected with WebSocket support")
       return True
   ```

2. **Add WebSocket data handling** to main bot loop:
   - Replace REST API price fetching with WebSocket stream
   - Maintain REST API as fallback
   - Handle reconnection logic

3. **Test with practice account** to verify:
   - Data timestamp comparison
   - Price update frequency
   - Latency measurements

### 5. Risk Assessment

**Low Risk:**
- WebSocket code already exists
- Can fallback to REST API if needed
- Non-breaking change

**Potential Issues:**
- WebSocket might still return delayed data (needs testing)
- Additional complexity in connection management
- Possible rate limits or connection restrictions

## Recommendations

1. **Run WebSocket Test Script**: Execute `scripts/test_websocket_data.py` to verify real-time data availability

2. **Gradual Rollout**:
   - Enable WebSocket for market data only initially
   - Monitor data timestamps and accuracy
   - Expand to trading events if successful

3. **Hybrid Approach**:
   - Use WebSocket for real-time prices
   - REST API for position management
   - Implement automatic fallback

## Test Script Created

Created `/scripts/test_websocket_data.py` to:
- Connect to TopStepX WebSockets with practice account
- Monitor incoming price updates
- Compare timestamps with REST API data
- Determine if WebSocket provides real-time data

## Conclusion

WebSocket implementation is already present but disabled. There's strong potential that enabling it could solve the 15-minute delay issue for practice accounts. The WebSocket endpoints appear to be designed for real-time market data streaming, which typically bypasses the delayed data mechanisms used in REST APIs.

**Next Steps:**
1. Run the test script to verify WebSocket behavior
2. If successful, enable WebSocket in production code
3. Implement proper error handling and reconnection logic

This investigation suggests that enabling WebSocket is the most promising solution for obtaining real-time data on practice accounts.