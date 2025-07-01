# 🎯 AutoSwipe Task Management System

## Overview

The AutoSwipe project uses a sophisticated hierarchical task management system that integrates with Git, provides dependency tracking, and enables intelligent task prioritization.

## Quick Start

```bash
# Initialize a new feature
./task init search-functionality

# Start working on a task
./task status T-001 in_progress

# Check what to work on next
./task next

# Generate daily standup
./task daily

# View critical path
./task critical-path
```

## Task Hierarchy

```
Epic (E-XXX) → Feature (F-XXX) → Story (S-XXX) → Task (T-XXX)
```

- **Epic**: Strategic goals (1-3 months)
- **Feature**: Major deliverables (1-4 weeks)  
- **Story**: User-facing changes (1-5 days)
- **Task**: Implementation units (15min-4h max)

## For Claude AI

When users say certain phrases, Claude will automatically:

| User Says | Claude Does |
|-----------|-------------|
| "let's start on [feature]" | Creates full task breakdown and begins implementation |
| "implement [feature]" | Same as above |
| "update status" | Updates task status in todo_list.md |
| "what's next?" | Shows highest priority unblocked task |
| "show dependencies" | Displays task dependency tree |

## File Structure

```
auto_swipe/
├── tasks.md              # Strategic overview (Epics & Features)
├── todo_list.md          # Tactical execution (Stories & Tasks)
├── .taskrc.json          # Configuration
├── task                  # CLI tool
├── scripts/
│   └── task_manager.py   # Task management logic
└── .github/
    ├── pull_request_template.md
    └── ISSUE_TEMPLATE/
        ├── epic.yml
        └── task.yml
```

## Task Status Workflow

```
pending → in_progress → review → testing → completed
         ↓
      blocked → pending
```

## Dependency Management

Tasks can have dependencies and can block other tasks:

```yaml
T-124: Implement search API
  depends_on: [T-123]  # Can't start until T-123 is done
  blocks: [T-125, T-126]  # These can't start until T-124 is done
  priority: critical  # Because it blocks multiple tasks
```

## Git Integration

### Branch Naming Convention
- Feature: `feature/F-XXX-feature-name`
- Story: `story/S-XXX-story-name`
- Task: `task/T-XXX-task-name`
- Fix: `fix/T-XXX-bug-description`

### Commit Message Format
```
[T-XXX] Brief description

- Detailed change 1
- Detailed change 2

Refs: #XXX
```

## Priority Levels

- **🔴 Critical**: Blocks 3+ tasks (4h SLA)
- **🟠 High**: Blocks 1-2 tasks (8h SLA)
- **🟡 Medium**: No dependencies (24h SLA)
- **🟢 Low**: Nice to have (72h SLA)

## Example: Creating a New Feature

```bash
$ ./task init user-authentication

✅ Created feature breakdown for 'user-authentication':
- 1 feature (F-001)
- 2 stories
- 8 tasks
- Total estimate: 15h
- Branch: feature/F-001-user-authentication

📋 First task:
T-001: Design registration UI (2h)
Dependencies: None
Priority: High

Ready to start? Use: task status T-001 in_progress
```

## Daily Workflow

### Morning
```bash
# Check daily standup
./task daily

# Get next priority task
./task next
```

### During Work
```bash
# Start a task
./task status T-123 in_progress

# If blocked
./task status T-123 blocked

# When done
./task status T-123 completed
```

### End of Day
```bash
# Generate summary
./task summary
```

## Advanced Features

### Sprint Planning
```bash
# Generate optimal sprint plan
./task sprint plan --capacity 40h

# View velocity trends
./task velocity --last 3
```

### Critical Path Analysis
```bash
# Find tasks that could delay the project
./task critical-path E-001

# Output:
CRITICAL PATH (32h total):
T-123 (2h) → T-124 (4h) → T-126 (3h) → T-128 (4h)
⚠️ Delay in any task delays project by same amount
```

### Dependency Visualization
```bash
# Generate visual dependency graph
./task deps --visualize E-001

# Output:
E-001: AI Search
├── F-012: Semantic Search
│   ├── S-045: Natural language input
│   │   ├── T-123: Create embeddings ✅
│   │   ├── T-124: Search API [🚧]
│   │   └── T-125: UI components [⏳]
│   └── S-046: Search filters
│       └── T-126: Filter logic [⏳ blocked by T-124]
```

## Configuration (.taskrc.json)

Key settings:
- `max_task_hours`: 4 (enforce small tasks)
- `sprint_capacity`: 40 (hours per sprint)
- `auto_branch`: true (create Git branches automatically)
- `dependency_check`: true (warn about unmet dependencies)

## Best Practices

1. **Keep tasks small**: Maximum 4 hours
2. **Clear dependencies**: Always specify what blocks what
3. **Update immediately**: Mark tasks complete as soon as done
4. **Use estimates**: Every task needs a time estimate
5. **Regular sync**: Update status every 2 hours of work

## Troubleshooting

### Task seems stuck
```bash
# Check dependencies
./task deps T-124

# Find alternative tasks
./task next --ignore-blocked
```

### Too many tasks
```bash
# Focus on critical path only
./task critical-path --filter current-sprint
```

### Lost track of progress
```bash
# Full status report
./task status --detailed
```

## Integration with Claude

Claude has been configured to automatically use this system. Just say:
- "let's build search" → Full breakdown + implementation starts
- "I'm done with that" → Task marked complete, next task shown
- "what should I do?" → Shows prioritized task list

No need to manually run commands - Claude handles it all!