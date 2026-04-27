"""
Unit tests for data models
Testing Category, Source, Transaction, and Budget models
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
from src.models.budget import Budget


@pytest.fixture
def db_session(tmp_path):
    """Create a temporary database for testing"""
    # Create temporary SQLite database
    db_path = tmp_path / "test_models.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestCategoryModel:
    """Test Category model"""

    def test_create_category(self, db_session, test_user):
        """Test: Can create a category"""
        category = Category(
            user_id=test_user.id,
            name="Groceries",
            description="Food and household items",
            category_type="expense",
            color="#FF5733",
            icon="shopping-cart",
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.id is not None
        assert category.name == "Groceries"
        assert category.user_id == test_user.id
        assert category.category_type == "expense"
        assert category.is_active is True
        assert category.is_system is False

    def test_category_hierarchy(self, db_session, test_user):
        """Test: Categories can have parent-child relationships"""
        # Create parent category
        parent = Category(
            user_id=test_user.id,
            name="Food",
            category_type="expense",
        )
        db_session.add(parent)
        db_session.commit()
        db_session.refresh(parent)

        # Create child category
        child = Category(
            user_id=test_user.id,
            name="Restaurants",
            category_type="expense",
            parent_id=parent.id,
        )
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)

        assert child.parent_id == parent.id
        assert child.parent.id == parent.id
        assert len(parent.subcategories) == 1
        assert parent.subcategories[0].id == child.id

    def test_category_to_dict(self, db_session, test_user):
        """Test: Category converts to dictionary correctly"""
        category = Category(
            user_id=test_user.id,
            name="Transportation",
            category_type="expense",
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        result = category.to_dict()
        assert result["id"] == category.id
        assert result["name"] == "Transportation"
        assert result["category_type"] == "expense"
        assert "created_at" in result


class TestSourceModel:
    """Test Source model"""

    def test_create_source(self, db_session, test_user):
        """Test: Can create a payment source"""
        source = Source(
            user_id=test_user.id,
            name="Chase Checking",
            description="Primary checking account",
            source_type="bank_account",
            account_number_last4="1234",
            institution_name="Chase Bank",
            current_balance=50000,  # $500.00 in cents
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)

        assert source.id is not None
        assert source.name == "Chase Checking"
        assert source.source_type == "bank_account"
        assert source.current_balance == 50000
        assert source.is_active is True

    def test_source_without_balance(self, db_session, test_user):
        """Test: Source can exist without balance tracking"""
        source = Source(
            user_id=test_user.id,
            name="Cash",
            source_type="cash",
            current_balance=None,  # Not tracked
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)

        assert source.id is not None
        assert source.current_balance is None

    def test_source_to_dict(self, db_session, test_user):
        """Test: Source converts to dictionary correctly"""
        source = Source(
            user_id=test_user.id,
            name="Visa Credit Card",
            source_type="credit_card",
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)

        result = source.to_dict()
        assert result["id"] == source.id
        assert result["name"] == "Visa Credit Card"
        assert result["source_type"] == "credit_card"


class TestTransactionModel:
    """Test Transaction model"""

    def test_create_transaction(self, db_session, test_user):
        """Test: Can create a transaction"""
        # Create category and source first
        category = Category(user_id=test_user.id, name="Food", category_type="expense")
        source = Source(user_id=test_user.id, name="Checking", source_type="bank_account")
        db_session.add_all([category, source])
        db_session.commit()

        transaction = Transaction(
            user_id=test_user.id,
            category_id=category.id,
            source_id=source.id,
            description="Grocery shopping at Whole Foods",
            amount=8543,  # $85.43 in cents
            transaction_type="expense",
            transaction_date=date.today(),
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.id is not None
        assert transaction.description == "Grocery shopping at Whole Foods"
        assert transaction.amount == 8543
        assert transaction.transaction_type == "expense"
        assert transaction.is_reconciled is False

    def test_transaction_relationships(self, db_session, test_user):
        """Test: Transaction relationships work correctly"""
        category = Category(user_id=test_user.id, name="Travel", category_type="expense")
        source = Source(user_id=test_user.id, name="Credit Card", source_type="credit_card")
        db_session.add_all([category, source])
        db_session.commit()

        transaction = Transaction(
            user_id=test_user.id,
            category_id=category.id,
            source_id=source.id,
            description="Flight ticket",
            amount=35000,
            transaction_type="expense",
            transaction_date=date.today(),
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        assert transaction.category.name == "Travel"
        assert transaction.source.name == "Credit Card"
        assert transaction.user.username == "testuser"

    def test_transaction_amount_conversion(self, db_session, test_user):
        """Test: Amount conversion between cents and dollars"""
        transaction = Transaction(
            user_id=test_user.id,
            description="Test transaction",
            amount=12050,  # $120.50
            transaction_type="expense",
            transaction_date=date.today(),
        )
        db_session.add(transaction)
        db_session.commit()

        # Test cents to dollars
        assert transaction.get_amount_dollars() == 120.50

        # Test dollars to cents
        assert Transaction.dollars_to_cents(120.50) == 12050
        assert Transaction.dollars_to_cents(99.99) == 9999

    def test_transaction_to_dict(self, db_session, test_user):
        """Test: Transaction converts to dictionary correctly"""
        transaction = Transaction(
            user_id=test_user.id,
            description="Test",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)

        result = transaction.to_dict()
        assert result["id"] == transaction.id
        assert result["amount"] == 1000
        assert result["transaction_type"] == "expense"
        assert result["is_reconciled"] is False


class TestBudgetModel:
    """Test Budget model"""

    def test_create_budget(self, db_session, test_user):
        """Test: Can create a budget"""
        category = Category(user_id=test_user.id, name="Dining Out", category_type="expense")
        db_session.add(category)
        db_session.commit()

        budget = Budget(
            user_id=test_user.id,
            category_id=category.id,
            name="Monthly Dining Budget",
            amount_limit=30000,  # $300.00
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 30),
            period_type="monthly",
        )
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)

        assert budget.id is not None
        assert budget.name == "Monthly Dining Budget"
        assert budget.amount_limit == 30000
        assert budget.period_type == "monthly"
        assert budget.allow_rollover is False

    def test_budget_alert_thresholds(self, db_session, test_user):
        """Test: Budget alert thresholds default to True"""
        budget = Budget(
            user_id=test_user.id,
            name="Test Budget",
            amount_limit=10000,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)

        assert budget.alert_threshold_50 is True
        assert budget.alert_threshold_75 is True
        assert budget.alert_threshold_90 is True
        assert budget.alert_threshold_100 is True

    def test_budget_amount_conversion(self, db_session, test_user):
        """Test: Budget amount conversion"""
        budget = Budget(
            user_id=test_user.id,
            name="Test",
            amount_limit=50000,  # $500.00
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        db_session.add(budget)
        db_session.commit()

        assert budget.get_limit_dollars() == 500.00
        assert Budget.dollars_to_cents(500.00) == 50000

    def test_budget_to_dict(self, db_session, test_user):
        """Test: Budget converts to dictionary correctly"""
        budget = Budget(
            user_id=test_user.id,
            name="Test Budget",
            amount_limit=10000,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)

        result = budget.to_dict()
        assert result["id"] == budget.id
        assert result["name"] == "Test Budget"
        assert result["amount_limit"] == 10000
        assert "start_date" in result


class TestModelCascades:
    """Test cascade delete behavior"""

    def test_deleting_user_deletes_categories(self, db_session, test_user):
        """Test: Deleting user cascades to categories"""
        category = Category(user_id=test_user.id, name="Test", category_type="expense")
        db_session.add(category)
        db_session.commit()

        category_id = category.id
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()

        # Category should be deleted
        result = db_session.query(Category).filter(Category.id == category_id).first()
        assert result is None

    def test_deleting_category_nullifies_transactions(self, db_session, test_user):
        """Test: Deleting category sets transaction category_id to NULL"""
        category = Category(user_id=test_user.id, name="Food", category_type="expense")
        db_session.add(category)
        db_session.commit()

        transaction = Transaction(
            user_id=test_user.id,
            category_id=category.id,
            description="Test",
            amount=1000,
            transaction_type="expense",
            transaction_date=date.today(),
        )
        db_session.add(transaction)
        db_session.commit()

        transaction_id = transaction.id
        
        # Delete category
        db_session.delete(category)
        db_session.commit()

        # Transaction should still exist but category_id should be None
        result = db_session.query(Transaction).filter(Transaction.id == transaction_id).first()
        assert result is not None
        assert result.category_id is None
