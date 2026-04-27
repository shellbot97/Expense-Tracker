"""
Unit tests for SourceService
"""

import pytest
from src.services.source_service import SourceService
from src.services.auth_service import AuthService
from src.models.source import Source
from src.models.user import User
from src.models.category import Category
from src.models.transaction import Transaction
from src.models.budget import Budget  # Import all models to resolve SQLAlchemy relationships
from src.utils.exceptions import ValidationError, NotFoundError, AlreadyExistsError


# ============= Fixtures =============

@pytest.fixture
def db_session(tmp_path):
    """Create a temporary database for testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.config.database import Base

    # Create temporary SQLite database
    db_path = tmp_path / "test.db"
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
    auth_service = AuthService(db_session)
    user = auth_service.register_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    return user


@pytest.fixture
def source_service(db_session):
    """Create a SourceService instance"""
    return SourceService(db_session)


@pytest.fixture
def test_source_data():
    """Valid source data"""
    return {
        "name": "Chase Checking",
        "source_type": "bank_account",
        "description": "Primary checking account",
        "account_number_last4": "1234",
        "institution_name": "Chase Bank",
        "current_balance": 150000,  # $1500.00
        "color": "#0066FF",
        "icon": "bank",
    }


# ============= Create Source Tests =============

@pytest.mark.unit
class TestCreateSource:
    """Tests for creating sources"""

    def test_create_basic_source(self, source_service, test_user):
        """Test creating a basic source"""
        source = source_service.create_source(
            user_id=test_user.id,
            name="Cash Wallet",
            source_type="cash",
        )

        assert source.id is not None
        assert source.user_id == test_user.id
        assert source.name == "Cash Wallet"
        assert source.source_type == "cash"
        assert source.is_active is True

    def test_create_source_with_all_fields(self, source_service, test_user, test_source_data):
        """Test creating a source with all fields"""
        source = source_service.create_source(
            user_id=test_user.id,
            **test_source_data
        )

        assert source.name == test_source_data["name"]
        assert source.source_type == test_source_data["source_type"]
        assert source.description == test_source_data["description"]
        assert source.account_number_last4 == test_source_data["account_number_last4"]
        assert source.institution_name == test_source_data["institution_name"]
        assert source.current_balance == test_source_data["current_balance"]
        assert source.color == test_source_data["color"]
        assert source.icon == test_source_data["icon"]

    def test_create_source_empty_name_raises_error(self, source_service, test_user):
        """Test that empty name raises ValidationError"""
        with pytest.raises(ValidationError, match="Name cannot be empty"):
            source_service.create_source(
                user_id=test_user.id,
                name="",
                source_type="cash",
            )

    def test_create_source_invalid_type_raises_error(self, source_service, test_user):
        """Test that invalid source_type raises ValidationError"""
        with pytest.raises(ValidationError, match="Invalid source_type"):
            source_service.create_source(
                user_id=test_user.id,
                name="Test Source",
                source_type="invalid_type",
            )

    def test_create_source_invalid_last4_raises_error(self, source_service, test_user):
        """Test that invalid last4 raises ValidationError"""
        with pytest.raises(ValidationError, match="must be exactly 4 characters"):
            source_service.create_source(
                user_id=test_user.id,
                name="Test Source",
                source_type="bank_account",
                account_number_last4="123",  # Too short
            )

    def test_create_source_duplicate_name_raises_error(self, source_service, test_user):
        """Test that duplicate name raises AlreadyExistsError"""
        source_service.create_source(
            user_id=test_user.id,
            name="My Wallet",
            source_type="cash",
        )

        with pytest.raises(AlreadyExistsError, match="already exists"):
            source_service.create_source(
                user_id=test_user.id,
                name="My Wallet",
                source_type="bank_account",
            )


# ============= Get Source Tests =============

@pytest.mark.unit
class TestGetSource:
    """Tests for getting sources"""

    def test_get_source_by_id(self, source_service, test_user):
        """Test getting a source by ID"""
        created = source_service.create_source(
            user_id=test_user.id,
            name="Test Source",
            source_type="cash",
        )

        source = source_service.get_source(created.id, test_user.id)

        assert source is not None
        assert source.id == created.id
        assert source.name == "Test Source"

    def test_get_nonexistent_source_returns_none(self, source_service, test_user):
        """Test that getting nonexistent source returns None"""
        source = source_service.get_source(99999, test_user.id)
        assert source is None

    def test_get_source_wrong_user_returns_none(self, source_service, test_user, db_session):
        """Test that getting source for wrong user returns None"""
        from src.models.user import User
        from src.services.auth_service import AuthService
        
        # Create another user
        auth_service = AuthService(db_session)
        other_user = auth_service.register_user("otheruser", "other@example.com", "password123")

        # Create source for first user
        source = source_service.create_source(
            user_id=test_user.id,
            name="My Source",
            source_type="cash",
        )

        # Try to get as other user
        result = source_service.get_source(source.id, other_user.id)
        assert result is None


# ============= List Sources Tests =============

@pytest.mark.unit
class TestListSources:
    """Tests for listing sources"""

    def test_list_user_sources(self, source_service, test_user):
        """Test listing all sources for user"""
        source_service.create_source(test_user.id, "Source 1", "cash")
        source_service.create_source(test_user.id, "Source 2", "bank_account")
        source_service.create_source(test_user.id, "Source 3", "credit_card")

        sources = source_service.list_sources(test_user.id)

        assert len(sources) == 3

    def test_list_sources_by_type(self, source_service, test_user):
        """Test filtering sources by type"""
        source_service.create_source(test_user.id, "Cash 1", "cash")
        source_service.create_source(test_user.id, "Bank 1", "bank_account")
        source_service.create_source(test_user.id, "Cash 2", "cash")

        sources = source_service.list_sources(test_user.id, source_type="cash")

        assert len(sources) == 2
        assert all(s.source_type == "cash" for s in sources)

    def test_list_sources_by_active_status(self, source_service, test_user):
        """Test filtering sources by active status"""
        s1 = source_service.create_source(test_user.id, "Active", "cash")
        s2 = source_service.create_source(test_user.id, "Inactive", "cash")
        
        # Deactivate one
        source_service.update_source(s2.id, test_user.id, is_active=False)

        active_sources = source_service.list_sources(test_user.id, is_active=True)
        inactive_sources = source_service.list_sources(test_user.id, is_active=False)

        assert len(active_sources) == 1
        assert len(inactive_sources) == 1

    def test_list_sources_sorted_by_name(self, source_service, test_user):
        """Test that sources are sorted alphabetically by name"""
        source_service.create_source(test_user.id, "Zebra", "cash")
        source_service.create_source(test_user.id, "Alpha", "cash")
        source_service.create_source(test_user.id, "Beta", "cash")

        sources = source_service.list_sources(test_user.id)

        assert sources[0].name == "Alpha"
        assert sources[1].name == "Beta"
        assert sources[2].name == "Zebra"


# ============= Update Source Tests =============

@pytest.mark.unit
class TestUpdateSource:
    """Tests for updating sources"""

    def test_update_source_name(self, source_service, test_user):
        """Test updating source name"""
        source = source_service.create_source(
            test_user.id, "Old Name", "cash"
        )

        updated = source_service.update_source(
            source.id, test_user.id, name="New Name"
        )

        assert updated.name == "New Name"

    def test_update_source_balance(self, source_service, test_user):
        """Test updating source balance"""
        source = source_service.create_source(
            test_user.id, "Bank", "bank_account", current_balance=100000
        )

        updated = source_service.update_source(
            source.id, test_user.id, current_balance=200000
        )

        assert updated.current_balance == 200000

    def test_update_nonexistent_source_raises_error(self, source_service, test_user):
        """Test that updating nonexistent source raises NotFoundError"""
        with pytest.raises(NotFoundError):
            source_service.update_source(99999, test_user.id, name="Test")

    def test_update_source_duplicate_name_raises_error(self, source_service, test_user):
        """Test that updating to duplicate name raises AlreadyExistsError"""
        s1 = source_service.create_source(test_user.id, "Source 1", "cash")
        s2 = source_service.create_source(test_user.id, "Source 2", "cash")

        with pytest.raises(AlreadyExistsError, match="already exists"):
            source_service.update_source(s2.id, test_user.id, name="Source 1")


# ============= Delete Source Tests =============

@pytest.mark.unit
class TestDeleteSource:
    """Tests for deleting sources"""

    def test_delete_source(self, source_service, test_user):
        """Test deleting a source"""
        source = source_service.create_source(test_user.id, "Test", "cash")

        result = source_service.delete_source(source.id, test_user.id)

        assert result is True
        # Verify it's gone
        assert source_service.get_source(source.id, test_user.id) is None

    def test_delete_nonexistent_source_raises_error(self, source_service, test_user):
        """Test that deleting nonexistent source raises NotFoundError"""
        with pytest.raises(NotFoundError):
            source_service.delete_source(99999, test_user.id)


# ============= Validation Tests =============

@pytest.mark.unit
class TestSourceValidation:
    """Tests for source validation"""

    def test_valid_source_types(self, source_service, test_user):
        """Test all valid source types"""
        valid_types = ["bank_account", "credit_card", "cash", "digital_wallet", "other"]

        for source_type in valid_types:
            source = source_service.create_source(
                test_user.id,
                f"Test {source_type}",
                source_type,
            )
            assert source.source_type == source_type

    def test_name_max_length(self, source_service, test_user):
        """Test that name cannot exceed 100 characters"""
        with pytest.raises(ValidationError, match="cannot exceed 100 characters"):
            source_service.create_source(
                test_user.id,
                "A" * 101,
                "cash",
            )

    def test_last4_must_be_digits(self, source_service, test_user):
        """Test that last4 must contain only digits"""
        with pytest.raises(ValidationError, match="must contain only digits"):
            source_service.create_source(
                test_user.id,
                "Test",
                "bank_account",
                account_number_last4="ABCD",
            )
