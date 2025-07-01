# How We Manage Tasks

## Task Management Philosophy

We use a lightweight, file-based task management system that lives directly in our codebase. This approach keeps task tracking close to the code and ensures all developers have visibility into project progress without needing external tools.

## Where Tasks Live

All task management happens in the `project/` directory:

```
project/
├── PROJECT_TASKS.md      # The main task list - this is where we track what needs to be done
├── EPIC_ROADMAP.md       # High-level project goals broken into epics
├── SPRINT_PLAN.md        # Our 2-week sprint schedule
├── TECHNICAL_DEBT.md     # Things we need to fix or improve
└── WEEKLY_PROGRESS.md    # Weekly updates on what got done
```

## How We Create and Track Tasks

### 1. Task Creation

When we identify work that needs to be done:

1. **Add to PROJECT_TASKS.md** with a unique ID like `TASK-010`
2. **Estimate story points** (1-8 points based on complexity)
3. **Assign to current or future sprint**
4. **Create a GitHub Issue** with the same task number

Example task entry:
```markdown
### TASK-010: Design System Creation (5 points)
**Status**: In Progress (40% complete)
**Assignee**: Team
**Sprint**: Sprint 2

Create a comprehensive design system:
- [ ] Design tokens (colors, typography, spacing)
- [ ] Update app_theme.dart
- [ ] Create component library
- [ ] Documentation
```

### 2. Working on Tasks

When starting a task:

1. **Create a feature branch**: `git checkout -b feature/TASK-010-design-system`
2. **Update task status** in PROJECT_TASKS.md to "In Progress"
3. **Make commits** referencing the task: `git commit -m "[TASK-010] Add color tokens"`
4. **Update progress percentage** as you work

### 3. Completing Tasks

When finishing a task:

1. **Create a Pull Request** with title: `[TASK-010] Design System Creation`
2. **Link the GitHub Issue** in the PR description
3. **Update PROJECT_TASKS.md** status to "Review"
4. **After merge**, update status to "Done"
5. **Update WEEKLY_PROGRESS.md** with completion

## Sprint Management

### Sprint Planning (Every 2 Weeks)

1. **Review backlog** in PROJECT_TASKS.md
2. **Select tasks** totaling ~50 story points
3. **Move tasks** to current sprint section
4. **Update SPRINT_PLAN.md** with sprint goals

### Daily Task Management

- Check PROJECT_TASKS.md for your assigned tasks
- Update task progress percentages
- Note any blockers in the task description
- Communicate delays early

### Sprint Review

At sprint end:
1. **Move completed tasks** to "Completed Tasks" section
2. **Calculate velocity** (story points completed)
3. **Update WEEKLY_PROGRESS.md** with sprint summary
4. **Plan next sprint** based on velocity

## Task States Explained

- **Backlog**: Task identified but not scheduled
- **Sprint X**: Assigned to current/future sprint
- **In Progress**: Actively being worked on (include % complete)
- **Review**: Code complete, in PR review
- **Testing**: Functionality being tested
- **Done**: Merged and deployed

## Task Naming Convention

All tasks follow the format `[TASK-XXX]` where XXX is a three-digit number:
- Example: `TASK-010` for Design System Creation
- Use this format in commit messages, PR titles, and issue references
- Increment numbers sequentially for new tasks

## Epic Management

Larger features are tracked as Epics in EPIC_ROADMAP.md:

1. **Epic 1: Supabase Migration** (95% complete)
   - Migrate from Firebase to Supabase
   - Status: Testing phase
   - All repositories migrated

2. **Epic 2: UI/UX Redesign** (15% complete)
   - Implement modern minimal design system
   - Current: Design tokens created
   - Next: Update app theme

3. **Epic 3: Infrastructure & Testing** (60% complete)
   - CI/CD pipeline setup
   - Test coverage improvement
   - Target: 80% coverage

Tasks are linked to epics to track overall progress.

## Technical Debt Tracking

TECHNICAL_DEBT.md captures:
- Code that needs refactoring
- Performance improvements
- Architecture changes
- Testing gaps

These items become tasks when prioritized in sprint planning.

## Weekly Progress Updates

Every Friday, update WEEKLY_PROGRESS.md with:

```markdown
## Week of June 13, 2025

### Completed
- [TASK-009] Supabase repositories implementation (8 points)
- [TASK-010] Design tokens creation (partial - 2 points)

### In Progress
- [TASK-010] Design System Creation (40% complete)

### Blockers
- None

### Next Week
- Complete TASK-010 design system
- Start TASK-011 component library
```

## Quick Reference Commands

### Creating a New Task
```bash
1. Edit project/PROJECT_TASKS.md
2. Add task with next ID (e.g., TASK-011)
3. Create GitHub Issue
4. Start feature branch: git checkout -b feature/TASK-011-description
```

### Daily Workflow
```bash
1. Check PROJECT_TASKS.md for your tasks
2. Update progress percentage
3. Commit with [TASK-XXX] prefix
4. Update status when done
```

### Commit Message Format
```
[TASK-XXX] Brief description of change

- Detailed change 1
- Detailed change 2
```

### Pull Request Format
- Title: `[TASK-XXX] Feature description`
- Link to GitHub Issue in description
- Update task status to "Review"
- Request code review

## Why This System Works

1. **Visibility**: Tasks live in the codebase where developers work
2. **Simplicity**: Just markdown files, no external tools needed
3. **Integration**: Git history shows task progress naturally
4. **Flexibility**: Easy to adapt and modify for team needs
5. **Accountability**: Clear ownership and progress tracking
6. **Version Control**: Task history tracked in Git

## Best Practices

### Task Size
- Keep tasks between 1-8 story points
- Break larger work into multiple tasks
- One task should be completable in 1-3 days

### Progress Updates
- Update percentages daily if actively working
- Note blockers immediately in task description
- Move to correct status promptly

### Code Quality
- All task code must pass linting
- Include tests for new features
- Update documentation as needed

## Current Sprint Status

- **Sprint 2**: June 13-27, 2025
- **Progress**: 35/50 story points completed
- **Focus**: UI/UX Redesign Epic
- **Active Tasks**: TASK-010 (Design System)
- **Velocity**: On track for 45-50 points

## Getting Started

For new team members:
1. Read through `project/PROJECT_TASKS.md` to see current work
2. Check `EPIC_ROADMAP.md` for project vision
3. Look for "good first issue" tasks in backlog
4. Create your first feature branch and start contributing!