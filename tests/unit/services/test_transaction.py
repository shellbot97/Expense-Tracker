"""
Unit tests for transaction service
Following TDD: Write tests first, then implement
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.database import Base
from src.models.user import User
from src.models.category import Category
from src.models.source import Source
from src.models.transaction import Transaction
from src.models.budget import Budget  # Import to resolve relationships
from src.services.transaction_service import TransactionService
from src.utils.exceptions import (
    ValidationError,
    NotFoundError,
    DatabaseError,
)
from tests.fixtures.transaction_fixtures import (
    valid_transaction_data,
    valid_transaction_with_category_source,
    invalid_transaction_data,
    transaction_filter_params,
)


@pytest.fixture
def db_session(tmp_path):
    """Create a temporary database for testing"""
    db_path = tmp_path / "test_transactions.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$test_hash",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_category(db_session, test_user):
    """Create a test category"""
    category = Category(
        user_id=test_user.id,
        name="Groceries",
        category_type="expense",
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_source(db_session, test_user):
    """Create a test source"""
    source = Source(
        user_id=test_user.id,
        name="Chase Checking",
        source_type="bank_account",
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    return source


@pytest.fixture
def transaction_service(db_session):
    """Create transaction service instance"""
    return TransactionService(db_session)


class TestCreateTransaction:
    """Test transaction creation"""

    def test_create_basic_transaction(self, transaction_service, test_user, valid_transaction_data):
        """Test: Can create a basic transaction"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            **valid_transaction_data
        )

        assert transaction.id is not None
        assert transaction.user_id == test_user.id
        assert transaction.description == valid_transaction_data["description"]
        assert transaction.amount == valid_transaction_data["amount"]
        assert transaction.transaction_type == valid_transaction_data["transaction_type"]

    def test_create_transaction_with_category_and_source(
        self, transaction_service, test_user, test_category, test_source
    ):
        """Test: Can create transaction with category and source"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            description="Test transaction",
            amount=5000,
            transaction_type="expense",
            transaction_date=date.today(),
            category_id=test_category.id,
            source_id=test_source.id,
        )

        assert transaction.category_id == test_category.id
        assert transaction.source_id == test_source.id

    def test_create_transaction_empty_description_raises_error(
        self, transaction_service, test_user
    ):
        """Test: Empty description raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            transaction_service.create_transaction(
                user_id=test_user.id,
                description="",
                amount=1000,
                transaction_type="expense",
                transaction_date=date.today(),
            )
        assert "description" in str(exc_info.value).lower()

    def test_create_transaction_negative_amount_raises_error(
        self, transaction_service, test_user
    ):
        """Test: Negative amount raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            transaction_service.create_transaction(
                user_id=test_user.id,
                description="Test",
                amount=-100,
                transaction_type="expense",
                transaction_date=date.today(),
            )
        assert "amount" in str(exc_info.value).lower()

    def test_create_transaction_invalid_type_raises_error(
        self, transaction_service, test_user
    ):
        """Test: Invalid transaction type raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            transaction_service.create_transaction(
                user_id=test_user.id,
                description="Test",
                amount=1000,
                transaction_type="invalid_type",
                transaction_date=date.today(),
            )
        assert "transaction_type" in str(exc_info.value).lower()


class TestGetTransaction:
    """Test getting transactions"""

    def test_get_transaction_by_id(self, transaction_service, test_user):
        """Test: Can retrieve transaction by ID"""
        # Create transaction
        created = transaction_service.create_transaction(
            user_id=test_user.id,
            description="Test transaction",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )

        # Retrieve it
        retrieved = transaction_service.get_transaction(created.id, test_user.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.description == created.description

    def test_get_nonexistent_transaction_returns_none(self, transaction_service, test_user):
        """Test: Getting non-existent transaction returns None"""
        result = transaction_service.get_transaction(99999, test_user.id)
        assert result is None

    def test_get_transaction_wrong_user_returns_none(
        self, transaction_service, test_user, db_session
    ):
        """Test: Cannot retrieve another user's transaction"""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hash",
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # Create transaction for test_user
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            description="Test",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )

        # Try to get with other_user's ID
        result = transaction_service.get_transaction(transaction.id, other_user.id)
        assert result is None


