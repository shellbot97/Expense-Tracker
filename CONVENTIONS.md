# Project Conventions & Standards

## Table of Contents
1. [Directory Structure](#directory-structure)
2. [Naming Conventions](#naming-conventions)
3. [Code Style](#code-style)
4. [Error Handling](#error-handling)
5. [Database Conventions](#database-conventions)
6. [API Design Standards](#api-design-standards)
7. [Testing Standards](#testing-standards)
8. [Documentation Requirements](#documentation-requirements)
9. [Git Workflow](#git-workflow)
10. [Security Standards](#security-standards)

---

## Directory Structure

### Standard Module Organization
```
src/
├── api/              # API routes and controllers (thin layer)
├── services/         # Business logic (core functionality)
├── models/           # Data models and ORM definitions
├── middleware/       # Request/response interceptors
├── utils/            # Shared utilities (pure functions)
├── parsers/          # File/data parsers
├── validators/       # Input validation schemas
├── config/           # Configuration and settings
└── types/            # Type definitions (TypeScript) or schemas
```

### Module Responsibilities
- **api/**: Route definitions, request/response mapping only
- **services/**: All business logic, no direct HTTP handling
- **models/**: Database schema, relationships, basic queries
- **middleware/**: Cross-cutting concerns (auth, logging, validation)
- **utils/**: Stateless, reusable functions with no side effects
- **parsers/**: Data transformation (CSV→JSON, Excel→JSON)

### File Organization Rules
1. One class/main export per file (exceptions: related types/interfaces)
2. Files should be < 300 lines (split if larger)
3. Group related functionality in subdirectories
4. Keep tests adjacent: `src/services/auth/` → `tests/unit/services/auth/`

---

## Naming Conventions

### Files and Directories
```
✅ Good:
- transaction_service.py         # Snake case for Python
- transactionService.js          # Camel case for JavaScript
- CategoryRule.py                # PascalCase for model classes
- csv_parser.py                  # Descriptive, specific

❌ Bad:
- Service.py                     # Too generic
- utils2.py                      # Numbered files
- transaction-service.py         # Inconsistent casing
```

### Variables and Functions
```python
# Python (snake_case)
def calculate_monthly_spending(user_id, start_date, end_date):
    total_amount = 0
    uncategorized_count = 0
    return total_amount

# JavaScript (camelCase)
function calculateMonthlySpending(userId, startDate, endDate) {
    let totalAmount = 0;
    let uncategorizedCount = 0;
    return totalAmount;
}
```

### Classes and Types
```python
# PascalCase for classes
class TransactionService:
    pass

class CategoryMappingRule:
    pass

# Interfaces/Protocols
class IAuthProvider(Protocol):
    pass
```

### Constants
```python
# Python: SCREAMING_SNAKE_CASE
MAX_FILE_SIZE_MB = 10
DEFAULT_CATEGORY_NAME = "Uncategorized"
AI_CONSENT_REQUIRED = True

# JavaScript: SCREAMING_SNAKE_CASE
const MAX_FILE_SIZE_MB = 10;
const DEFAULT_CATEGORY_NAME = "Uncategorized";
const AI_CONSENT_REQUIRED = true;
```

### Database Tables and Columns
```sql
-- Tables: plural, snake_case
CREATE TABLE users (...);
CREATE TABLE transactions (...);
CREATE TABLE category_mapping_rules (...);

-- Columns: snake_case
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    amount_cents INTEGER NOT NULL,  -- Store money as cents
    category_id INTEGER,
    source_id INTEGER NOT NULL,
    description TEXT,
    is_categorized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints
```
RESTful conventions:
GET    /api/v1/transactions           # List/search
GET    /api/v1/transactions/{id}      # Get single
POST   /api/v1/transactions           # Create
PUT    /api/v1/transactions/{id}      # Full update
PATCH  /api/v1/transactions/{id}      # Partial update
DELETE /api/v1/transactions/{id}      # Delete

GET    /api/v1/categories
POST   /api/v1/categories
GET    /api/v1/categories/{id}/rules  # Nested resource

POST   /api/v1/statements/upload      # Action endpoints
POST   /api/v1/transactions/{id}/categorize
```

---

## Code Style

### Python Style (PEP 8 Compliant)
```python
"""Module docstring explaining purpose."""

import os
import sys
from typing import List, Optional, Dict, Any
from datetime import datetime

# Third-party imports
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

# Local imports
from src.models.Transaction import Transaction
from src.services.auth import get_current_user


class TransactionService:
    """Service for transaction management and categorization."""
    
    def __init__(self, db_session):
        """Initialize service with database session."""
        self.db = db_session
    
    def create_transaction(
        self,
        user_id: int,
        amount: float,
        description: str,
        date: datetime,
        source_id: int
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            user_id: User ID who owns the transaction
            amount: Transaction amount in dollars
            description: Transaction description/memo
            date: Transaction date
            source_id: Financial source ID
            
        Returns:
            Transaction: Created transaction object
            
        Raises:
            ValueError: If amount is negative
            DatabaseError: If database operation fails
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        
        # Convert dollars to cents for storage
        amount_cents = int(amount * 100)
        
        transaction = Transaction(
            user_id=user_id,
            amount_cents=amount_cents,
            description=description.strip(),
            transaction_date=date,
            source_id=source_id
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction


# Type hints everywhere
def calculate_total(transactions: List[Transaction]) -> float:
    """Calculate total amount from transaction list."""
    return sum(t.amount_cents for t in transactions) / 100
```

### JavaScript/TypeScript Style
```typescript
/**
 * Service for transaction management and categorization.
 */
export class TransactionService {
    private db: Database;
    
    constructor(db: Database) {
        this.db = db;
    }
    
    /**
     * Create a new transaction.
     * 
     * @param userId - User ID who owns the transaction
     * @param amount - Transaction amount in dollars
     * @param description - Transaction description/memo
     * @param date - Transaction date
     * @param sourceId - Financial source ID
     * @returns Created transaction object
     * @throws {ValueError} If amount is negative
     */
    async createTransaction(
        userId: number,
        amount: number,
        description: string,
        date: Date,
        sourceId: number
    ): Promise<Transaction> {
        if (amount < 0) {
            throw new ValueError("Amount must be non-negative");
        }
        
        // Convert dollars to cents for storage
        const amountCents = Math.round(amount * 100);
        
        const transaction = await this.db.transactions.create({
            userId,
            amountCents,
            description: description.trim(),
            transactionDate: date,
            sourceId,
        });
        
        return transaction;
    }
}
```

### Code Organization Principles
1. **Single Responsibility**: Each function/class does ONE thing
2. **DRY (Don't Repeat Yourself)**: Extract common logic to utils
3. **Separation of Concerns**: Keep layers independent
4. **Explicit > Implicit**: Clear variable names, no magic numbers
5. **Early Returns**: Reduce nesting with guard clauses

```python
# ❌ Bad: Deep nesting
def process_transaction(transaction):
    if transaction:
        if transaction.amount > 0:
            if transaction.category_id:
                return categorize(transaction)
            else:
                return mark_uncategorized(transaction)
    return None

# ✅ Good: Early returns
def process_transaction(transaction):
    if not transaction:
        return None
    
    if transaction.amount <= 0:
        raise ValueError("Amount must be positive")
    
    if not transaction.category_id:
        return mark_uncategorized(transaction)
    
    return categorize(transaction)
```

---

## Error Handling

### Custom Exception Hierarchy
```python
class ExpenseTrackerError(Exception):
    """Base exception for all application errors."""
    pass

class ValidationError(ExpenseTrackerError):
    """Raised when input validation fails."""
    pass

class AuthenticationError(ExpenseTrackerError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(ExpenseTrackerError):
    """Raised when user lacks permission."""
    pass

class ResourceNotFoundError(ExpenseTrackerError):
    """Raised when requested resource doesn't exist."""
    pass

class DataIntegrityError(ExpenseTrackerError):
    """Raised when data constraint is violated."""
    pass

class AIServiceError(ExpenseTrackerError):
    """Raised when AI service call fails."""
    pass
```

### Error Handling Patterns
```python
# Service Layer: Raise specific exceptions
def get_transaction(transaction_id: int, user_id: int) -> Transaction:
    """Get transaction by ID, ensuring user ownership."""
    transaction = db.query(Transaction).filter_by(id=transaction_id).first()
    
    if not transaction:
        raise ResourceNotFoundError(f"Transaction {transaction_id} not found")
    
    if transaction.user_id != user_id:
        raise AuthorizationError("Access denied to this transaction")
    
    return transaction


# API Layer: Convert to HTTP responses
@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction_endpoint(
    transaction_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = transaction_service.get_transaction(
            transaction_id,
            current_user.id
        )
        return transaction
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging Standards
```python
import logging

logger = logging.getLogger(__name__)

# Log levels:
# DEBUG: Detailed diagnostic information
# INFO: General informational messages
# WARNING: Something unexpected but recoverable
# ERROR: Error occurred, operation failed
# CRITICAL: Serious error, application may crash

# ✅ Good logging
logger.info(f"User {user_id} uploaded statement: {filename}")
logger.warning(f"Transaction {tx_id} could not be categorized")
logger.error(f"Failed to parse CSV: {filename}", exc_info=True)

# ❌ Bad logging
logger.info(f"User data: {user}")  # Don't log PII
logger.error("Error occurred")     # Not descriptive
print("Debug message")              # Use logger, not print
```

### Never Log Sensitive Data
```python
# ❌ Bad: Logs sensitive information
logger.info(f"User login: {username} with password {password}")
logger.debug(f"API key: {api_key}")
logger.info(f"Transaction: {transaction}")  # May contain PII

# ✅ Good: Redact or summarize
logger.info(f"User {user_id} authenticated successfully")
logger.debug("API key configured")
logger.info(f"Imported {count} transactions for user {user_id}")
```

---

## Database Conventions

### Schema Design Rules
1. **Use surrogate keys**: Integer primary keys (id), not natural keys
2. **Timestamps**: All tables have `created_at` and `updated_at`
3. **Soft deletes**: Add `deleted_at` for user-visible data
4. **Foreign keys**: Always use constraints with ON DELETE behavior
5. **Money storage**: Store as integers (cents) to avoid float issues

### Model Example
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    
    # Data fields
    transaction_date = Column(DateTime, nullable=False)
    amount_cents = Column(Integer, nullable=False)  # Stored as cents
    description = Column(String(500), nullable=False)
    is_categorized = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category")
    source = relationship("Source")
    
    # Indexes (add in migration)
    __table_args__ = (
        Index("idx_user_date", "user_id", "transaction_date"),
        Index("idx_category", "category_id"),
    )
```

### Query Patterns
```python
# ✅ Good: Use ORM, avoid N+1 queries
transactions = (
    db.query(Transaction)
    .options(joinedload(Transaction.category))  # Eager load
    .filter(Transaction.user_id == user_id)
    .filter(Transaction.transaction_date >= start_date)
    .order_by(Transaction.transaction_date.desc())
    .all()
)

# ❌ Bad: Raw SQL without parameterization
query = f"SELECT * FROM transactions WHERE user_id = {user_id}"  # SQL injection!
results = db.execute(query)
```

---

## API Design Standards

### Response Format
```json
// Success response (200, 201)
{
    "data": {
        "id": 123,
        "amount": 45.99,
        "description": "Coffee shop",
        "category": "Food & Dining"
    },
    "meta": {
        "timestamp": "2026-04-26T10:30:00Z"
    }
}

// List response with pagination
{
    "data": [...],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 145,
        "total_pages": 8
    }
}

// Error response (4xx, 5xx)
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid transaction amount",
        "details": {
            "field": "amount",
            "reason": "must be positive"
        }
    },
    "meta": {
        "timestamp": "2026-04-26T10:30:00Z",
        "request_id": "abc-123-def"
    }
}
```

### Status Codes
- **200 OK**: Successful GET/PUT/PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing/invalid authentication
- **403 Forbidden**: Authenticated but no permission
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Validation failed
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Input Validation
```python
from pydantic import BaseModel, Field, validator
from datetime import date

class TransactionCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in dollars")
    description: str = Field(..., min_length=1, max_length=500)
    transaction_date: date
    source_id: int = Field(..., gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    
    @validator("description")
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()
    
    @validator("transaction_date")
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v
```

---

## Testing Standards

See [TESTING_PROTOCOL.md](./TESTING_PROTOCOL.md) for detailed guidelines.

### Quick Reference
```python
# Test file naming
tests/unit/services/test_transaction_service.py
tests/integration/api/test_transaction_endpoints.py

# Test function naming
def test_create_transaction_success():
    pass

def test_create_transaction_negative_amount_raises_error():
    pass

# AAA pattern: Arrange, Act, Assert
def test_categorization_applies_first_matching_rule():
    # Arrange
    rule1 = CategoryRule(pattern="AMAZON", category_id=1, priority=1)
    rule2 = CategoryRule(pattern="AMZ", category_id=2, priority=2)
    transaction = Transaction(description="AMAZON PURCHASE")
    
    # Act
    result = categorization_engine.categorize(transaction, [rule1, rule2])
    
    # Assert
    assert result.category_id == 1  # First rule matched
```

---

## Documentation Requirements

### Code Documentation
1. **Module docstrings**: Every file starts with purpose description
2. **Class docstrings**: Explain class responsibility
3. **Function docstrings**: Args, returns, raises, examples
4. **Inline comments**: Only for complex/non-obvious logic

```python
def calculate_spending_trend(
    user_id: int,
    category_id: Optional[int],
    start_date: date,
    end_date: date,
    interval: str = "month"
) -> List[Dict[str, Any]]:
    """
    Calculate spending trends over time.
    
    Args:
        user_id: User ID to analyze
        category_id: Optional category filter
        start_date: Start of analysis period (inclusive)
        end_date: End of analysis period (inclusive)
        interval: Aggregation interval ("day", "week", "month", "year")
        
    Returns:
        List of dicts with keys: period, total_amount, transaction_count
        Example: [
            {"period": "2026-04", "total_amount": 1234.56, "transaction_count": 45},
            {"period": "2026-05", "total_amount": 987.65, "transaction_count": 38}
        ]
        
    Raises:
        ValueError: If start_date > end_date or invalid interval
        ResourceNotFoundError: If user doesn't exist
    """
    # Implementation
    pass
```

### README Updates
- Update README_DEV.md when adding new major components
- Document new environment variables in .env.example
- Update architecture diagrams if structure changes

---

## Git Workflow

### Branch Naming
```
feature/F001-T004-jwt-token-management
bugfix/transaction-parser-csv-encoding
hotfix/security-auth-bypass
refactor/categorization-engine-optimization
docs/update-api-documentation
```

### Commit Messages (Conventional Commits)
```
feat(auth): implement JWT token validation [F001-T004]
fix(parser): handle UTF-8 BOM in CSV files
test(categorization): add edge cases for regex matching
docs(readme): update setup instructions
refactor(db): optimize transaction query with indexes
chore(deps): upgrade FastAPI to 0.100.0
```

### Pull Request Template
```markdown
## Description
Brief description of changes

## Related Tasks
- [ ] F001-T004: JWT token management

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows CONVENTIONS.md
- [ ] Documentation updated
- [ ] No linting errors
- [ ] project_state.json updated
```

---

## Security Standards

### Authentication & Authorization
1. Never store passwords in plain text (use bcrypt/argon2)
2. Use JWT with expiration (< 24 hours)
3. Implement refresh token rotation
4. Validate user ownership on all resource access

### Input Validation
1. Validate all user inputs (never trust client)
2. Use parameterized queries (prevent SQL injection)
3. Sanitize file uploads (check type, size, content)
4. Implement rate limiting on all endpoints

### Data Privacy
1. **Never log PII**: passwords, tokens, full names, addresses
2. **Anonymize AI data**: Remove identifiable information before sending
3. **Explicit consent**: Require user approval for AI features
4. **Audit trail**: Log all data sharing events

### Dependencies
1. Pin exact versions in requirements.txt
2. Run security audits: `pip-audit` or `npm audit`
3. Keep dependencies updated (security patches)
4. Review third-party libraries before adding

---

## AI Development Best Practices

### For AI Assistants Working on This Project
1. **Always check** `project_state.json` before starting work
2. **Read relevant code** before making changes (understand context)
3. **Follow TDD**: Write tests first, then implementation
4. **Ask clarifying questions** if requirements are ambiguous
5. **Update documentation** as you go, not after
6. **Mark tasks complete** only after tests pass

### Context Management
- Refer to [MEMORY_STRATEGY.md](./MEMORY_STRATEGY.md) for session continuity
- Update module summaries after completing major features
- Keep prompts focused on specific tasks (avoid scope creep)

---

*Last Updated: 2026-04-26*
*Version: 1.0*
