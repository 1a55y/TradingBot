# Claude Code Chat Memory 🧠

## TOP RULE
**DO NOT CREATE NEW .MD FILES UNTIL ASKED** - This is the #1 rule. No documentation files unless explicitly requested.

## Project Overview
Building a Gold Futures (MGC) trading bot for TopStep evaluation with self-learning capabilities. Bot improves automatically without complex ML.

## Key Decisions Made (Updated 2025-06-28)

### 1. Plan Evolution
- Started with overly complex 20+ module plan
- Simplified to realistic, phased approach
- **FINAL DECISION**: JSON status monitoring (simpler than Jupyter)
- **Flexibility Note**: Plans/structure will evolve during development
- Created comprehensive combined plan with progressive file structure

### 2. Bot Architecture
- **Goal**: Autonomous bot that trades while user sleeps
- **Monitoring**: JSON status files (status.json, trades_today.json)
- **Fallback**: File-based communication for overnight runs
- **File Evolution**: 3 files → 5 files → 7 files → 10 files (progressive)
- **Self-Learning**: Simple tracking system, no complex ML

### 3. Technical Constraints Discovered
- ❌ Claude CANNOT see Cursor's integrated terminal directly
- ❌ Claude CANNOT monitor background processes
- ✅ Claude CAN read/edit Jupyter notebooks (but JSON simpler)
- ✅ Claude CAN read/write files
- ✅ Claude CAN see command outputs when running them

### 4. Strategy Enhancement
- Original SMC guide was missing critical concepts
- Added: Breaker blocks, inducement, ChoCH vs BOS, mitigation blocks
- Created SMC_Strategy_Guide_Enhanced.md with complete methodology
- Pattern scoring system: Only trade 7+ setups
- DXY correlation is critical for gold

### 5. Current Status & Plans
- Active plan: Plans/MainPlan/Overall_Plan/Plan.md (living document)
- Strategy: Plans/MainPlan/SMC_Strategy_Plan/SMC_Strategy.md
- File structure will evolve based on need (not rigid)
- 10-week implementation timeline (flexible, quality over speed)
- Progressive file structure: start with 3, grow as needed

### 6. Self-Learning System (NEW)
- **Pattern Performance Tracking**: Win/loss rates per pattern type
- **Dynamic Position Sizing**: Based on recent 20-trade performance
- **Condition Discovery**: Learn what conditions improve win rate
- **Progressive Complexity**: Start with one pattern, add when profitable
- **No ML Required**: Simple statistics and rule-based adaptation

## Implementation Priority (10-Week Plan - Flexible)

### Weeks 1-2: Foundation (3 files)
- API connection and basic execution
- Everything in bot.py initially
- Test connection and basic trades

### Weeks 3-4: Core Functionality (5 files)
- Split out broker.py and patterns.py
- Order block detection
- Basic signal generation

### Weeks 5-6: Risk & Monitoring (7-8 files)
- Add risk_manager.py and monitoring.py
- JSON status monitoring (not Jupyter)
- Position sizing logic
- Self-learning system basics

### Weeks 7-8: Enhanced Features (10 files)
- Add advanced_patterns.py and learning_system.py
- Breaker blocks (if basics profitable)
- Full self-learning implementation

### Weeks 9-10: Testing & Production
- Complete system testing
- Paper trade minimum 100 trades
- Performance optimization
- Bug fixes and refinements

## Code Context
- Using TopStepX API ($14.50/month)
- Trading MGC (Micro Gold) - $1/tick, $0.10 tick size
- Max risk: $500/trade (start with $250 while learning)
- Position limits: 50 MGC exchange limit, 2-15 MGC typical
- NY Session only (4:45 PM - 10:30 PM Helsinki time)
- Start with 5 MGC positions (bot adjusts based on performance)

## Trading Evolution with Self-Learning
- **Month 1**: 5-8 MGC, order blocks only, 40-45% win rate
- **Month 2**: 10-12 MGC, add breakers if profitable, 45-50% win rate
- **Month 3**: 12-16 MGC, proven patterns only, 50-55% win rate
- Bot automatically adjusts size and patterns based on results

## Monitoring Approach
- **Primary**: JSON files (status.json, trades_today.json, bot_learning.json)
- **Access**: Simple bash commands, jq for parsing
- **Updates**: Every 30 seconds via monitoring.py
- **Future**: Terminal dashboard with rich library (after JSON works)

## Chat Personality Notes
- User wants brutal honesty
- User is experienced and technical
- User has Claude AI Opus Max subscription
- Focus on practical, working solutions
- Avoid overengineering

## Remember for Next Time
- JSON monitoring is the chosen approach (simpler than Jupyter)
- User wants autonomous bot, not babysitting
- Start with 3 files, grow organically to ~10 files
- Test everything before adding complexity
- Breaker blocks are the most important pattern to add
- DXY correlation must be checked for every gold trade
- Pattern scoring: Only trade 7+ quality setups
- Bot learns and improves automatically through simple tracking