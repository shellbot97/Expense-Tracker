# Quick Start Guide

## For Immediate Development

This guide will get you from initialization to writing your first feature.

---

## Step 1: Choose Your Technology Stack

**Recommended**: Python with FastAPI

### Why Python?
- Excellent data processing libraries (pandas, numpy)
- Easy AI integration (OpenAI, Anthropic SDKs)
- Rich ecosystem for financial applications
- FastAPI provides automatic API documentation

### Alternative Options
- **Node.js (Express/NestJS)**: If you prefer JavaScript
- **Go**: If you need maximum performance

**Decision Point**: Choose now and document in `.ai-memory/decisions.md`

---

## Step 2: Set Up Project Structure

### Create Directory Structure
```bash
# From project root
mkdir -p src/api src/services src/models src/middleware src/utils src/parsers src/config
mkdir -p tests/unit tests/integration tests/fixtures
mkdir -p scripts migrations docker
```

### Install Python (if not installed)
```bash
# Check version
python3 --version  # Should be 3.10+

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Create requirements.txt
```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Data Processing
pandas==2.1.3
openpyxl==3.1.2

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.25.1

# Code Quality
black==23.11.0
flake8==6.1.0
mypy==1.7.1
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Step 3: Set Up Database

### Option A: Docker (Recommended)
```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: expense_user
      POSTGRES_PASSWORD: dev_password_change_me
      POSTGRES_DB: expense_tracker
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

# Start database
docker-compose up -d

# Verify it's running
docker-compose ps
```

### Option B: Local PostgreSQL
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15

# Create database
createdb expense_tracker
```

---

## Step 4: Create Environment File

```bash
# Create .env file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://expense_user:dev_password_change_me@localhost:5432/expense_tracker

# Security
JWT_SECRET=your-secret-key-change-this-to-random-string
JWT_EXPIRY_HOURS=24

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# AI (Optional - for later)
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-...

# Server
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

---

## Step 5: Initialize Project

### Create Main Application File
```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Personal Expense Tracker",
    description="Privacy-first expense management system",
    version="0.1.0"
)

# CORS (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Expense Tracker API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Test It Works
```bash
# Start server
uvicorn src.main:app --reload

# In another terminal, test
curl http://localhost:8000/
# Should return: {"message":"Expense Tracker API","version":"0.1.0"}

# View auto-generated API docs
open http://localhost:8000/docs
```

---

## Step 6: Start First Feature (F001 - Authentication)

### Update project_state.json
```json
// Mark F001 as in-progress
{
  "id": "F001",
  "status": "in-progress",
  ...
}
```

### Create First Test (TDD!)
```python
# tests/unit/services/test_auth.py
import pytest
from src.services.auth import AuthService

def test_register_user_creates_new_user():
    """Should create a new user with hashed password."""
    # Arrange
    auth_service = AuthService()
    
    # Act
    user = auth_service.register_user(
        username="testuser",
        email="test@example.com",
        password="SecurePass123!"
    )
    
    # Assert
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password != "SecurePass123!"  # Should be hashed
```

### Run Test (It Will Fail - That's TDD!)
```bash
pytest tests/unit/services/test_auth.py
# Result: FAILED (AuthService doesn't exist yet)
```

### Implement Minimal Code
```python
# src/services/auth.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class AuthService:
    def register_user(self, username: str, email: str, password: str) -> User:
        hashed_password = pwd_context.hash(password)
        return User(username, email, hashed_password)
```

### Run Test Again
```bash
pytest tests/unit/services/test_auth.py
# Result: PASSED ✓
```

### Continue TDD Cycle
Repeat for all tasks in F001:
1. Write test (RED)
2. Write minimal code (GREEN)
3. Refactor (BLUE)
4. Add more tests

---

## Step 7: Update Documentation as You Go

### After Completing a Task
1. Update `project_state.json` task status
2. Update `.ai-memory/active-session.md` with progress
3. Document any decisions in `.ai-memory/decisions.md`

### After Completing a Feature
1. Mark feature as `completed` in `project_state.json`
2. Create module summary in `.ai-memory/module-summaries/`
3. Commit changes with descriptive message

---

## Daily Workflow

### Starting Your Day
```bash
# 1. Pull latest changes
git pull

# 2. Check project state
cat project_state.json | grep "in-progress"

# 3. Read active session
cat .ai-memory/active-session.md

# 4. Activate environment
source venv/bin/activate

# 5. Start database
docker-compose up -d

# 6. Run tests (make sure everything still works)
pytest

# 7. Start server
uvicorn src.main:app --reload
```

### During Development
1. **Before coding**: Write test first
2. **While coding**: Follow CONVENTIONS.md
3. **After coding**: Run tests, update docs
4. **Before commit**: Run linter

```bash
# Run tests
pytest tests/

# Run linter
flake8 src/

# Format code
black src/

# Type check
mypy src/
```

### Ending Your Day
```bash
# 1. Run full test suite
pytest --cov=src

# 2. Update active-session.md
# Document progress, blockers, next steps

# 3. Update project_state.json
# Mark completed tasks

# 4. Commit work
git add .
git commit -m "feat(auth): implement user registration [F001-T002]"

# 5. Push (if using remote)
git push
```

---

## Common Commands Reference

```bash
# Database
docker-compose up -d                    # Start database
docker-compose down                     # Stop database
docker-compose exec db psql -U expense_user -d expense_tracker  # Connect to DB

# Testing
pytest                                  # Run all tests
pytest tests/unit/                      # Unit tests only
pytest -v                              # Verbose output
pytest -k test_auth                    # Run specific test
pytest --cov=src --cov-report=html     # With coverage

# Code Quality
black src/                             # Format code
flake8 src/                            # Lint code
mypy src/                              # Type check

# Server
uvicorn src.main:app --reload          # Development server
uvicorn src.main:app --host 0.0.0.0 --port 8000  # Production-like

# Git
git checkout -b feature/F001-T001      # New feature branch
git commit -m "feat(auth): description" # Commit with convention
git push origin feature/F001-T001      # Push branch
```

---

## Troubleshooting

### Database Connection Fails
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs db

# Restart
docker-compose restart db
```

### Import Errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Failing
```bash
# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/services/test_auth.py -v

# Check if database is in clean state
# (Integration tests may need reset)
```

---

## Next Steps

1. ✅ **Technology chosen**: Python + FastAPI
2. ✅ **Project structure created**: Directories set up
3. ✅ **Database running**: PostgreSQL ready
4. ✅ **First test written**: TDD cycle started
5. ⏭️ **Continue F001**: Complete all authentication tasks
6. ⏭️ **Move to F002**: Design database models
7. ⏭️ **Build F003-F007**: Core MVP features

---

## Resources

- **Project State**: `project_state.json`
- **Architecture**: `README_DEV.md`
- **Conventions**: `CONVENTIONS.md`
- **Testing**: `TESTING_PROTOCOL.md`
- **Memory Strategy**: `MEMORY_STRATEGY.md`
- **API Docs**: http://localhost:8000/docs (when server running)

---

**You're ready to build!** Start with F001 (Authentication) and follow the TDD workflow.

*Last Updated: 2026-04-26*
