"""
Authentication Service
Handles user registration, login, and JWT token management
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from src.models.user import User
from src.config.settings import settings
from src.utils.exceptions import (
    InvalidCredentialsError,
    AlreadyExistsError,
    ValidationError,
    InvalidTokenError,
    TokenExpiredError,
)


# Password hashing context
pwd_context = CryptContext(
    schemes=settings.PASSWORD_HASH_SCHEMES,
    deprecated=settings.PASSWORD_HASH_DEPRECATED,
)


class AuthService:
    """
    Authentication service for user management
    Follows CONVENTIONS.md patterns for error handling and validation
    """

    def __init__(self, db: Session):
        self.db = db

    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user
        
        Args:
            username: Unique username (3-50 chars)
            email: Valid email address
            password: Password (minimum 8 chars)
            
        Returns:
            Created User object
            
        Raises:
            ValidationError: If input validation fails
            AlreadyExistsError: If username or email already exists
        """
        # Validate inputs
        self._validate_username(username)
        self._validate_email(email)
        self._validate_password(password)

        # Check for duplicates
        if self._get_user_by_username(username):
            raise AlreadyExistsError(f"Username '{username}' already exists")

        if self._get_user_by_email(email):
            raise AlreadyExistsError(f"Email '{email}' already exists")

        # Hash password
        hashed_password = self._hash_password(password)

        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login(self, username: str, password: str) -> str:
        """
        Authenticate user and generate JWT token
        
        Args:
            username: Username
            password: Password
            
        Returns:
            JWT token string
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        # Get user
        user = self._get_user_by_username(username)
        if not user:
            raise InvalidCredentialsError("Invalid username or password")

        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsError("Account is inactive")

        # Verify password
        if not self.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid username or password")

        # Generate JWT token
        token = self._generate_token(user.id)
        return token

    def verify_token(self, token: str) -> int:
        """
        Verify JWT token and extract user ID
        
        Args:
            token: JWT token string
            
        Returns:
            User ID from token
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            user_id_str: str = payload.get("sub")
            if user_id_str is None:
                raise InvalidTokenError("Invalid token payload")
            # Convert string back to int
            user_id = int(user_id_str)
            return user_id
        except JWTError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    # Private helper methods

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    def _generate_token(self, user_id: int) -> str:
        """Generate JWT token for user"""
        expires = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)
        payload = {
            "sub": str(user_id),  # JWT "sub" must be a string
            "exp": expires,
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return token

    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def _validate_username(self, username: str):
        """
        Validate username
        Rules: 3-50 characters, alphanumeric + underscore
        """
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")

        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters")

        if len(username) > 50:
            raise ValidationError("Username cannot exceed 50 characters")

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )

    def _validate_email(self, email: str):
        """
        Validate email format
        Basic regex pattern for email validation
        """
        if not email or not email.strip():
            raise ValidationError("Email cannot be empty")

        # Basic email regex pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")

        if len(email) > 255:
            raise ValidationError("Email cannot exceed 255 characters")

    def _validate_password(self, password: str):
        """
        Validate password strength
        Rules: Minimum 8 characters
        """
        if not password:
            raise ValidationError("Password cannot be empty")

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        if len(password) > 128:
            raise ValidationError("Password cannot exceed 128 characters")
