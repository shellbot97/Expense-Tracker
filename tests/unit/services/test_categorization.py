"""
Unit tests for CategorizationService
"""

import pytest
from datetime import date
from src.services.categorization_service import CategorizationService
from src.services.auth_service import AuthService
from src.services.category_service import CategoryService
from src.services.transaction_service import TransactionService
from src.models.category import Category
from src.models.transaction import Transaction
from src.models.user import User
from src.models.source import Source
from src.models.budget import Budget
from src.utils.exceptions import NotFoundError, ValidationError


# ============= Fixtures =============

@pytest.fixture
def db_session(tmp_path):
    """Create a temporary database for testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.config.database import Base

    db_path = tmp_path / "test.db"
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
    auth_service = AuthService(db_session)
    return auth_service.register_user("testuser", "test@example.com", "password123")


@pytest.fixture
def categorization_service(db_session):
    """Create CategorizationService instance"""
    return CategorizationService(db_session)


@pytest.fixture
def category_service(db_session):
    """Create CategoryService instance"""
    return CategoryService(db_session)


@pytest.fixture
def transaction_service(db_session):
    """Create TransactionService instance"""
    return TransactionService(db_session)


@pytest.fixture
def test_categories(category_service, test_user):
    """Create test categories with matching patterns"""
    groceries = category_service.create_category(
        test_user.id,
        "Groceries",
        "expense",
        matching_pattern="(?i)(walmart|safeway|whole foods|grocery)",
    )
    
    gas = category_service.create_category(
        test_user.id,
        "Gas Stations",
        "expense",
        matching_pattern="(?i)(shell|chevron|mobil|bp|gas station)",
    )
    
    salary = category_service.create_category(
        test_user.id,
        "Salary",
        "income",
        matching_pattern="(?i)(payroll|salary|paycheck)",
    )
    
    return {"groceries": groceries, "gas": gas, "salary": salary}


# ============= Categorize Transaction Tests =============

@pytest.mark.unit
class TestCategorizeTransaction:
    """Tests for categorizing single transactions"""

    def test_categorize_transaction_with_match(
        self, categorization_service, transaction_service, test_user, test_categories
    ):
        """Test categorizing a transaction with matching pattern"""
        # Create transaction
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Purchase at Walmart Supercenter",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        # Categorize
        category_id, confidence = categorization_service.categorize_transaction(
            transaction.id, test_user.id
        )
        
        assert category_id == test_categories["groceries"].id
        assert confidence > 0.0
        assert confidence <= 1.0

    def test_categorize_transaction_no_match(
        self, categorization_service, transaction_service, test_user, test_categories
    ):
        """Test categorizing a transaction with no matching pattern"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Random purchase at unknown store",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        category_id, confidence = categorization_service.categorize_transaction(
            transaction.id, test_user.id
        )
        
        assert category_id is None
        assert confidence == 0.0

    def test_categorize_skips_manually_categorized(
        self, categorization_service, transaction_service, test_user, test_categories, category_service
    ):
        """Test that manually categorized transactions are skipped"""
        # Create another category
        other_cat = category_service.create_category(
            test_user.id, "Other", "expense"
        )
        
        # Create transaction with Walmart description
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Purchase at Walmart",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        # Manually categorize it
        categorization_service.manually_categorize(
            transaction.id, test_user.id, other_cat.id
        )
        
        # Try to auto-categorize (should skip)
        category_id, confidence = categorization_service.categorize_transaction(
            transaction.id, test_user.id, force=False
        )
        
        # Should keep manual category
        assert category_id == other_cat.id

    def test_categorize_force_overrides_manual(
        self, categorization_service, transaction_service, test_user, test_categories, category_service
    ):
        """Test that force=True re-categorizes manually categorized transactions"""
        other_cat = category_service.create_category(
            test_user.id, "Other", "expense"
        )
        
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Purchase at Walmart",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        # Manually categorize
        categorization_service.manually_categorize(
            transaction.id, test_user.id, other_cat.id
        )
        
        # Force re-categorize
        category_id, confidence = categorization_service.categorize_transaction(
            transaction.id, test_user.id, force=True
        )
        
        # Should match Groceries now
        assert category_id == test_categories["groceries"].id


# ============= Bulk Categorization Tests =============

@pytest.mark.unit
class TestBulkCategorization:
    """Tests for bulk categorization"""

    def test_bulk_categorize_all(
        self, categorization_service, transaction_service, test_user, test_categories
    ):
        """Test bulk categorization of all transactions"""
        # Create multiple transactions
        transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Walmart purchase",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            amount=4000,
            description="Shell gas station",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            amount=2000,
            description="Random store",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        # Bulk categorize
        stats = categorization_service.categorize_bulk(test_user.id)
        
        assert stats["processed"] == 3
        assert stats["categorized"] == 2  # Walmart and Shell
        assert stats["uncategorized"] == 1  # Random

    def test_bulk_categorize_with_limit(
        self, categorization_service, transaction_service, test_user, test_categories
    ):
        """Test bulk categorization with limit"""
        # Create 5 transactions
        for i in range(5):
            transaction_service.create_transaction(
                user_id=test_user.id,
                amount=5000,
                description="Walmart purchase",
                transaction_date=date.today(),
                transaction_type="expense",
            )
        
        # Categorize with limit
        stats = categorization_service.categorize_bulk(test_user.id, limit=3)
        
        assert stats["processed"] == 3
        assert stats["categorized"] == 3