class TestListTransactions:
    """Test listing transactions"""

    def test_list_user_transactions(self, transaction_service, test_user):
        """Test: Can list all user's transactions"""
        # Create multiple transactions
        for i in range(3):
            transaction_service.create_transaction(
                user_id=test_user.id,
                description=f"Transaction {i}",
                amount=1000 * (i + 1),
                transaction_type="expense",
                transaction_date=date.today(),
            )

        transactions = transaction_service.list_transactions(test_user.id)

        assert len(transactions) == 3
        assert all(t.user_id == test_user.id for t in transactions)

    def test_list_transactions_with_date_filter(self, transaction_service, test_user):
        """Test: Can filter transactions by date range"""
        # Create transactions on different dates
        today = date.today()
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Today",
            amount=1000,
            transaction_type="expense",
            transaction_date=today,
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Last week",
            amount=2000,
            transaction_type="expense",
            transaction_date=today - timedelta(days=7),
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Last month",
            amount=3000,
            transaction_type="expense",
            transaction_date=today - timedelta(days=30),
        )

        # Filter for last 10 days
        start_date = today - timedelta(days=10)
        transactions = transaction_service.list_transactions(
            user_id=test_user.id,
            start_date=start_date,
            end_date=today,
        )

        assert len(transactions) == 2  # Today and last week

    def test_list_transactions_with_type_filter(self, transaction_service, test_user):
        """Test: Can filter by transaction type"""
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Expense",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Income",
            amount=5000,
            transaction_type="income",
            transaction_date=date.today(),
        )

        expenses = transaction_service.list_transactions(
            user_id=test_user.id,
            transaction_type="expense",
        )

        assert len(expenses) == 1
        assert expenses[0].transaction_type == "expense"

    def test_list_transactions_pagination(self, transaction_service, test_user):
        """Test: Pagination works correctly"""
        # Create 10 transactions
        for i in range(10):
            transaction_service.create_transaction(
                user_id=test_user.id,
                description=f"Transaction {i}",
                amount=1000,
                transaction_type="expense",
                transaction_date=date.today(),
            )

        # Get first page
        page1 = transaction_service.list_transactions(
            user_id=test_user.id,
            limit=5,
            offset=0,
        )

        # Get second page
        page2 = transaction_service.list_transactions(
            user_id=test_user.id,
            limit=5,
            offset=5,
        )

        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id


class TestUpdateTransaction:
    """Test updating transactions"""

    def test_update_transaction(self, transaction_service, test_user):
        """Test: Can update transaction fields"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            description="Original",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )

        updated = transaction_service.update_transaction(
            transaction_id=transaction.id,
            user_id=test_user.id,
            description="Updated",
            amount=2000,
        )

        assert updated.description == "Updated"
        assert updated.amount == 2000

    def test_update_nonexistent_transaction_raises_error(
        self, transaction_service, test_user
    ):
        """Test: Updating non-existent transaction raises NotFoundError"""
        with pytest.raises(NotFoundError):
            transaction_service.update_transaction(
                transaction_id=99999,
                user_id=test_user.id,
                description="Updated",
            )

    def test_update_other_user_transaction_raises_error(
        self, transaction_service, test_user, db_session
    ):
        """Test: Cannot update another user's transaction"""
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hash",
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            description="Test",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )

        with pytest.raises(NotFoundError):
            transaction_service.update_transaction(
                transaction_id=transaction.id,
                user_id=other_user.id,
                description="Updated",
            )


class TestDeleteTransaction:
    """Test deleting transactions"""

    def test_delete_transaction(self, transaction_service, test_user):
        """Test: Can delete transaction"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            description="Test",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )

        result = transaction_service.delete_transaction(transaction.id, test_user.id)

        assert result is True
        
        # Verify it's deleted
        deleted = transaction_service.get_transaction(transaction.id, test_user.id)
        assert deleted is None

    def test_delete_nonexistent_transaction_raises_error(
        self, transaction_service, test_user
    ):
        """Test: Deleting non-existent transaction raises NotFoundError"""
        with pytest.raises(NotFoundError):
            transaction_service.delete_transaction(99999, test_user.id)


class TestTransactionStats:
    """Test transaction statistics"""

    def test_get_transaction_summary(self, transaction_service, test_user):
        """Test: Can get transaction summary stats"""
        # Create mix of expenses and income
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Expense 1",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Expense 2",
            amount=2000,
            transaction_type="expense",
            transaction_date=date.today(),
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            description="Income",
            amount=5000,
            transaction_type="income",
            transaction_date=date.today(),
        )

        summary = transaction_service.get_summary(test_user.id)

        assert summary["total_expenses"] == 3000
        assert summary["total_income"] == 5000
        assert summary["net"] == 2000  # 5000 - 3000
        assert summary["transaction_count"] == 3
