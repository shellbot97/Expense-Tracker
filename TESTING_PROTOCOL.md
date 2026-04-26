# Testing Protocol - Test-First Workflow

## Core Principle
**"No task is complete until tests pass."** Every feature must have comprehensive tests before marking as `completed` in `project_state.json`.

---

## Table of Contents
1. [Testing Philosophy](#testing-philosophy)
2. [Test Types](#test-types)
3. [Test-Driven Development (TDD) Workflow](#test-driven-development-tdd-workflow)
4. [Test Structure](#test-structure)
5. [Coverage Requirements](#coverage-requirements)
6. [Testing Tools](#testing-tools)
7. [Common Test Patterns](#common-test-patterns)
8. [Edge Cases Checklist](#edge-cases-checklist)
9. [Testing Privacy & Security](#testing-privacy--security)
10. [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

### Why Test-First?
1. **Design Clarity**: Writing tests first forces clear interface design
2. **Fewer Bugs**: Catch issues before they reach production
3. **Confidence**: Refactor without fear of breaking things
4. **Documentation**: Tests serve as living documentation
5. **Speed**: Automated tests are faster than manual testing

### Testing Mindset
- **Test behavior, not implementation**: Focus on what, not how
- **Test edge cases**: Empty inputs, nulls, extremes, invalid data
- **Test errors**: Ensure errors are handled gracefully
- **Keep tests simple**: Each test should verify ONE thing
- **Make tests readable**: Tests are documentation

---

## Test Types

### 1. Unit Tests (80% of tests)
**Purpose**: Test individual functions/classes in isolation

**Characteristics**:
- Fast (< 1ms per test)
- No external dependencies (database, API, filesystem)
- Use mocks/stubs for dependencies
- High coverage (aim for 90%+)

**When to Write**:
- For every service, utility, and helper function
- For all business logic
- For data validation and transformation

**Example**:
```python
# tests/unit/services/test_categorization.py
def test_categorize_transaction_matches_first_rule():
    """Should apply first matching rule when multiple rules match."""
    # Arrange
    rules = [
        CategoryRule(id=1, pattern="AMAZON.*", category_id=10, priority=1),
        CategoryRule(id=2, pattern="AMZ", category_id=20, priority=2)
    ]
    transaction = Transaction(description="AMAZON MARKETPLACE")
    engine = CategorizationEngine()
    
    # Act
    result = engine.categorize(transaction, rules)
    
    # Assert
    assert result.category_id == 10
    assert result.rule_id == 1
```

### 2. Integration Tests (15% of tests)
**Purpose**: Test multiple components working together

**Characteristics**:
- Slower (< 100ms per test)
- May use test database
- Test real interactions between modules
- Focus on interfaces between components

**When to Write**:
- For API endpoints (request → database → response)
- For data flow across layers (parser → validator → database)
- For complex workflows (file upload → parse → categorize → store)

**Example**:
```python
# tests/integration/api/test_transaction_endpoints.py
def test_create_transaction_endpoint_success(client, db_session, auth_headers):
    """Should create transaction and return 201 with transaction data."""
    # Arrange
    payload = {
        "amount": 45.99,
        "description": "Coffee shop",
        "transaction_date": "2026-04-26",
        "source_id": 1
    }
    
    # Act
    response = client.post("/api/v1/transactions", json=payload, headers=auth_headers)
    
    # Assert
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["amount"] == 45.99
    assert data["description"] == "Coffee shop"
    
    # Verify database
    transaction = db_session.query(Transaction).filter_by(id=data["id"]).first()
    assert transaction is not None
    assert transaction.amount_cents == 4599
```

### 3. End-to-End Tests (5% of tests)
**Purpose**: Test complete user workflows

**Characteristics**:
- Slowest (seconds per test)
- Use real or near-real environment
- Test from user perspective
- Fewer tests, high value

**When to Write**:
- For critical user journeys (upload statement → view dashboard)
- After MVP is complete
- For regression testing

**Example**:
```python
# tests/e2e/test_statement_upload_workflow.py
def test_complete_statement_upload_workflow(client, auth_token):
    """Should upload CSV, categorize transactions, and make them queryable."""
    # Upload statement
    with open("tests/fixtures/sample_statement.csv", "rb") as f:
        response = client.post(
            "/api/v1/statements/upload",
            files={"file": f},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    assert response.status_code == 201
    
    # Verify transactions are created
    response = client.get("/api/v1/transactions", headers=auth_headers)
    assert len(response.json()["data"]) > 0
    
    # Verify categorization happened
    categorized = [t for t in response.json()["data"] if t["category_id"]]
    assert len(categorized) > 0
```

---

## Test-Driven Development (TDD) Workflow

### The Red-Green-Refactor Cycle

```
1. 🔴 RED: Write failing test
   └─> Test defines desired behavior
   
2. 🟢 GREEN: Write minimal code to pass
   └─> Focus on making it work, not perfect
   
3. 🔵 REFACTOR: Clean up code
   └─> Improve design while keeping tests green
   
4. REPEAT
```

### Example TDD Session

**Task**: Implement function to calculate monthly spending

#### Step 1: Write Test (RED)
```python
# tests/unit/services/test_analytics.py
def test_calculate_monthly_spending_returns_correct_total():
    """Should sum all transactions in given month."""
    # Arrange
    transactions = [
        Transaction(amount_cents=1000, transaction_date=date(2026, 4, 1)),
        Transaction(amount_cents=2500, transaction_date=date(2026, 4, 15)),
        Transaction(amount_cents=500, transaction_date=date(2026, 5, 1)),  # Different month
    ]
    analytics = AnalyticsService()
    
    # Act
    result = analytics.calculate_monthly_spending(transactions, year=2026, month=4)
    
    # Assert
    assert result == 35.00  # (1000 + 2500) / 100

# Run test: pytest tests/unit/services/test_analytics.py
# Result: FAILED (function doesn't exist)
```

#### Step 2: Minimal Implementation (GREEN)
```python
# src/services/analytics.py
class AnalyticsService:
    def calculate_monthly_spending(self, transactions, year, month):
        total_cents = sum(
            t.amount_cents 
            for t in transactions 
            if t.transaction_date.year == year and t.transaction_date.month == month
        )
        return total_cents / 100

# Run test: pytest tests/unit/services/test_analytics.py
# Result: PASSED
```

#### Step 3: Refactor (REFACTOR)
```python
# src/services/analytics.py
from typing import List
from datetime import date

class AnalyticsService:
    def calculate_monthly_spending(
        self,
        transactions: List[Transaction],
        year: int,
        month: int
    ) -> float:
        """
        Calculate total spending for a specific month.
        
        Args:
            transactions: List of transactions to analyze
            year: Target year (e.g., 2026)
            month: Target month (1-12)
            
        Returns:
            Total spending in dollars
        """
        total_cents = sum(
            transaction.amount_cents
            for transaction in transactions
            if self._is_in_month(transaction.transaction_date, year, month)
        )
        return self._cents_to_dollars(total_cents)
    
    def _is_in_month(self, transaction_date: date, year: int, month: int) -> bool:
        return transaction_date.year == year and transaction_date.month == month
    
    def _cents_to_dollars(self, cents: int) -> float:
        return cents / 100

# Run test again: pytest tests/unit/services/test_analytics.py
# Result: PASSED (still works after refactor)
```

#### Step 4: Add Edge Case Tests
```python
def test_calculate_monthly_spending_empty_list_returns_zero():
    analytics = AnalyticsService()
    result = analytics.calculate_monthly_spending([], year=2026, month=4)
    assert result == 0.0

def test_calculate_monthly_spending_no_matches_returns_zero():
    transactions = [
        Transaction(amount_cents=1000, transaction_date=date(2025, 4, 1)),
    ]
    analytics = AnalyticsService()
    result = analytics.calculate_monthly_spending(transactions, year=2026, month=4)
    assert result == 0.0
```

---

## Test Structure

### File Organization
```
tests/
├── unit/                          # Unit tests (mirror src/ structure)
│   ├── services/
│   │   ├── test_auth.py
│   │   ├── test_categorization.py
│   │   └── test_analytics.py
│   ├── parsers/
│   │   ├── test_csv_parser.py
│   │   └── test_excel_parser.py
│   └── utils/
│       └── test_validators.py
├── integration/                   # Integration tests
│   ├── api/
│   │   ├── test_transaction_endpoints.py
│   │   └── test_category_endpoints.py
│   └── services/
│       └── test_ingestion_flow.py
├── e2e/                          # End-to-end tests
│   └── test_user_workflows.py
├── fixtures/                     # Test data
│   ├── sample_statement.csv
│   ├── sample_transactions.json
│   └── test_users.json
└── conftest.py                   # Pytest fixtures and configuration
```

### Test Function Naming
```python
# Pattern: test_<function>_<scenario>_<expected_result>

# ✅ Good names
def test_authenticate_valid_credentials_returns_user():
def test_authenticate_invalid_password_raises_error():
def test_parse_csv_empty_file_raises_validation_error():
def test_categorize_transaction_no_matching_rule_returns_none():

# ❌ Bad names
def test_authenticate():           # Not specific
def test_1():                       # Meaningless
def test_auth_works():             # Vague
```

### AAA Pattern (Arrange-Act-Assert)
```python
def test_create_user_success():
    # Arrange: Set up test data and dependencies
    username = "testuser"
    password = "SecurePass123!"
    auth_service = AuthService(db_session)
    
    # Act: Execute the function being tested
    user = auth_service.create_user(username, password)
    
    # Assert: Verify the results
    assert user.username == username
    assert user.password != password  # Should be hashed
    assert bcrypt.checkpw(password.encode(), user.password.encode())
```

### Pytest Fixtures
```python
# tests/conftest.py
import pytest
from src.config.database import engine, SessionLocal
from src.models import Base

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user(db_session):
    """Create a test user."""
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_headers(sample_user):
    """Generate authentication headers."""
    token = generate_jwt(sample_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_transactions():
    """Generate sample transaction data."""
    return [
        Transaction(amount_cents=1000, description="Coffee", transaction_date=date.today()),
        Transaction(amount_cents=5000, description="Grocery", transaction_date=date.today()),
    ]
```

---

## Coverage Requirements

### Minimum Coverage Targets
- **Overall**: 80% code coverage
- **Services**: 90% coverage (core business logic)
- **API endpoints**: 85% coverage
- **Utils**: 95% coverage (should be simple, pure functions)
- **Models**: 70% coverage (mostly relationships)

### Measuring Coverage
```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Check specific file
pytest --cov=src/services/categorization.py --cov-report=term-missing
```

### Coverage Is Not Everything
**100% coverage ≠ bug-free code**

Must also test:
- Edge cases
- Error conditions
- Integration points
- Performance
- Security

---

## Testing Tools

### Python Stack
```toml
# requirements-dev.txt
pytest==7.4.0                  # Test framework
pytest-cov==4.1.0             # Coverage plugin
pytest-mock==3.11.1           # Mocking utilities
pytest-asyncio==0.21.0        # Async test support
faker==19.3.0                 # Generate fake data
factory-boy==3.3.0            # Test data factories
httpx==0.24.1                 # API testing (FastAPI)
```

### Key Libraries
```python
# Mocking
from unittest.mock import Mock, MagicMock, patch, call
from pytest_mock import mocker

# Factories (for test data)
import factory
from factory import Faker

# Assertions
import pytest
from pytest import raises, warns, approx
```

---

## Common Test Patterns

### 1. Testing Exceptions
```python
def test_create_user_duplicate_username_raises_error():
    auth_service.create_user("testuser", "password1")
    
    with pytest.raises(ValidationError, match="Username already exists"):
        auth_service.create_user("testuser", "password2")
```

### 2. Mocking External Dependencies
```python
def test_categorize_with_ai_calls_llm_api(mocker):
    """Test AI categorization without actually calling API."""
    # Mock the API call
    mock_llm = mocker.patch("src.services.ai.categorization.call_llm_api")
    mock_llm.return_value = {"category": "Food & Dining", "confidence": 0.95}
    
    transaction = Transaction(description="Starbucks")
    result = ai_categorization_service.categorize(transaction)
    
    assert result.category == "Food & Dining"
    mock_llm.assert_called_once_with(
        prompt=mocker.ANY,
        transaction_description="Starbucks"
    )
```

### 3. Testing Database Operations
```python
def test_get_transactions_filters_by_date_range(db_session, sample_user):
    # Create transactions with different dates
    old_tx = Transaction(user_id=sample_user.id, transaction_date=date(2026, 1, 1))
    new_tx = Transaction(user_id=sample_user.id, transaction_date=date(2026, 4, 26))
    db_session.add_all([old_tx, new_tx])
    db_session.commit()
    
    # Query with date filter
    service = TransactionService(db_session)
    results = service.get_transactions(
        user_id=sample_user.id,
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 30)
    )
    
    assert len(results) == 1
    assert results[0].id == new_tx.id
```

### 4. Parametrized Tests (Test Multiple Inputs)
```python
@pytest.mark.parametrize("amount,expected_cents", [
    (10.00, 1000),
    (0.01, 1),
    (999.99, 99999),
    (0, 0),
])
def test_dollars_to_cents_conversion(amount, expected_cents):
    result = convert_dollars_to_cents(amount)
    assert result == expected_cents
```

### 5. Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_fetch_ai_suggestions():
    mock_response = {"suggestions": ["Food", "Dining"]}
    
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        result = await ai_service.fetch_suggestions("Coffee shop")
        
    assert result == ["Food", "Dining"]
```

---

## Edge Cases Checklist

For every function, consider testing:

### Input Validation
- [ ] Empty input ([], "", None, {})
- [ ] Null/undefined values
- [ ] Very large input (1000+ items)
- [ ] Invalid types (string when expecting int)
- [ ] Out of range values (negative when positive expected)
- [ ] Special characters in strings
- [ ] SQL injection attempts
- [ ] XSS attempts (if handling HTML)

### Boundary Conditions
- [ ] Zero
- [ ] One
- [ ] Maximum allowed value
- [ ] Just over maximum
- [ ] Negative numbers (when not allowed)
- [ ] Floating point precision

### Date/Time
- [ ] Dates in the past
- [ ] Dates in the future
- [ ] Leap years
- [ ] Timezone edge cases
- [ ] Daylight saving time transitions

### Lists/Collections
- [ ] Empty list
- [ ] Single item
- [ ] Duplicate items
- [ ] Unordered items
- [ ] Null items in list

### Strings
- [ ] Empty string ""
- [ ] Single character
- [ ] Very long string (>1000 chars)
- [ ] Unicode/emoji
- [ ] Leading/trailing whitespace
- [ ] Only whitespace

### Error Conditions
- [ ] Database connection failure
- [ ] API timeout
- [ ] Permission denied
- [ ] Resource not found
- [ ] Concurrent modification

---

## Testing Privacy & Security

### Privacy Tests
```python
def test_ai_service_blocks_request_without_consent(db_session, sample_user):
    """Should raise error when user hasn't given AI consent."""
    sample_user.ai_consent = False
    db_session.commit()
    
    with pytest.raises(ConsentRequiredError):
        ai_service.categorize_with_ai(transaction, user_id=sample_user.id)

def test_anonymization_removes_pii():
    """Should remove personally identifiable information before AI call."""
    transaction = Transaction(description="John Doe - Coffee at 123 Main St")
    anonymized = anonymization_service.anonymize(transaction)
    
    assert "John Doe" not in anonymized.description
    assert "123 Main St" not in anonymized.description
```

### Security Tests
```python
def test_sql_injection_protection():
    """Should prevent SQL injection in search."""
    malicious_input = "'; DROP TABLE users; --"
    
    # Should not raise error or execute SQL
    results = transaction_service.search(description=malicious_input)
    assert results == []  # No matches, no SQL executed

def test_password_is_hashed():
    """Should never store plain text passwords."""
    user = auth_service.create_user("testuser", "MyPassword123")
    
    assert user.password != "MyPassword123"
    assert len(user.password) > 50  # Hashed string is long
    assert user.password.startswith("$2b$")  # Bcrypt prefix

def test_jwt_expires():
    """Should reject expired JWT tokens."""
    user = User(id=1)
    token = generate_jwt(user.id, expiry_hours=0)  # Already expired
    
    with pytest.raises(AuthenticationError, match="Token expired"):
        validate_jwt(token)
```

---

## CI/CD Integration

### Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: Run tests
        entry: pytest tests/ -v
        language: system
        pass_filenames: false
        always_run: true
```

### GitHub Actions Example
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
      
      - name: Fail if coverage < 80%
        run: |
          coverage report --fail-under=80
```

---

## Testing Checklist (Before Marking Task Complete)

- [ ] **All tests pass**: `pytest tests/` shows all green
- [ ] **Coverage meets target**: Check with `pytest --cov`
- [ ] **Edge cases tested**: See [Edge Cases Checklist](#edge-cases-checklist)
- [ ] **Error cases tested**: Exceptions are handled
- [ ] **Integration tested**: If crosses module boundaries
- [ ] **No skipped tests**: All `@pytest.mark.skip` removed
- [ ] **No warnings**: Run with `pytest -W error`
- [ ] **Tests are fast**: Unit tests < 1ms, integration < 100ms
- [ ] **Tests are isolated**: Can run in any order
- [ ] **Documentation updated**: Docstrings match implementation

---

## Anti-Patterns (What NOT to Do)

❌ **Testing implementation details**
```python
# Bad: Tests internal variable names
def test_calculate():
    calc = Calculator()
    calc.process()
    assert calc._internal_value == 5  # Coupled to implementation
```

❌ **One giant test**
```python
# Bad: Tests everything at once
def test_entire_application():
    # 200 lines of test code...
    assert everything_works
```

❌ **No assertions**
```python
# Bad: Doesn't verify anything
def test_create_user():
    user = auth_service.create_user("test", "pass")
    # No assertions!
```

❌ **Flaky tests** (sometimes pass, sometimes fail)
```python
# Bad: Depends on current time
def test_transaction_is_today():
    tx = create_transaction()
    assert tx.date == datetime.now()  # Fails at midnight!
```

❌ **Tests that depend on order**
```python
# Bad: Tests must run in specific sequence
def test_step_1():
    global user
    user = create_user()

def test_step_2():
    user.update()  # Fails if test_step_1 didn't run first
```

---

## Quick Reference

### Run Tests
```bash
# All tests
pytest

# Specific file
pytest tests/unit/services/test_auth.py

# Specific test
pytest tests/unit/services/test_auth.py::test_authenticate_success

# With coverage
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf

# Parallel execution (faster)
pytest -n auto
```

### Write Test
```python
# tests/unit/services/test_my_service.py
import pytest
from src.services.my_service import MyService

def test_function_name_scenario_expected_result():
    # Arrange
    service = MyService()
    input_data = "test"
    
    # Act
    result = service.process(input_data)
    
    # Assert
    assert result == expected_value
```

---

*Last Updated: 2026-04-26*
*Version: 1.0*
