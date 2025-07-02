# SignalR Real-Time Data Connection Issue

## Problem Summary
We need real-time data from TopStepX. REST API provides 15-minute delayed data for practice accounts. SignalR connection opens but fails during handshake.

## What Works ✅
1. JWT authentication successful
2. WebSocket connection opens to `wss://rtc.topstepx.com/hubs/market`
3. Position query fixed (accountId vs accountIds)
4. REST API fully functional (but delayed)

## What Fails ❌
1. SignalR handshake fails after WebSocket opens
2. Subscription methods return "error on server"
3. No real-time data received

## Deep Analysis 🧠

### JavaScript Example (Working)
```javascript
const rtcConnection = new HubConnectionBuilder()
    .withUrl(marketHubUrl, {
        skipNegotiation: true,
        transport: HttpTransportType.WebSockets,
        accessTokenFactory: () => JWT_TOKEN,
        timeout: 10000
    })
    .withAutomaticReconnect()
    .build();

// Subscriptions
rtcConnection.invoke('SubscribeContractQuotes', CONTRACT_ID);
rtcConnection.on('GatewayQuote', (contractId, data) => {...});
```

### Python Implementation (Failing)
```python
# Using signalrcore library
connection = HubConnectionBuilder()\
    .with_url(
        f"{hub_url}?access_token={jwt_token}",
        options={
            "skip_negotiation": True,
            "transport": ["websockets"]
        }
    )\
    .build()
```

## Hypotheses 🔍

1. **Protocol Mismatch**: JavaScript SDK might use different SignalR protocol version
2. **Library Incompatibility**: `signalrcore` might not support TopStepX's SignalR implementation
3. **Missing Headers**: Server might expect additional headers/parameters
4. **Authentication Format**: Token might need different format/encoding

## Next Steps 🚀

1. **Capture JavaScript Traffic**: Use browser DevTools to see exact WebSocket frames
2. **Try Different Libraries**: Test `python-signalr-client` or raw WebSocket
3. **Contact TopStepX**: Ask for Python examples or documentation
4. **Reverse Engineer**: Analyze the JavaScript SDK internals

## Evidence Log 📊

### Successful WebSocket Open
```
2025-07-01 20:12:20,022 - SignalRCoreClient - DEBUG - -- web socket open --
2025-07-01 20:12:20,022 - SignalRCoreClient - DEBUG - Sending message HandshakeRequestMessage
2025-07-01 20:12:20,182 - SignalRCoreClient - DEBUG - Message received{}
2025-07-01 20:12:20,183 - SignalRCoreClient - DEBUG - Evaluating handshake {}
```

### Failed Subscription
```
"Failed to invoke 'SubscribeContractQuotes' due to an error on the server."
```

## Critical Question ❓
The handshake response is empty `{}` - this might indicate the server expects a different protocol or the `signalrcore` library is incompatible with TopStepX's SignalR implementation.