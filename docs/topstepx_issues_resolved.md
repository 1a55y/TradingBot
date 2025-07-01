# TopstepX API Issues - Resolved

## Summary
This document outlines two critical issues encountered with the TopstepX API integration and their solutions.

## Issue 1: Position Query 400 Error

### Problem
- API returned 400 Bad Request when querying positions
- Error: "Unknown field argument 'accountIds' on field 'Query.userSyncTradesConnection'"

### Root Cause
Incorrect field name in GraphQL query - using `accountIds` instead of `accountId`

### Solution
Changed the query parameter from:
```graphql
userSyncTradesConnection(accountIds: ["..."])
```
To:
```graphql
userSyncTradesConnection(accountId: "...")
```

## Issue 2: Data Delay in Practice Account

### Problem
- Position data showing significant delays (5+ minutes)
- Trades not appearing immediately after execution
- Inconsistent data updates

### Root Cause
Practice accounts use simulated/delayed data with `live: false` parameter

### Solution
For real-time data access:
1. Use a live/funded account
2. Set `live: true` in API queries
3. Practice accounts will always have delayed data

### Workarounds for Practice Accounts
1. **Implement polling mechanism** - Query API every 30-60 seconds
2. **Add manual refresh** - Allow users to trigger data updates
3. **Display data age** - Show timestamp of last update
4. **Set expectations** - Clearly indicate when using practice/delayed data

## Key Takeaways
1. Always verify GraphQL schema field names match documentation
2. Practice accounts have inherent data delays that cannot be bypassed
3. Real-time data requires live/funded accounts
4. Clear communication about data delays improves user experience