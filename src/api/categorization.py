"""
Categorization API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, Body, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.services.auth_service import AuthService
from src.services.categorization_service import CategorizationService
from src.api.schemas import (
    CategorizeTransactionRequest,
    CategorizeResponse,
    BulkCategorizeRequest,
    BulkCategorizeResponse,
    CategorySuggestion,
    CategorySuggestionsResponse,
    UncategorizedCountResponse,
    ManualCategorizeRequest,
    TransactionResponse,
)
from src.utils.exceptions import InvalidTokenError

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
    "/transactions/{transaction_id}/categorize",
    response_model=CategorizeResponse,
    summary="Categorize a transaction",
)
def categorize_transaction(
    transaction_id: int = Path(..., description="Transaction ID"),
    request: CategorizeTransactionRequest = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Automatically categorize a transaction using regex rules
    
    - **force**: Force re-categorization even if manually categorized
    
    Returns the assigned category and confidence score.
    Skips manually categorized transactions unless force=true.
    """
    service = CategorizationService(db)
    category_id, confidence = service.categorize_transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        force=request.force,
    )
    
    # Get updated transaction to check manually_categorized flag
    from src.models.transaction import Transaction
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    return {
        "category_id": category_id,
        "confidence": confidence,
        "manually_categorized": transaction.is_manually_categorized if transaction else False,
    }


@router.post(
    "/transactions/categorize-bulk",
    response_model=BulkCategorizeResponse,
    summary="Bulk categorize transactions",
)
def categorize_bulk(
    request: BulkCategorizeRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Categorize multiple transactions in bulk
    
    - **transaction_type**: Optional filter by type (expense/income/transfer)
    - **force**: Force re-categorization of manually categorized transactions
    - **limit**: Maximum number of transactions to process
    
    Returns statistics about the categorization process.
    """
    service = CategorizationService(db)
    stats = service.categorize_bulk(
        user_id=user_id,
        transaction_type=request.transaction_type,
        force=request.force,
        limit=request.limit,
    )
    
    return stats


@router.get(
    "/transactions/uncategorized/count",
    response_model=UncategorizedCountResponse,
    summary="Get uncategorized transaction count",
)
def get_uncategorized_count(
    transaction_type: Optional[str] = Query(None, pattern="^(expense|income|transfer)$"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get count of uncategorized transactions
    
    Optionally filter by transaction type.
    """
    service = CategorizationService(db)
    count = service.get_uncategorized_count(
        user_id=user_id,
        transaction_type=transaction_type,
    )
    
    return {
        "count": count,
        "transaction_type": transaction_type,
    }


@router.post(
    "/transactions/{transaction_id}/suggest-categories",
    response_model=CategorySuggestionsResponse,
    summary="Get category suggestions",
)
def suggest_categories(
    transaction_id: int = Path(..., description="Transaction ID"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get category suggestions for a transaction
    
    Returns up to 5 matching categories sorted by confidence.
    Useful for manual categorization UI.
    """
    from src.models.transaction import Transaction
    from src.utils.exceptions import NotFoundError
    
    # Get transaction
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
        .first()
    )
    
    if not transaction:
        raise NotFoundError(f"Transaction with ID {transaction_id} not found")
    
    service = CategorizationService(db)
    matches = service.suggest_category(
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        user_id=user_id,
    )
    
    suggestions = [
        CategorySuggestion(
            category_id=cat_id,
            category_name=cat_name,
            confidence=conf,
        )
        for cat_id, cat_name, conf in matches
    ]
    
    return {"suggestions": suggestions}


@router.put(
    "/transactions/{transaction_id}/manual-categorize",
    response_model=TransactionResponse,
    summary="Manually categorize a transaction",
)
def manual_categorize(
    transaction_id: int = Path(..., description="Transaction ID"),
    request: ManualCategorizeRequest = Body(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Manually categorize or uncategorize a transaction
    
    - **category_id**: Category ID to assign (null to uncategorize)
    
    This marks the transaction as manually categorized, preventing
    automatic re-categorization unless explicitly forced.
    """
    service = CategorizationService(db)
    transaction = service.manually_categorize(
        transaction_id=transaction_id,
        user_id=user_id,
        category_id=request.category_id,
    )
    
    return transaction
