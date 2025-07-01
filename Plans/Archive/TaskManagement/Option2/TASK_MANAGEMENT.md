# Task Management System

A simple, git-based task management system for the EU Whistleblowing Platform project.

## How It Works

### 1. TASKS.md (Strategic View - The PLAN)
- Complete 4-week breakdown of all tasks
- Shows dependencies and blockers
- Updated only when tasks are completed or scope changes
- Reference: `W1-D1` = Week 1, Day 1
- Large tasks (>4h) get broken down into subtasks

### 2. todo_list.md (Daily Execution - The REALITY)
- **Living document** updated throughout the work session
- New entry created at start of each work session
- **Real-time updates** as work progresses:
  - Task breakdown at start
  - "In Progress" section updated as subtasks complete
  - Technical decisions documented as they're made
  - Blockers noted when encountered
  - Time tracked for each subtask
- Becomes the permanent historical record
- Newest entries at the top

### 3. Git Integration
- **Branches:** One per week (`week1-foundation`, `week2-core-features`, etc.)
- **Commits:** Daily with format `[W1-D1] Clear description`
- **Merges:** Weekly to main branch

## Daily Workflow

1. **Start of work session:**
   - Check TASKS.md for today's goals
   - Review yesterday's entry in todo_list.md for blockers/decisions
   - Create new entry in todo_list.md with date and task name
   - Break down large tasks into subtasks (1-2h each)
   - Create/switch to appropriate git branch

2. **During work (LIVE UPDATES):**
   - Update "In Progress" section in todo_list.md as subtasks complete
   - Document technical decisions immediately
   - Note blockers as they appear
   - Track actual time for each subtask
   - Make commits referencing the task: `[W1-D1] Description`

3. **End of work session:**
   - Final update to todo_list.md with complete summary
   - Check off completed items in TASKS.md
   - Ensure all decisions and blockers are documented
   - Push your branch

## Example Git Commands

```bash
# Start week 1
git checkout -b week1-foundation

# Daily commit
git add .
git commit -m "[W1-D1] Set up Supabase project and schema"
git push origin week1-foundation

# End of week merge
git checkout main
git merge week1-foundation
git push origin main
```

## Key Principles

1. **todo_list.md is a living document** - Update it throughout the day, not just at the end
2. **Break down large tasks** - Nothing larger than 4 hours, ideally 1-2 hour chunks
3. **Document decisions immediately** - Don't wait until end of day
4. **Track actual time** - Helps improve future estimates
5. **TASKS.md shows the plan, todo_list.md shows reality**

## Benefits
- Git history shows real progress timeline
- Decisions are documented in context
- Blockers are tracked and resolved
- Time estimates improve over time
- Zero overhead - just markdown and git
- Historical record of how the project actually developed