# ============= Uncategorized Count Tests =============

@pytest.mark.unit
class TestUncategorizedCount:
    """Tests for uncategorized transaction counting"""

    def test_get_uncategorized_count(
        self, categorization_service, transaction_service, test_user
    ):
        """Test getting uncategorized transaction count"""
        # Create uncategorized transactions
        transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Transaction 1",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Transaction 2",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        count = categorization_service.get_uncategorized_count(test_user.id)
        
        assert count == 2

    def test_get_uncategorized_count_by_type(
        self, categorization_service, transaction_service, test_user
    ):
        """Test getting uncategorized count filtered by type"""
        transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Expense",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Income",
            transaction_date=date.today(),
            transaction_type="income",
        )
        
        expense_count = categorization_service.get_uncategorized_count(
            test_user.id, transaction_type="expense"
        )
        income_count = categorization_service.get_uncategorized_count(
            test_user.id, transaction_type="income"
        )
        
        assert expense_count == 1
        assert income_count == 1


# ============= Category Suggestions Tests =============

@pytest.mark.unit
class TestCategorySuggestions:
    """Tests for category suggestions"""

    def test_suggest_category(
        self, categorization_service, test_user, test_categories
    ):
        """Test getting category suggestions"""
        suggestions = categorization_service.suggest_category(
            description="Purchase at Walmart Supercenter",
            transaction_type="expense",
            user_id=test_user.id,
        )
        
        assert len(suggestions) > 0
        assert suggestions[0][0] == test_categories["groceries"].id
        assert suggestions[0][2] > 0.0  # confidence

    def test_suggest_category_multiple_matches(
        self, categorization_service, category_service, test_user
    ):
        """Test suggestions with multiple matching categories"""
        # Create categories with overlapping patterns
        category_service.create_category(
            test_user.id,
            "Food General",
            "expense",
            matching_pattern="(?i)(food)",
        )
        category_service.create_category(
            test_user.id,
            "Fast Food",
            "expense",
            matching_pattern="(?i)(mcdonalds|burger|food)",
        )
        
        suggestions = categorization_service.suggest_category(
            description="McDonalds food purchase",
            transaction_type="expense",
            user_id=test_user.id,
        )
        
        # Should have multiple suggestions
        assert len(suggestions) >= 2


# ============= Manual Categorization Tests =============

@pytest.mark.unit
class TestManualCategorization:
    """Tests for manual categorization"""

    def test_manually_categorize(
        self, categorization_service, transaction_service, test_user, test_categories
    ):
        """Test manually categorizing a transaction"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Test",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        updated = categorization_service.manually_categorize(
            transaction.id, test_user.id, test_categories["groceries"].id
        )
        
        assert updated.category_id == test_categories["groceries"].id
        assert updated.is_manually_categorized is True

    def test_manually_uncategorize(
        self, categorization_service, transaction_service, test_user, test_categories
    ):
        """Test manually uncategorizing a transaction"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Walmart",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        # First categorize
        categorization_service.manually_categorize(
            transaction.id, test_user.id, test_categories["groceries"].id
        )
        
        # Then uncategorize
        updated = categorization_service.manually_categorize(
            transaction.id, test_user.id, None
        )
        
        assert updated.category_id is None
        assert updated.is_manually_categorized is True

    def test_manually_categorize_type_mismatch_raises_error(
        self, categorization_service, transaction_service, test_user, test_categories
    ):
        """Test that type mismatch raises ValidationError"""
        transaction = transaction_service.create_transaction(
            user_id=test_user.id,
            amount=5000,
            description="Test",
            transaction_date=date.today(),
            transaction_type="expense",
        )
        
        with pytest.raises(ValidationError, match="does not match"):
            categorization_service.manually_categorize(
                transaction.id, test_user.id, test_categories["salary"].id
            )


# ============= Confidence Calculation Tests =============

@pytest.mark.unit
class TestConfidenceCalculation:
    """Tests for confidence score calculation"""

    def test_confidence_exact_match(self, categorization_service):
        """Test confidence for exact match"""
        confidence = categorization_service._calculate_match_confidence(
            description="Walmart",
            pattern="(?i)walmart",
        )
        
        assert confidence > 0.8  # High confidence for exact match

    def test_confidence_partial_match(self, categorization_service):
        """Test confidence for partial match"""
        confidence = categorization_service._calculate_match_confidence(
            description="Bought groceries at Walmart Supercenter",
            pattern="(?i)walmart",
        )
        
        assert confidence > 0.0
        assert confidence < 1.0

    def test_confidence_no_match(self, categorization_service):
        """Test confidence for no match"""
        confidence = categorization_service._calculate_match_confidence(
            description="Target store",
            pattern="(?i)walmart",
        )
        
        assert confidence == 0.0

    def test_confidence_invalid_regex(self, categorization_service):
        """Test that invalid regex returns 0 confidence"""
        confidence = categorization_service._calculate_match_confidence(
            description="Test",
            pattern="[invalid(",  # Invalid regex
        )
        
        assert confidence == 0.0
