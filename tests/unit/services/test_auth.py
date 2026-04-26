"""
Unit tests for authentication service
Following TDD: Write tests first, then implement
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.services.auth_service import AuthService
from src.models.user import User
from src.utils.exceptions import (
    InvalidCredentialsError,
    AlreadyExistsError,
    ValidationError,
    InvalidTokenError,
    TokenExpiredError,
)
from tests.fixtures.user_fixtures import (
    valid_user_data,
    valid_user_data_2,
    invalid_user_data,
    user_login_data,
    invalid_login_data,
)


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
def auth_service(db_session):
    """Create AuthService instance"""
    return AuthService(db_session)


class TestUserRegistration:
    """Test user registration functionality"""

    def test_register_user_creates_new_user(self, auth_service, valid_user_data):
        """Test: Registration creates a new user with hashed password"""
        # Arrange: valid user data (from fixture)
        
        # Act: Register user
        user = auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Assert: User created successfully
        assert user is not None
        assert user.id is not None
        assert user.username == valid_user_data["username"]
        assert user.email == valid_user_data["email"]
        assert user.hashed_password != valid_user_data["password"]  # Password should be hashed
        assert user.is_active is True
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_register_user_hashes_password(self, auth_service, valid_user_data):
        """Test: Password is properly hashed, not stored in plaintext"""
        # Act
        user = auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Assert
        assert user.hashed_password != valid_user_data["password"]
        assert len(user.hashed_password) > 50  # Bcrypt hashes are long
        assert user.hashed_password.startswith("$2b$")  # Bcrypt prefix

    def test_register_duplicate_username_raises_error(self, auth_service, valid_user_data):
        """Test: Cannot register duplicate username"""
        # Arrange: Create first user
        auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Act & Assert: Try to register with same username
        with pytest.raises(AlreadyExistsError) as exc_info:
            auth_service.register_user(
                username=valid_user_data["username"],
                email="different@example.com",
                password="DifferentPass123!",
            )
        
        assert "username" in str(exc_info.value).lower()

    def test_register_duplicate_email_raises_error(self, auth_service, valid_user_data):
        """Test: Cannot register duplicate email"""
        # Arrange: Create first user
        auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Act & Assert: Try to register with same email
        with pytest.raises(AlreadyExistsError) as exc_info:
            auth_service.register_user(
                username="differentuser",
                email=valid_user_data["email"],
                password="DifferentPass123!",
            )
        
        assert "email" in str(exc_info.value).lower()

    def test_register_empty_username_raises_error(self, auth_service):
        """Test: Empty username raises validation error"""
        with pytest.raises(ValidationError):
            auth_service.register_user(
                username="",
                email="test@example.com",
                password="SecurePass123!",
            )

    def test_register_invalid_email_raises_error(self, auth_service):
        """Test: Invalid email format raises validation error"""
        with pytest.raises(ValidationError):
            auth_service.register_user(
                username="testuser",
                email="not-an-email",
                password="SecurePass123!",
            )

    def test_register_short_password_raises_error(self, auth_service):
        """Test: Password too short raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            auth_service.register_user(
                username="testuser",
                email="test@example.com",
                password="123",
            )
        
        assert "password" in str(exc_info.value).lower()


class TestUserLogin:
    """Test user login functionality"""

    def test_login_with_valid_credentials_returns_token(self, auth_service, valid_user_data):
        """Test: Login with correct credentials returns JWT token"""
        # Arrange: Register user first
        auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Act: Login
        token = auth_service.login(
            username=valid_user_data["username"],
            password=valid_user_data["password"],
        )
        
        # Assert: Token returned
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # JWT tokens are long
        assert "." in token  # JWT format has dots

    def test_login_with_wrong_password_raises_error(self, auth_service, valid_user_data):
        """Test: Login with wrong password fails"""
        # Arrange: Register user
        auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Act & Assert: Try to login with wrong password
        with pytest.raises(InvalidCredentialsError):
            auth_service.login(
                username=valid_user_data["username"],
                password="WrongPassword123!",
            )

    def test_login_with_nonexistent_user_raises_error(self, auth_service):
        """Test: Login with non-existent username fails"""
        with pytest.raises(InvalidCredentialsError):
            auth_service.login(
                username="nonexistent",
                password="AnyPassword123!",
            )

    def test_login_inactive_user_raises_error(self, auth_service, valid_user_data, db_session):
        """Test: Inactive users cannot login"""
        # Arrange: Register and deactivate user
        user = auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        user.is_active = False
        db_session.commit()
        
        # Act & Assert: Try to login
        with pytest.raises(InvalidCredentialsError) as exc_info:
            auth_service.login(
                username=valid_user_data["username"],
                password=valid_user_data["password"],
            )
        
        assert "inactive" in str(exc_info.value).lower() or "disabled" in str(exc_info.value).lower()


class TestTokenVerification:
    """Test JWT token verification"""

    def test_verify_valid_token_returns_user_id(self, auth_service, valid_user_data):
        """Test: Valid token verification returns user ID"""
        # Arrange: Register and login
        user = auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        token = auth_service.login(
            username=valid_user_data["username"],
            password=valid_user_data["password"],
        )
        
        # Act: Verify token
        user_id = auth_service.verify_token(token)
        
        # Assert: Returns correct user ID
        assert user_id is not None
        assert user_id == user.id

    def test_verify_invalid_token_raises_error(self, auth_service):
        """Test: Invalid token raises error"""
        with pytest.raises(InvalidTokenError):
            auth_service.verify_token("invalid.token.here")

    def test_verify_malformed_token_raises_error(self, auth_service):
        """Test: Malformed token raises error"""
        with pytest.raises(InvalidTokenError):
            auth_service.verify_token("not-a-jwt")

    def test_verify_token_wrong_signature_raises_error(self, auth_service, valid_user_data):
        """Test: Token with wrong signature fails"""
        # Arrange: Register and create token
        auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        token = auth_service.login(
            username=valid_user_data["username"],
            password=valid_user_data["password"],
        )
        
        # Act: Tamper with token
        tampered_token = token[:-5] + "xxxxx"
        
        # Assert: Verification fails
        with pytest.raises(InvalidTokenError):
            auth_service.verify_token(tampered_token)


class TestGetUserById:
    """Test get user by ID functionality"""

    def test_get_existing_user_returns_user(self, auth_service, valid_user_data):
        """Test: Can retrieve user by ID"""
        # Arrange: Create user
        created_user = auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Act: Get user
        user = auth_service.get_user_by_id(created_user.id)
        
        # Assert: User found
        assert user is not None
        assert user.id == created_user.id
        assert user.username == valid_user_data["username"]
        assert user.email == valid_user_data["email"]

    def test_get_nonexistent_user_returns_none(self, auth_service):
        """Test: Non-existent user ID returns None"""
        user = auth_service.get_user_by_id(99999)
        assert user is None


class TestPasswordVerification:
    """Test password verification utility"""

    def test_verify_correct_password_returns_true(self, auth_service, valid_user_data):
        """Test: Correct password verification"""
        # Arrange: Create user
        user = auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Act & Assert: Verify password
        assert auth_service.verify_password(valid_user_data["password"], user.hashed_password)

    def test_verify_wrong_password_returns_false(self, auth_service, valid_user_data):
        """Test: Wrong password verification fails"""
        # Arrange: Create user
        user = auth_service.register_user(
            username=valid_user_data["username"],
            email=valid_user_data["email"],
            password=valid_user_data["password"],
        )
        
        # Act & Assert: Verify wrong password
        assert not auth_service.verify_password("WrongPassword", user.hashed_password)
