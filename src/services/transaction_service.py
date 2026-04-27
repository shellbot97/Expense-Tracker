"""
Transaction service - Business logic for transaction management
"""

from typing import Optional, List, Dict
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.models.transaction import Transaction
from src.models.category import Category
from src.models.source import Source
from src.utils.exceptions import ValidationError, NotFoundError


class TransactionService:
    """Service for managing financial transactions"""

    VALID_TRANSACTION_TYPES = ["expense", "income", "transfer"]

    def __init__(self, db: Session):
        self.db = db

    def create_transaction(
        self,
        user_id: int,
        description: str,
        amount: int,
        transaction_type: str,
        transaction_date: date,
        category_id: Optional[int] = None,
        source_id: Optional[int] = None,
        notes: Optional[str] = None,
        tags: Optional[str] = None,
        original_description: Optional[str] = None,
        original_amount: Optional[str] = None,
    ) -> Transaction:
        """
        Create a new transaction
        
        Args:
            user_id: User ID
            description: Transaction description
            amount: Amount in cents
            transaction_type: Type (expense/income/transfer)
            transaction_date: Date of transaction
            category_id: Optional category ID
            source_id: Optional source ID
            notes: Optional notes
            tags: Optional comma-separated tags
            original_description: Original description from import
            original_amount: Original amount from import
            
        Returns:
            Created transaction
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        self._validate_description(description)
        self._validate_amount(amount)
        self._validate_transaction_type(transaction_type)
        
        # Validate category and source belong to user
        if category_id:
            self._validate_category_ownership(category_id, user_id)
        if source_id:
            self._validate_source_ownership(source_id, user_id)

        # Create transaction
        transaction = Transaction(
            user_id=user_id,
            description=description.strip(),
            amount=amount,
            transaction_type=transaction_type,
            transaction_date=transaction_date,
            category_id=category_id,
            source_id=source_id,
            notes=notes,
            tags=tags,
            original_description=original_description,
            original_amount=original_amount,
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def get_transaction(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            Transaction or None if not found
        """
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
            .first()
        )

    def list_transactions(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[str] = None,
        category_id: Optional[int] = None,
        source_id: Optional[int] = None,
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Transaction]:
        """
        List transactions with filters
        
        Args:
            user_id: User ID
            start_date: Filter by start date
            end_date: Filter by end date
            transaction_type: Filter by type
            category_id: Filter by category
            source_id: Filter by source
            min_amount: Minimum amount filter
            max_amount: Maximum amount filter
            limit: Max results to return
            offset: Pagination offset
            
        Returns:
            List of transactions
        """
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)

        # Apply filters
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if source_id:
            query = query.filter(Transaction.source_id == source_id)
        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)

        # Order by date descending (newest first)
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_transaction(
        self,
        transaction_id: int,
        user_id: int,
        description: Optional[str] = None,
        amount: Optional[int] = None,
        transaction_type: Optional[str] = None,
        transaction_date: Optional[date] = None,
        category_id: Optional[int] = None,
        source_id: Optional[int] = None,
        notes: Optional[str] = None,
        tags: Optional[str] = None,
        is_reconciled: Optional[bool] = None,
    ) -> Transaction:
        """
        Update transaction
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            **kwargs: Fields to update
            
        Returns:
            Updated transaction
            
        Raises:
            NotFoundError: If transaction not found
            ValidationError: If validation fails
        """
        transaction = self.get_transaction(transaction_id, user_id)
        if not transaction:
            raise NotFoundError(f"Transaction with ID {transaction_id} not found")

        # Validate updates
        if description is not None:
            self._validate_description(description)
            transaction.description = description.strip()
        if amount is not None:
            self._validate_amount(amount)
            transaction.amount = amount
        if transaction_type is not None:
            self._validate_transaction_type(transaction_type)
            transaction.transaction_type = transaction_type
        if transaction_date is not None:
            transaction.transaction_date = transaction_date
        if category_id is not None:
            self._validate_category_ownership(category_id, user_id)
            transaction.category_id = category_id
        if source_id is not None:
            self._validate_source_ownership(source_id, user_id)
            transaction.source_id = source_id
        if notes is not None:
            transaction.notes = notes
        if tags is not None:
            transaction.tags = tags
        if is_reconciled is not None:
            transaction.is_reconciled = is_reconciled

        # Mark as manually categorized if category changed
        if category_id is not None:
            transaction.is_manually_categorized = True

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """
        Delete transaction
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If transaction not found
        """
        transaction = self.get_transaction(transaction_id, user_id)
        if not transaction:
            raise NotFoundError(f"Transaction with ID {transaction_id} not found")

        self.db.delete(transaction)
        self.db.commit()

        return True

    def get_summary(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Get transaction summary statistics
        
        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with summary stats
        """
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        # Get all transactions
        transactions = query.all()

        # Calculate stats
        total_expenses = sum(
            t.amount for t in transactions if t.transaction_type == "expense"
        )
        total_income = sum(
            t.amount for t in transactions if t.transaction_type == "income"
        )
        net = total_income - total_expenses

        return {
            "total_expenses": total_expenses,
            "total_income": total_income,
            "net": net,
            "transaction_count": len(transactions),
        }

    # Private validation methods

    def _validate_description(self, description: str):
        """Validate transaction description"""
        if not description or not description.strip():
            raise ValidationError("Description cannot be empty")
        if len(description) > 500:
            raise ValidationError("Description cannot exceed 500 characters")

    def _validate_amount(self, amount: int):
        """Validate transaction amount"""
        if not isinstance(amount, int):
            raise ValidationError("Amount must be an integer (cents)")
        if amount < 0:
            raise ValidationError("Amount cannot be negative")
        if amount == 0:
            raise ValidationError("Amount cannot be zero")

    def _validate_transaction_type(self, transaction_type: str):
        """Validate transaction type"""
        if transaction_type not in self.VALID_TRANSACTION_TYPES:
            raise ValidationError(
                f"Invalid transaction_type. Must be one of: {', '.join(self.VALID_TRANSACTION_TYPES)}"
            )

    def _validate_category_ownership(self, category_id: int, user_id: int):
        """Validate that category belongs to user"""
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id,
        ).first()
        if not category:
            raise ValidationError(f"Category with ID {category_id} not found or not owned by user")

    def _validate_source_ownership(self, source_id: int, user_id: int):
        """Validate that source belongs to user"""
        source = self.db.query(Source).filter(
            Source.id == source_id,
            Source.user_id == user_id,
        ).first()
        if not source:
            raise ValidationError(f"Source with ID {source_id} not found or not owned by user")
