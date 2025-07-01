# T-BOT Task Management System

A hybrid approach combining lightweight file tracking with GitHub Issues for building the Gold Futures Trading Bot.

## Quick Start (15 minutes)

### 1. Create GitHub Issues
Create 10 issues, one per week:
```
Issue #1: Week 1-2: Foundation - API & WebSocket
Issue #2: Week 3-4: Pattern Detection  
Issue #3: Week 5-6: Risk Management & Dashboard
Issue #4: Week 7-8: Enhanced Patterns
Issue #5: Week 9-10: Testing & Production
```

### 2. Initial Git Setup
```bash
# Initialize repo if needed
git init

# Create .gitignore
echo "*.env
*.log
__pycache__/
.pytest_cache/" > .gitignore

# First commit
git commit -m "Initial setup with task management

Issue: #1"
```

### 3. Create Your First Files

#### WEEKLY_PLAN.md
```markdown
# Week 1: Foundation (Issue #1)

## Goals This Week
- [ ] TopStepX API connection
- [ ] WebSocket data streaming  
- [ ] Basic order execution

## Monday: API Setup
- Research TopStepX documentation
- Create connection module
- Test authentication
```

#### work_log.md
```markdown
# 2025-06-28 - API Connection Setup

## BREAKDOWN (MANDATORY - DO NOT SKIP)
Task: Establish TopStepX API connection
Estimated: 3 hours

Subtasks:
1. Research & Setup (1h)
   - [ ] Read TopStepX API docs (30m)
   - [ ] Setup project structure (15m)
   - [ ] Configure environment variables (15m)

2. Implementation (1.5h)
   - [ ] Create connection class (30m)
   - [ ] Add authentication (30m)
   - [ ] Error handling (30m)

3. Testing (30m)
   - [ ] Test auth flow (15m)
   - [ ] Verify rate limits (15m)

## Progress
10:00 - Starting subtask 1: Research
10:30 - TopStepX uses REST + WebSocket combo
11:00 - Created src/api/connection.py
11:15 - Issue: SSL certificate validation failing
11:45 - Fixed: Added custom cert handling
12:00 - Successfully authenticated!

## Decisions
- Using asyncio for WebSocket handling
- Storing credentials in .env file
- Rate limiting: 10 requests/second
```

## Core System Components

### 1. GitHub Issues (Strategic Level)
- One issue per week of the 10-week plan
- Labels: `foundation`, `pattern-detection`, `risk-mgmt`, `testing`, `bug`, `enhancement`
- Milestones: `MVP`, `Full-Patterns`, `Production-Ready`

### 2. File-Based Tracking (Tactical Level)

#### WEEKLY_PLAN.md (Current Week Focus)
- Break down GitHub issue into daily tasks
- Show dependencies and blockers
- Update only when scope changes

#### work_log.md (Real-Time Progress)
- **Living document** updated throughout work
- **MANDATORY breakdown** before any coding
- Track decisions, blockers, solutions
- Newest entries at top

### 3. Git Integration
```
# Branch Strategy
main
├── week-1-foundation
├── week-3-patterns  (current)
└── feature/order-blocks

# Commit Format
[W3-D1] Add volume-based order block detection

- Implemented volume profile calculation
- Added trend filter
- Accuracy: 78%

Issue: #3
```

## MANDATORY Task Breakdown Rules

### No Coding Without Breakdown
1. **Any task >1 hour** must be broken into 15-30 min subtasks
2. **Any feature >4 hours** needs full decomposition with checkboxes
3. **Any debugging >30 min** requires investigation steps

### The 2-Hour Rule
If any subtask is >2 hours after breakdown, it's still too big. Break it down further.

### Why This is MANDATORY
- **Prevents rabbit holes**: Can't get lost for 4 hours
- **Better estimates**: Sum of small tasks = accurate
- **Clear progress**: Checkbox dopamine + visibility
- **Easy handoff**: Claude knows where you stopped
- **Catches complexity**: Can't break down = don't understand

## Daily Workflow

### Morning (10 min)
- [ ] Check WEEKLY_PLAN.md
- [ ] Review yesterday's work_log.md
- [ ] Create today's work_log.md entry
- [ ] **MANDATORY: Break down today's task into subtasks**
- [ ] Estimate time for each subtask

### During Work (continuous)
- [ ] Check off subtasks as completed
- [ ] Update work_log.md with progress
- [ ] Document decisions immediately
- [ ] Note blockers when they occur
- [ ] Reference issue # in commits

