"""
Source API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.services.auth_service import AuthService
from src.services.source_service import SourceService
from src.api.schemas import (
    SourceCreateRequest,
    SourceUpdateRequest,
    SourceResponse,
)
from src.utils.exceptions import (
    ValidationError,
    NotFoundError,
    InvalidTokenError,
)

router = APIRouter()
bearer_scheme = HTTPBearer()


def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """Extract JWT token from Authorization header"""
    return credentials.credentials


def get_current_user_id(
    token: str = Depends(get_auth_token),
    db: Session = Depends(get_db)
) -> int:
    """Get current user ID from JWT token"""
    auth_service = AuthService(db)
    user_id = auth_service.verify_token(token)
    if not user_id:
        raise InvalidTokenError("Invalid or expired token")
    return user_id


@router.post(
    "",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new source",
)
def create_source(
    source_data: SourceCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new payment source
    
    - **name**: Source name (required, unique per user)
    - **source_type**: Type (bank_account/credit_card/cash/digital_wallet/other)
    - **description**: Optional description
    - **account_number_last4**: Last 4 digits of account (optional)
    - **institution_name**: Bank/institution name (optional)
    - **current_balance**: Balance in cents (optional)
    - **color**: Hex color for UI (optional, e.g. #FF5733)
    - **icon**: Icon name for UI (optional)
    """
    service = SourceService(db)
    source = service.create_source(
        user_id=user_id,
        name=source_data.name,
        source_type=source_data.source_type,
        description=source_data.description,
        account_number_last4=source_data.account_number_last4,
        institution_name=source_data.institution_name,
        current_balance=source_data.current_balance,
        color=source_data.color,
        icon=source_data.icon,
    )
    return source


@router.get(
    "",
    response_model=list[SourceResponse],
    summary="List sources",
)
def list_sources(
    source_type: Optional[str] = Query(None, pattern="^(bank_account|credit_card|cash|digital_wallet|other)$"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    List all sources for the current user
    
    Optionally filter by type and active status.
    Results are ordered by name alphabetically.
    """
    service = SourceService(db)
    sources = service.list_sources(
        user_id=user_id,
        source_type=source_type,
        is_active=is_active,
    )
    return sources


@router.get(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Get a specific source",
)
def get_source(
    source_id: int = Path(..., description="Source ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific source by ID"""
    service = SourceService(db)
    source = service.get_source(source_id, user_id)
    if not source:
        raise NotFoundError(f"Source with ID {source_id} not found")
    return source


@router.put(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Update a source",
)
def update_source(
    source_data: SourceUpdateRequest,
    source_id: int = Path(..., description="Source ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update a source
    
    All fields are optional. Only provided fields will be updated.
    """
    service = SourceService(db)
    
    # Build kwargs from non-None values
    update_data = {}
    if source_data.name is not None:
        update_data["name"] = source_data.name
    if source_data.source_type is not None:
        update_data["source_type"] = source_data.source_type
    if source_data.description is not None:
        update_data["description"] = source_data.description
    if source_data.account_number_last4 is not None:
        update_data["account_number_last4"] = source_data.account_number_last4
    if source_data.institution_name is not None:
        update_data["institution_name"] = source_data.institution_name
    if source_data.current_balance is not None:
        update_data["current_balance"] = source_data.current_balance
    if source_data.color is not None:
        update_data["color"] = source_data.color
    if source_data.icon is not None:
        update_data["icon"] = source_data.icon
    if source_data.is_active is not None:
        update_data["is_active"] = source_data.is_active
    
    source = service.update_source(
        source_id=source_id,
        user_id=user_id,
        **update_data
    )
    return source


@router.delete(
    "/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a source",
)
def delete_source(
    source_id: int = Path(..., description="Source ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Delete a source
    
    Note: This will set associated transactions' source_id to NULL,
    preserving the transaction records.
    """
    service = SourceService(db)
    service.delete_source(source_id, user_id)
    return None
