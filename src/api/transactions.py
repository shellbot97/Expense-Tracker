"""
Transaction API endpoints
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.services.auth_service import AuthService
from src.services.transaction_service import TransactionService
from src.api.schemas import (
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionResponse,
    TransactionListResponse,
    TransactionSummaryResponse,
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
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
)
def create_transaction(
    transaction_data: TransactionCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new transaction
    
    - **description**: Transaction description (required)
    - **amount**: Amount in cents (required, must be positive)
    - **transaction_type**: Type of transaction (expense/income/transfer)
    - **transaction_date**: Date of transaction
    - **category_id**: Optional category ID
    - **source_id**: Optional source (account) ID
    - **notes**: Optional notes
    - **tags**: Optional comma-separated tags
    """
    service = TransactionService(db)
    transaction = service.create_transaction(
        user_id=user_id,
        description=transaction_data.description,
        amount=transaction_data.amount,
        transaction_type=transaction_data.transaction_type,
        transaction_date=transaction_data.transaction_date,
        category_id=transaction_data.category_id,
        source_id=transaction_data.source_id,
        notes=transaction_data.notes,
        tags=transaction_data.tags,
    )
    return transaction


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions with filters",
)
def list_transactions(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    transaction_type: Optional[str] = Query(None, pattern="^(expense|income|transfer)$"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    source_id: Optional[int] = Query(None, description="Filter by source ID"),
    min_amount: Optional[int] = Query(None, ge=0, description="Minimum amount in cents"),
    max_amount: Optional[int] = Query(None, ge=0, description="Maximum amount in cents"),
    limit: int = Query(100, ge=1, le=1000, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    List transactions with optional filters
    
    All filters are optional. Results are ordered by date descending (newest first).
    """
    service = TransactionService(db)
    transactions = service.list_transactions(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        category_id=category_id,
        source_id=source_id,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
        offset=offset,
    )
    
    return {
        "transactions": transactions,
        "total": len(transactions),
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/summary",
    response_model=TransactionSummaryResponse,
    summary="Get transaction summary statistics",
)
def get_transaction_summary(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get transaction summary statistics
    
    Returns total expenses, income, net, and transaction count.
    Optionally filter by date range.
    """
    service = TransactionService(db)
    summary = service.get_summary(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return summary


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get a specific transaction",
)
def get_transaction(
    transaction_id: int = Path(..., description="Transaction ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get a specific transaction by ID
    """
    service = TransactionService(db)
    transaction = service.get_transaction(transaction_id, user_id)
    if not transaction:
        raise NotFoundError(f"Transaction with ID {transaction_id} not found")
    return transaction


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update a transaction",
)
def update_transaction(
    transaction_data: TransactionUpdateRequest,
    transaction_id: int = Path(..., description="Transaction ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update a transaction
    
    All fields are optional. Only provided fields will be updated.
    """
    service = TransactionService(db)
    
    # Build kwargs from non-None values
    update_data = {}
    if transaction_data.description is not None:
        update_data["description"] = transaction_data.description
    if transaction_data.amount is not None:
        update_data["amount"] = transaction_data.amount
    if transaction_data.transaction_type is not None:
        update_data["transaction_type"] = transaction_data.transaction_type
    if transaction_data.transaction_date is not None:
        update_data["transaction_date"] = transaction_data.transaction_date
    if transaction_data.category_id is not None:
        update_data["category_id"] = transaction_data.category_id
    if transaction_data.source_id is not None:
        update_data["source_id"] = transaction_data.source_id
    if transaction_data.notes is not None:
        update_data["notes"] = transaction_data.notes
    if transaction_data.tags is not None:
        update_data["tags"] = transaction_data.tags
    if transaction_data.is_reconciled is not None:
        update_data["is_reconciled"] = transaction_data.is_reconciled
    
    transaction = service.update_transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        **update_data
    )
    return transaction


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction",
)
def delete_transaction(
    transaction_id: int = Path(..., description="Transaction ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Delete a transaction
    
    This permanently deletes the transaction.
    """
    service = TransactionService(db)
    service.delete_transaction(transaction_id, user_id)
    return None
