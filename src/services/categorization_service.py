"""
Categorization service - Auto-categorize transactions using regex rules
"""

import re
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.transaction import Transaction
from src.models.category import Category
from src.utils.exceptions import NotFoundError, ValidationError


class CategorizationService:
    """Service for automatic transaction categorization"""

    def __init__(self, db: Session):
        self.db = db

    def categorize_transaction(
        self,
        transaction_id: int,
        user_id: int,
        force: bool = False,
    ) -> Tuple[Optional[int], float]:
        """
        Categorize a single transaction using regex rules
        
        Args:
            transaction_id: Transaction ID to categorize
            user_id: User ID for authorization
            force: Force re-categorization even if manually categorized
            
        Returns:
            Tuple of (category_id, confidence_score)
            
        Raises:
            NotFoundError: If transaction not found
        """
        # Get transaction
        transaction = (
            self.db.query(Transaction)
            .filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
            .first()
        )
        
        if not transaction:
            raise NotFoundError(f"Transaction with ID {transaction_id} not found")
        
        # Skip if manually categorized and not forced
        if transaction.is_manually_categorized and not force:
            return transaction.category_id, 0.0
        
        # Find matching category
        category_id, confidence = self._find_best_match(
            transaction.description,
            transaction.transaction_type,
            user_id,
        )
        
        if category_id:
            # Update transaction
            transaction.category_id = category_id
            transaction.categorized_by_ai = False  # Rule-based, not AI
            transaction.ai_confidence_score = int(confidence * 100)
            transaction.is_manually_categorized = False
            
            self.db.commit()
            self.db.refresh(transaction)
        
        return category_id, confidence

    def categorize_bulk(
        self,
        user_id: int,
        transaction_type: Optional[str] = None,
        force: bool = False,
        limit: Optional[int] = None,
    ) -> dict:
        """
        Categorize multiple transactions in bulk
        
        Args:
            user_id: User ID
            transaction_type: Optional filter by type
            force: Force re-categorization
            limit: Max transactions to process
            
        Returns:
            Dict with statistics: {
                "processed": int,
                "categorized": int,
                "uncategorized": int,
                "skipped": int
            }
        """
        # Build query
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        if not force:
            # Only process uncategorized or auto-categorized transactions
            query = query.filter(Transaction.is_manually_categorized == False)
        
        if limit:
            query = query.limit(limit)
        
        transactions = query.all()
        
        stats = {
            "processed": 0,
            "categorized": 0,
            "uncategorized": 0,
            "skipped": 0,
        }
        
        for transaction in transactions:
            stats["processed"] += 1
            
            # Skip if manually categorized and not forced
            if transaction.is_manually_categorized and not force:
                stats["skipped"] += 1
                continue
            
            # Find match
            category_id, confidence = self._find_best_match(
                transaction.description,
                transaction.transaction_type,
                user_id,
            )
            
            if category_id:
                transaction.category_id = category_id
                transaction.categorized_by_ai = False
                transaction.ai_confidence_score = int(confidence * 100)
                transaction.is_manually_categorized = False
                stats["categorized"] += 1
            else:
                stats["uncategorized"] += 1
        
        self.db.commit()
        
        return stats

    def get_uncategorized_count(
        self,
        user_id: int,
        transaction_type: Optional[str] = None,
    ) -> int:
        """Get count of uncategorized transactions"""
        query = (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.category_id.is_(None),
            )
        )
        
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        return query.count()

    def suggest_category(
        self,
        description: str,
        transaction_type: str,
        user_id: int,
    ) -> List[Tuple[int, str, float]]:
        """
        Suggest categories for a transaction description
        
        Args:
            description: Transaction description
            transaction_type: Type (expense/income/transfer)
            user_id: User ID
            
        Returns:
            List of (category_id, category_name, confidence) sorted by confidence
        """
        matches = self._find_all_matches(description, transaction_type, user_id)
        return matches[:5]  # Top 5 suggestions

    def manually_categorize(
        self,
        transaction_id: int,
        user_id: int,
        category_id: Optional[int],
    ) -> Transaction:
        """
        Manually categorize a transaction
        
        This marks the transaction as manually_categorized to prevent
        automatic re-categorization.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID
            category_id: Category ID (None to uncategorize)
            
        Returns:
            Updated transaction
            
        Raises:
            NotFoundError: If transaction or category not found
        """
        transaction = (
            self.db.query(Transaction)
            .filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
            .first()
        )
        
        if not transaction:
            raise NotFoundError(f"Transaction with ID {transaction_id} not found")
        
        # Validate category if provided
        if category_id:
            category = (
                self.db.query(Category)
                .filter(
                    Category.id == category_id,
                    Category.user_id == user_id,
                )
                .first()
            )
            
            if not category:
                raise NotFoundError(f"Category with ID {category_id} not found")
            
            # Check type compatibility
            if category.category_type != transaction.transaction_type:
                raise ValidationError(
                    f"Category type '{category.category_type}' does not match "
                    f"transaction type '{transaction.transaction_type}'"
                )
        
        # Update transaction
        transaction.category_id = category_id
        transaction.is_manually_categorized = True
        transaction.categorized_by_ai = False
        transaction.ai_confidence_score = None
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction

    # Private helper methods

    def _find_best_match(
        self,
        description: str,
        transaction_type: str,
        user_id: int,
    ) -> Tuple[Optional[int], float]:
        """Find best matching category for description"""
        matches = self._find_all_matches(description, transaction_type, user_id)
        
        if matches:
            # Return category_id and confidence of best match
            return matches[0][0], matches[0][2]
        
        return None, 0.0

    def _find_all_matches(
        self,
        description: str,
        transaction_type: str,
        user_id: int,
    ) -> List[Tuple[int, str, float]]:
        """
        Find all matching categories with confidence scores
        
        Returns:
            List of (category_id, category_name, confidence) sorted by confidence
        """
        # Get all categories with matching patterns
        categories = (
            self.db.query(Category)
            .filter(
                Category.user_id == user_id,
                Category.category_type == transaction_type,
                Category.matching_pattern.isnot(None),
            )
            .all()
        )
        
        matches = []
        
        for category in categories:
            confidence = self._calculate_match_confidence(
                description,
                category.matching_pattern,
            )
            
            if confidence > 0:
                matches.append((category.id, category.name, confidence))
        
        # Sort by confidence descending
        matches.sort(key=lambda x: x[2], reverse=True)
        
        return matches

    def _calculate_match_confidence(
        self,
        description: str,
        pattern: str,
    ) -> float:
        """
        Calculate confidence score for a regex match
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            # Try to compile and match pattern
            regex = re.compile(pattern, re.IGNORECASE)
            match = regex.search(description)
            
            if not match:
                return 0.0
            
            # Calculate confidence based on match quality
            matched_length = len(match.group(0))
            desc_length = len(description.strip())
            
            if desc_length == 0:
                return 0.0
            
            # Base confidence: ratio of matched text to total description
            base_confidence = matched_length / desc_length
            
            # Boost confidence for exact or nearly exact matches
            if matched_length >= desc_length * 0.8:
                base_confidence = min(0.95, base_confidence + 0.3)
            elif matched_length >= desc_length * 0.5:
                base_confidence = min(0.85, base_confidence + 0.2)
            
            # Cap at 0.95 (never 100% for rule-based)
            return min(0.95, base_confidence)
            
        except re.error:
            # Invalid regex pattern
            return 0.0
