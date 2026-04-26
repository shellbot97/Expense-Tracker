# Memory Management Strategy

## Purpose
This document defines how to maintain project context across AI coding sessions to:
1. Stay within token limits
2. Reduce repetitive context gathering
3. Maintain coding momentum
4. Ensure consistency across sessions

---

## Core Principle
**"Progressive Summarization"**: As modules are completed, compress detailed code into high-level summaries that AI can reference without loading full source.

---

## File Structure

```
project-root/
├── .ai-memory/                    # AI session memory (gitignored)
│   ├── module-summaries/         # Completed module summaries
│   │   ├── auth-system.md
│   │   ├── data-models.md
│   │   ├── categorization-engine.md
│   │   └── ...
│   ├── active-session.md         # Current session context
│   ├── decisions.md              # ADR (Architecture Decision Records)
│   └── known-issues.md           # Bugs and technical debt
├── project_state.json            # Single source of truth for progress
├── README_DEV.md                 # Architecture overview
└── CONVENTIONS.md                # Coding standards
```

---

## Memory Hierarchy

### Tier 1: Always Load (< 5K tokens)
**Files that should be in every AI session context:**
- `project_state.json` - Current progress and task status
- `README_DEV.md` (Architecture section only) - System design
- `CONVENTIONS.md` (Relevant sections) - Coding standards
- `.ai-memory/active-session.md` - Current work context

**Why**: These provide essential context for any task.

### Tier 2: Load on Demand (Per Module)
**Files loaded when working on specific features:**
- `.ai-memory/module-summaries/<module-name>.md` - Related module summaries
- Actual source code for the feature being modified
- Related tests

**Why**: Only load what's needed for current task.

### Tier 3: Archive (Reference Only)
**Not loaded unless explicitly debugging:**
- Full source code of completed, stable modules
- Old session logs
- Detailed implementation notes

**Why**: Prevents context overflow.

---

## Module Summary Template

When a feature is marked as `completed` in `project_state.json`, create a summary:

**File**: `.ai-memory/module-summaries/<feature-id>-<name>.md`

```markdown
# Module: <Feature Name> (<Feature ID>)
**Status**: Completed
**Completed Date**: 2026-04-26
**Files**: src/services/auth.py, src/models/User.py, tests/unit/test_auth.py

## Purpose
One-sentence description of what this module does.

## Public API
```python
# Key functions/classes other modules use
class AuthService:
    def authenticate(username: str, password: str) -> User
    def create_user(username: str, password: str) -> User
    def validate_token(token: str) -> User
```

## Key Design Decisions
- JWT tokens with 24-hour expiry
- Passwords hashed with bcrypt (12 rounds)
- Refresh tokens stored in database

## Dependencies
- Uses: User model (F002), JWT library
- Used by: All protected API endpoints

## Testing
- 15 unit tests, 100% coverage
- Tested edge cases: expired tokens, invalid passwords, SQL injection attempts

## Known Limitations
- No refresh token rotation yet (planned for F001-ENHANCE)
- Rate limiting not implemented

## Quick Reference
// For common usage patterns
```python
# Standard authentication flow
user = auth_service.authenticate(username, password)
token = auth_service.generate_token(user)
```

## Related Modules
- F002 (Data Models) - User model
- F009 (Privacy Layer) - Consent checks
```

---

## Active Session Tracking

**File**: `.ai-memory/active-session.md`

Update this file at the start and end of each coding session:

```markdown
# Active Session Log

## Current Session (2026-04-26)
**Working On**: F005-T002 (CSV Parser Implementation)
**Status**: In Progress
**Context**: Implementing CSV parser with column mapping support

### Session Goals
- [ ] Parse CSV with flexible column mapping
- [ ] Handle different date formats
- [ ] Validate required columns

### Key Decisions Made
- Using pandas for CSV parsing (handles edge cases better)
- Column mapping stored in user preferences
- Date formats: ISO, MM/DD/YYYY, DD/MM/YYYY

### Next Steps
- Implement date format auto-detection
- Add unit tests for edge cases
- Handle malformed CSV files

### Blockers
None

---

## Previous Session (2026-04-25)
**Completed**: F002-T007 (ORM Models)
**Summary**: Implemented all database models with relationships.
Created summary: .ai-memory/module-summaries/F002-data-models.md
```

---

## Architecture Decision Records (ADR)

**File**: `.ai-memory/decisions.md`

Track important technical decisions:

```markdown
# Architecture Decision Records

## ADR-001: Use PostgreSQL Over SQLite for Production
**Date**: 2026-04-26
**Status**: Accepted
**Context**: Need to choose primary database
**Decision**: PostgreSQL for production, SQLite for testing
**Rationale**: 
- Better concurrency support
- JSONB for flexible data
- Strong analytics query performance
**Consequences**: 
- More complex setup
- Docker required for local dev

## ADR-002: Store Money as Integers (Cents)
**Date**: 2026-04-26
**Status**: Accepted
**Context**: Need to avoid floating-point precision issues
**Decision**: Store all monetary values as integers (cents)
**Rationale**: Prevents 0.1 + 0.2 = 0.30000000000000004 issues
**Consequences**: Must convert to/from dollars in API layer
```

---

## Known Issues Tracking

**File**: `.ai-memory/known-issues.md`

```markdown
# Known Issues & Technical Debt

## Active Bugs
### BUG-001: CSV Parser Fails on Empty Lines
**Severity**: Medium
**Discovered**: 2026-04-26
**Affects**: F005 (Statement Ingestion)
**Workaround**: None yet
**Fix Plan**: Add empty line filtering in next session

## Technical Debt
### DEBT-001: Categorization Engine O(n*m) Complexity
**Priority**: Low (optimize post-MVP)
**Impact**: Slow for users with >100 rules
**Solution**: Implement trie-based regex matching
**Estimated Effort**: 8 hours

### DEBT-002: No Database Connection Pooling
**Priority**: Medium (needed before production)
**Impact**: May hit connection limits under load
**Solution**: Add SQLAlchemy pool configuration
**Estimated Effort**: 2 hours
```

