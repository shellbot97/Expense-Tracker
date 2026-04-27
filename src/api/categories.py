"""
Category API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.services.auth_service import AuthService
from src.services.category_service import CategoryService
from src.api.schemas import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
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
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
def create_category(
    category_data: CategoryCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new expense/income category
    
    - **name**: Category name (required, unique per user)
    - **category_type**: Type (expense/income)
    - **description**: Optional description
    - **parent_id**: Parent category ID for hierarchical categories
    - **matching_pattern**: Regex pattern for auto-categorization
    - **is_system**: Whether this is a system category (default: false)
    - **color**: Hex color for UI (optional, e.g. #FF5733)
    - **icon**: Icon name for UI (optional)
    """
    service = CategoryService(db)
    category = service.create_category(
        user_id=user_id,
        name=category_data.name,
        category_type=category_data.category_type,
        description=category_data.description,
        parent_id=category_data.parent_id,
        matching_pattern=category_data.matching_pattern,
        is_system=category_data.is_system,
        color=category_data.color,
        icon=category_data.icon,
    )
    return category


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="List categories",
)
def list_categories(
    category_type: Optional[str] = Query(None, pattern="^(expense|income)$"),
    parent_id: Optional[int] = Query(None, description="Filter by parent category ID"),
    is_system: Optional[bool] = Query(None, description="Filter by system status"),
    include_subcategories: bool = Query(True, description="Include all subcategories"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    List all categories for the current user
    
    Optionally filter by type, parent, and system status.
    Results are ordered alphabetically by name.
    
    Use parent_id=null and include_subcategories=false to get only root categories.
    """
    service = CategoryService(db)
    categories = service.list_categories(
        user_id=user_id,
        category_type=category_type,
        parent_id=parent_id,
        is_system=is_system,
        include_subcategories=include_subcategories,
    )
    return categories


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get a specific category",
)
def get_category(
    category_id: int = Path(..., description="Category ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific category by ID"""
    service = CategoryService(db)
    category = service.get_category(category_id, user_id)
    if not category:
        raise NotFoundError(f"Category with ID {category_id} not found")
    return category


@router.get(
    "/{category_id}/hierarchy",
    response_model=list[CategoryResponse],
    summary="Get category hierarchy",
)
def get_category_hierarchy(
    category_id: int = Path(..., description="Category ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get category and all its descendants
    
    Returns the category and all subcategories in a flat list.
    """
    service = CategoryService(db)
    hierarchy = service.get_category_hierarchy(category_id, user_id)
    return hierarchy


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category",
)
def update_category(
    category_data: CategoryUpdateRequest,
    category_id: int = Path(..., description="Category ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update a category
    
    All fields are optional. Only provided fields will be updated.
    System categories cannot be modified.
    """
    service = CategoryService(db)
    
    # Build kwargs from non-None values
    update_data = {}
    if category_data.name is not None:
        update_data["name"] = category_data.name
    if category_data.category_type is not None:
        update_data["category_type"] = category_data.category_type
    if category_data.description is not None:
        update_data["description"] = category_data.description
    if category_data.parent_id is not None:
        update_data["parent_id"] = category_data.parent_id
    if category_data.matching_pattern is not None:
        update_data["matching_pattern"] = category_data.matching_pattern
    if category_data.color is not None:
        update_data["color"] = category_data.color
    if category_data.icon is not None:
        update_data["icon"] = category_data.icon
    
    category = service.update_category(
        category_id=category_id,
        user_id=user_id,
        **update_data
    )
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
)
def delete_category(
    category_id: int = Path(..., description="Category ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Delete a category
    
    System categories cannot be deleted.
    Categories with subcategories cannot be deleted (delete children first).
    Associated transactions will have their category_id set to NULL.
    """
    service = CategoryService(db)
    service.delete_category(category_id, user_id)
    return None