### End of Day (5 min)
- [ ] Final work_log.md summary
- [ ] Update GitHub issue checkboxes
- [ ] Commit with descriptive message
- [ ] Note tomorrow's priority

## Task Breakdown Examples

### Example 1: WebSocket Implementation (6 hours)

```markdown
## BREAKDOWN - WebSocket Implementation
Total Estimate: 6 hours

1. Research Phase (1h)
   - [ ] Review TopStepX WebSocket docs (30m)
   - [ ] Check asyncio best practices (15m)
   - [ ] Design connection architecture (15m)

2. Basic Connection (1.5h)
   - [ ] Create WebSocketClient class (30m)
   - [ ] Implement connect/disconnect (30m)
   - [ ] Add basic error handling (30m)

3. Message Handling (1.5h)
   - [ ] Define message types enum (15m)
   - [ ] Create message parser (45m)
   - [ ] Add callback system (30m)

4. Reconnection Logic (1h)
   - [ ] Implement exponential backoff (30m)
   - [ ] Add connection health monitoring (30m)

5. Testing & Integration (1h)
   - [ ] Unit tests for each component (30m)
   - [ ] Integration test with live data (30m)
```

### Example 2: Bug Fix (2 hours)

```markdown
## BREAKDOWN - Fix Memory Leak in Data Handler
Total Estimate: 2 hours

1. Investigation (45m)
   - [ ] Profile memory usage over time (15m)
   - [ ] Identify growing objects (15m)
   - [ ] Trace object references (15m)

2. Root Cause Analysis (30m)
   - [ ] Check for circular references (15m)
   - [ ] Review event listener cleanup (15m)

3. Implement Fix (30m)
   - [ ] Add proper cleanup methods (15m)
   - [ ] Implement weak references (15m)

4. Verification (15m)
   - [ ] Re-run memory profiler (10m)
   - [ ] Document fix (5m)
```

### Red Flags - Too Vague
- ❌ "Implement trading logic" (20+ hours?)
- ❌ "Fix WebSocket issues" (which ones?)
- ❌ "Add tests" (how many? for what?)

### Good Breakdown Signs
- ✅ 15-30 minute chunks
- ✅ Single responsibility per task
- ✅ Clear completion criteria
- ✅ Confident time estimates

## Work Log Best Practices

### DO:
- Write decisions AS YOU MAKE THEM
- Include error messages and solutions
- Note time for major milestones
- Keep technical details that matter
- Update breakdown checkboxes in real-time

### DON'T:
- Wait until end of day to update
- Write vague entries like "worked on API"
- Skip documenting workarounds
- Delete old logs (archive weekly instead)

## Integration with Claude

When starting a session:
```
"Check work_log.md for where we left off. Today we're working on [specific task from WEEKLY_PLAN.md]"
```

When stuck:
```
"Help me break down [complex task] into 30-minute subtasks"
```

## Commit Message Examples

### Good:
```
[W1-D2] Add WebSocket connection with auto-reconnect

- Implemented exponential backoff
- Handles network interruptions
- Tested with 1-hour continuous stream

Issue: #1
```

### Bad:
```
fix websocket
```

## Weekly Routine

### Monday Morning (20 min)
1. Create/update WEEKLY_PLAN.md from GitHub issue
2. **Break down week into daily goals**
3. **Break down Monday's tasks into subtasks**
4. Create week branch: `git checkout -b week-X-topic`

### Daily
Follow daily workflow above

### Friday Afternoon (15 min)
1. Archive week's work_logs to `logs/week-X/`
2. Update GitHub issue with summary
3. Create PR with week's changes
4. Review what worked/didn't work
5. Plan next week's issue

## Why This System Works

1. **GitHub Issues** = Strategic roadmap visibility
2. **Mandatory breakdowns** = No more "lost 6 hours debugging"
3. **work_log.md** = Critical decision history for trading logic
4. **Real-time updates** = Claude and you stay synced
5. **Minimal overhead** = More coding, less process

## Golden Rule

**If you can't break it down, you don't understand it yet.**

When stuck:
1. Research for 15 minutes
2. Ask Claude for breakdown help
3. Start with what you DO know
4. Add "Research X" as first subtask

Remember: The goal is building a profitable trading bot, not perfect documentation. Keep it simple and useful.