---

## Session Workflow

### Starting a New Session

1. **Load Tier 1 files** (always)
2. **Check** `project_state.json` for current status
3. **Read** `.ai-memory/active-session.md` for context
4. **Load relevant module summaries** (not full source)
5. **Begin work** on specific task

### During Session

1. **Update** `.ai-memory/active-session.md` with progress
2. **Document decisions** in `.ai-memory/decisions.md` if needed
3. **Track bugs** in `.ai-memory/known-issues.md`
4. **Update** `project_state.json` task status

### Ending Session

1. **Complete** `.ai-memory/active-session.md` summary
2. **If feature complete**: Create module summary in `.ai-memory/module-summaries/`
3. **Update** `project_state.json` with final status
4. **Commit changes** with descriptive message

---

## Token Budget Guidelines

### Context Window Management
- **Target**: Keep total context < 50K tokens (leave room for responses)
- **Monitor**: Check token usage when loading multiple files
- **Optimize**: Use summaries instead of full source when possible

### When Context is Full
1. Unload oldest module summaries not related to current task
2. Remove detailed code examples from loaded context
3. Focus on single feature at a time
4. Create more granular summaries

### File Size Estimates
- `project_state.json`: ~5K tokens
- `README_DEV.md` (full): ~4K tokens
- `CONVENTIONS.md` (full): ~6K tokens
- Module summary: ~1K tokens each
- Source file (300 lines): ~2K tokens

---

## Progressive Summarization Process

### When to Summarize
- Feature marked as `completed` in `project_state.json`
- All tests passing
- Code reviewed and merged
- No active work planned on that module

### How to Summarize
1. **Extract public API**: What other modules need to know
2. **Document key decisions**: Why choices were made
3. **Note limitations**: What's not implemented
4. **Provide examples**: Common usage patterns
5. **Link dependencies**: What it uses/what uses it

### What to Exclude
- Implementation details (available in source)
- Verbose code examples (keep to essentials)
- Historical context (keep in git history)
- Debugging notes (unless general lessons)

---

## AI Assistant Instructions

### When Starting Work
```
1. Read project_state.json
2. Read .ai-memory/active-session.md
3. Load summaries for related modules only
4. Ask: "What module summaries should I load for this task?"
```

### During Work
```
- Keep active-session.md updated
- Don't load full source unless modifying it
- Reference module summaries for interfaces
- Ask clarifying questions early
```

### When Completing Feature
```
1. Write comprehensive tests
2. Update project_state.json (mark completed)
3. Create module summary in .ai-memory/module-summaries/
4. Update active-session.md with completion
5. Document any decisions made
```

### If Context Feels Cluttered
```
"I notice the context is getting large. Should I:
1. Create a summary for [completed module]?
2. Unload [unrelated module]?
3. Focus on just [current task]?"
```

---

## Example: Working Across Multiple Sessions

### Session 1: Start Feature F006 (Categorization Engine)
```
1. Load: project_state.json, README_DEV.md, CONVENTIONS.md
2. Load summaries: F002 (data models), F004 (category management)
3. Implement basic regex matching
4. Write initial tests
5. Update active-session.md: "In progress, basic matching works"
```

### Session 2: Continue F006
```
1. Load: project_state.json, active-session.md
2. Load summary: F004 (to check category rule structure)
3. Add rule priority and conflict resolution
4. Complete tests
5. Mark F006 complete in project_state.json
6. Create .ai-memory/module-summaries/F006-categorization-engine.md
```

### Session 3: Start F007 (Transaction API), Needs F006
```
1. Load: project_state.json, active-session.md
2. Load summaries: F002, F006 (needed for this task)
3. Implement API endpoints using categorization_engine
4. Reference F006 summary for function signatures
5. Don't load F006 source code (not modifying it)
```

---

## Maintenance

### Weekly Review
- Check if `.ai-memory/` needs cleanup
- Merge related module summaries if appropriate
- Archive old session logs
- Update known-issues.md status

### Monthly Review
- Update README_DEV.md with architecture changes
- Review and update ADRs
- Consolidate technical debt items
- Update testing protocol if patterns emerged

---

## Tool Integration

### VS Code Copilot
- Use `.copilot-instructions.md` to reference this strategy
- Point to `.ai-memory/` for project-specific context
- Reference module summaries in prompts

### Example Prompt
```
"I need to add a new filter to the transaction API (F007).
Please review:
1. .ai-memory/module-summaries/F007-transaction-api.md
2. CONVENTIONS.md (API Design section)

Then implement the filter following our patterns."
```

---

## Benefits of This Strategy

1. **Reduced Token Usage**: Summaries are 50% smaller than full source
2. **Faster Context Loading**: Load only what's needed
3. **Better Continuity**: Active session file bridges gaps
4. **Decision Preservation**: ADRs prevent revisiting solved problems
5. **Onboarding**: New AI sessions can understand system quickly

---

## Antipatterns to Avoid

❌ **Loading entire codebase every session**
- Use module summaries instead

❌ **No session notes**
- Always update active-session.md

❌ **Detailed summaries**
- Keep summaries concise (target 1K tokens)

❌ **Never updating summaries**
- Refresh when module changes significantly

❌ **Ignoring completed features**
- Mark complete and summarize immediately

---

*Last Updated: 2026-04-26*
*Version: 1.0*
