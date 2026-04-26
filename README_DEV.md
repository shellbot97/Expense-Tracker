# Developer README - Personal Expense Tracker

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Design](#architecture-design)
3. [Technology Stack](#technology-stack)
4. [Setup Instructions](#setup-instructions)
5. [Development Workflow](#development-workflow)
6. [Environment Assumptions](#environment-assumptions)
7. [Known Limitations](#known-limitations)
8. [Project Structure](#project-structure)

---

## Project Overview

A privacy-first, AI-augmented expense management system designed for granular control over personal finance data. The system prioritizes **local data ownership** with optional cloud-based AI features requiring explicit user consent.

### Core Principles
- **Privacy First**: All data processing is local by default
- **Modular Design**: Loosely coupled components for easy maintenance and testing
- **Test-First**: No feature is complete without comprehensive tests
- **Extensibility**: Plugin architecture for categorization rules and data sources

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Future)                       │
│            React/Vue Dashboard + Chat Interface             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                      │
│              Authentication & Request Routing               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│  Data Engine  │    │  Intelligence  │    │ User Config  │
│               │    │     Layer      │    │  Management  │
│ • Ingestion   │    │ • Analytics    │    │ • Sources    │
│ • Parsing     │    │ • Aggregation  │    │ • Categories │
│ • Validation  │    │ • Anomalies    │    │ • Rules      │
└───────────────┘    └────────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                   ┌──────────────────────┐
                   │ Categorization Engine │
                   │  (Local Regex-based)  │
                   └──────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   Privacy Gateway    │
                   │  (Consent Manager)   │
                   └──────────────────────┘
                              │
                              ▼ (Opt-in only)
                   ┌──────────────────────┐
                   │   AI Services Layer   │
                   │ • Smart Categorize   │
                   │ • Chat Interface     │
                   │ • Insights           │
                   └──────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Persistence                        │
│          Database (PostgreSQL/SQLite) + Cache               │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **API Gateway Layer**
- **Purpose**: Entry point for all requests, handles authentication, rate limiting
- **Key Files**: `src/api/`, `src/middleware/auth.js`
- **Dependencies**: JWT library, request validation

#### 2. **Data Processing Engine**
- **Purpose**: Ingest, parse, and validate financial statements
- **Key Modules**:
  - `StatementParser`: CSV/Excel parsing with column mapping
  - `TransactionValidator`: Data sanitization and validation
  - `DuplicateDetector`: Prevents duplicate imports
- **Key Files**: `src/services/ingestion/`, `src/parsers/`

#### 3. **Categorization Engine**
- **Purpose**: Local, regex-based transaction classification
- **Algorithm**:
  1. Load user-defined category rules (sorted by priority)
  2. For each transaction, test description against regex patterns
  3. Apply first matching rule
  4. Flag uncategorized transactions for manual review
- **Key Files**: `src/services/categorization/`, `src/models/CategoryRule.js`
- **Performance**: O(n*m) where n=transactions, m=rules (optimizable with trie)

#### 4. **Intelligence Layer**
- **Purpose**: Analytics, aggregation, and anomaly detection
- **Components**:
  - `AnalyticsService`: Spending summaries by category/source/time
  - `AnomalyDetector`: Statistical outlier detection
  - `TrendAnalyzer`: Time-series analysis
- **Key Files**: `src/services/analytics/`

#### 5. **Privacy & Consent Gateway**
- **Purpose**: Controls data flow to external AI services
- **Behavior**:
  - Blocks AI requests unless user has granted explicit consent
  - Anonymizes data before sending to AI (removes PII)
  - Logs all data sharing events for audit
- **Key Files**: `src/middleware/privacy.js`, `src/services/consent/`

#### 6. **AI Services Layer (Opt-in)**
- **Purpose**: Cloud-based intelligent features
- **Features**:
  - Smart categorization suggestions
  - Natural language chat interface for insights
  - Savings recommendations
- **Key Files**: `src/services/ai/`, `src/integrations/llm/`
- **Note**: All AI features require `F009` (Privacy Layer) to be completed first

---

## Technology Stack

### Backend (To Be Decided)
**Options:**
- **Python (FastAPI/Django)**: Best for data processing, ML integrations
- **Node.js (Express/NestJS)**: Fast development, large ecosystem
- **Go**: High performance, excellent concurrency

**Recommendation**: Python with FastAPI for rapid prototyping and AI integrations

### Database
**Options:**
- **PostgreSQL**: Robust, excellent for analytics queries
- **SQLite**: Simplest for single-user, local-first approach

**Recommendation**: PostgreSQL for production, SQLite for dev/testing

### AI Provider
**Options:**
- **OpenAI (GPT-4)**: Most capable, higher cost
- **Anthropic (Claude)**: Strong reasoning, privacy-focused
- **Local LLM (Ollama/LLaMA)**: Fully private, no API costs

**Recommendation**: Start with Anthropic for privacy alignment

### Testing
- **Unit Tests**: pytest (Python) / Jest (Node.js)
- **Integration Tests**: pytest with fixtures / Supertest
- **E2E Tests**: To be added post-MVP

---

## Setup Instructions

### Prerequisites
```bash
# Check versions
python --version  # 3.10+ required
node --version    # 18+ required (if using Node)
docker --version  # 24+ required
```

### Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd expense-tracking-system

# 2. Create virtual environment (Python example)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL
# - JWT_SECRET
# - AI_API_KEY (optional, for AI features)

# 5. Initialize database
python scripts/init_db.py

# 6. Run migrations
alembic upgrade head  # or your migration tool

# 7. (Optional) Seed with sample data
python scripts/seed_data.py

# 8. Run tests
pytest tests/

# 9. Start development server
uvicorn main:app --reload
```

### Docker Setup (Alternative)

```bash
# Build and run all services
docker-compose up --build

# Run tests in container
docker-compose run api pytest

# Access database
docker-compose exec db psql -U postgres
```

---

## Development Workflow

### Before Starting a Task
1. Pull latest changes: `git pull origin main`
2. Create feature branch: `git checkout -b feature/F001-T001-auth-schema`
3. Check task dependencies in `project_state.json`
4. Update task status to `in-progress`

### During Development
1. **Write tests first** (TDD approach)
2. Implement feature
3. Run tests: `pytest tests/test_<module>.py`
4. Run linter: `flake8 src/` or `eslint src/`
5. Commit with descriptive message: `git commit -m "feat(auth): implement JWT token validation [F001-T004]"`

### Before Marking Task Complete
1. ✅ All unit tests pass
2. ✅ Code coverage > 80% for new code
3. ✅ No linting errors
4. ✅ Documentation updated (docstrings, README if needed)
5. ✅ Manual testing completed
6. ✅ Update `project_state.json` task status to `completed`

### Code Review Checklist
- [ ] Follows naming conventions (see `CONVENTIONS.md`)
- [ ] Error handling implemented
- [ ] Input validation present
- [ ] No hardcoded secrets
- [ ] Tests cover edge cases
- [ ] Privacy rules respected (no PII logging)

---

## Environment Assumptions

### Development Environment
- **OS**: macOS/Linux/Windows with WSL2
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Network**: Internet required for AI features only

### Runtime Environment
- **Database**: Persistent storage required
- **File System**: Write access for uploaded statements
- **Ports**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis/optional)

### Third-Party Dependencies
- **Required**: None (core features work offline)
- **Optional**: 
  - AI API keys (OpenAI/Anthropic) for smart features
  - Email service (for future notifications)

---

## Known Limitations

### Current Phase (Initialization)
- [ ] No frontend implemented yet
- [ ] AI features not built (F010, F011)
- [ ] No user authentication (F001 pending)
- [ ] No data persistence (F002 pending)

### Technical Debt / Future Improvements
1. **Performance**:
   - Categorization engine O(n*m) complexity (consider trie-based matching)
   - No caching layer yet (add Redis for frequent queries)
   - File uploads not streaming (switch to chunked uploads for large files)

2. **Security**:
   - JWT refresh tokens not implemented
   - No rate limiting on API endpoints
   - No CSRF protection (add for future web interface)
   - Password reset flow not designed

3. **Scalability**:
   - Single-user architecture (multi-tenancy requires refactor)
   - No horizontal scaling strategy
   - Database connection pooling not configured

4. **Data Model**:
   - No soft deletes (all deletes are hard)
   - No audit trail for data changes
   - Transaction history not versioned

5. **AI Features**:
   - No fallback if AI service is down
   - Prompt injection not fully mitigated
   - Context window limitations for large datasets
   - No local LLM option implemented yet

6. **Testing**:
   - No integration tests yet
   - No performance/load tests
   - No E2E tests

### Design Constraints from PRD
1. **Privacy-First Architecture**: AI features must always be opt-in
2. **Local Processing**: Core categorization must work without internet
3. **Single-User Focus**: Not designed for multi-user scenarios initially
4. **Data Ownership**: User data never leaves system without explicit consent

---

## Project Structure

```
expense-tracking-system/
├── Docs/                          # Documentation
│   ├── super-primitive-PRD.md     # Product requirements
│   ├── example-prompts.md         # AI prompt examples
│   └── architecture/              # Architecture diagrams
├── project_state.json             # Task tracking and project status
├── README_DEV.md                  # This file
├── CONVENTIONS.md                 # Coding standards and conventions
├── TESTING_PROTOCOL.md            # Testing guidelines
├── MEMORY_STRATEGY.md             # Context management for AI sessions
│
├── src/                           # Source code
│   ├── api/                       # API routes and controllers
│   │   ├── auth.py
│   │   ├── transactions.py
│   │   ├── categories.py
│   │   └── sources.py
│   ├── services/                  # Business logic
│   │   ├── ingestion/            # File parsing and import
│   │   ├── categorization/       # Rule-based categorization
│   │   ├── analytics/            # Aggregation and insights
│   │   ├── ai/                   # AI integrations (opt-in)
│   │   └── consent/              # Privacy and consent management
│   ├── models/                    # Data models (ORM)
│   │   ├── User.py
│   │   ├── Transaction.py
│   │   ├── Category.py
│   │   ├── Source.py
│   │   └── CategoryRule.py
│   ├── middleware/                # Request/response middleware
│   │   ├── auth.py
│   │   ├── privacy.py
│   │   └── validation.py
│   ├── utils/                     # Shared utilities
│   │   ├── regex_helpers.py
│   │   ├── date_utils.py
│   │   └── validators.py
│   ├── parsers/                   # Statement parsers
│   │   ├── csv_parser.py
│   │   └── excel_parser.py
│   └── config/                    # Configuration
│       ├── settings.py
│       └── database.py
│
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── fixtures/                  # Test data
│   └── conftest.py               # Pytest configuration
│
├── scripts/                       # Utility scripts
│   ├── init_db.py                # Database initialization
│   ├── seed_data.py              # Sample data seeding
│   └── migrate.py                # Migration runner
│
├── migrations/                    # Database migrations
├── docker/                        # Docker configurations
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── docker-compose.yml            # Local dev environment
└── pytest.ini                     # Test configuration
```

---

## Quick Reference

### Common Commands
```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/unit/test_categorization.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run linter
flake8 src/

# Format code
black src/

# Start dev server
uvicorn main:app --reload

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Update project state
# Edit project_state.json manually or use CLI tool (to be built)
```

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/expense_tracker
JWT_SECRET=your-secret-key-change-me
JWT_EXPIRY_HOURS=24
AI_PROVIDER=anthropic  # openai, anthropic, or local
AI_API_KEY=sk-...
LOG_LEVEL=INFO
ENVIRONMENT=development  # development, staging, production
```

---

## Next Steps

1. **Decide Technology Stack**: Choose backend language (Python recommended)
2. **Set Up Project Scaffold**: Create directory structure, install dependencies
3. **Start with F001 & F002**: Authentication and data models are foundation
4. **Implement Core MVP**: Focus on F001-F007 for first usable version
5. **Add Tests Continuously**: Never mark a task complete without tests

---

## Support & Resources

- **Project State**: Always refer to `project_state.json` for current progress
- **Conventions**: Check `CONVENTIONS.md` before writing code
- **Testing**: Follow `TESTING_PROTOCOL.md` guidelines
- **AI Sessions**: Use `MEMORY_STRATEGY.md` to manage long-term context

---

*Last Updated: 2026-04-26*
*Project Phase: Initialization*
