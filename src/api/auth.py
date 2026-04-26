"""
Authentication API endpoints
Provides REST API for user registration and login
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.services.auth_service import AuthService
from src.api.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)

# Create router
router = APIRouter()

# Bearer token scheme for JWT authentication
bearer_scheme = HTTPBearer()


def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """
    Extract JWT token from Authorization header
    Expects: Authorization: Bearer <token>
    """
    return credentials.credentials


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with username, email, and password",
)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user
    
    - **username**: Unique username (3-50 chars, alphanumeric + underscore)
    - **email**: Valid email address
    - **password**: Password (minimum 8 characters)
    
    Returns the created user object (without password)
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and receive JWT access token",
)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login with username and password
    
    - **username**: Username
    - **password**: Password
    
    Returns JWT access token for subsequent authenticated requests
    """
    auth_service = AuthService(db)
    token = auth_service.login(
        username=login_data.username,
        password=login_data.password,
    )
    return TokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get currently authenticated user's information",
)
def get_current_user(
    token: str = Depends(get_auth_token),
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user
    
    Requires valid JWT token in Authorization header
    """
    auth_service = AuthService(db)
    user_id = auth_service.verify_token(token)
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        from src.utils.exceptions import NotFoundError
        raise NotFoundError("User not found")
    
    return user

