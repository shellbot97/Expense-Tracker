"""
Statement ingestion service - import transactions from bank statements
"""

import hashlib
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from src.models.transaction import Transaction
from src.models.source import Source
from src.parsers.csv_parser import CSVParser
from src.parsers.excel_parser import ExcelParser, EXCEL_SUPPORT
from src.utils.exceptions import ValidationError, NotFoundError


class StatementIngestionService:
    """
    Service for uploading and importing bank statements
    
    Handles CSV and Excel files, with duplicate detection and validation.
    """
    
    def __init__(self, db: Session):
        """
        Initialize statement ingestion service
        
        Args:
            db: Database session
        """
        self.db = db
    
    def import_csv(
        self,
        user_id: int,
        file_content: str,
        column_mapping: Dict[str, str],
        source_id: Optional[int] = None,
        auto_categorize: bool = True,
        skip_duplicates: bool = True,
    ) -> Dict:
        """
        Import transactions from CSV file
        
        Args:
            user_id: User ID
            file_content: Raw CSV string content
            column_mapping: Dict mapping CSV columns to transaction fields
            source_id: Optional source ID to associate transactions with
            auto_categorize: Whether to auto-categorize after import
            skip_duplicates: Whether to skip duplicate transactions
            
        Returns:
            Dict with import statistics
        """
        # Validate user has access to source
        if source_id:
            source = self.db.query(Source).filter(
                Source.id == source_id,
                Source.user_id == user_id
            ).first()
            if not source:
                raise NotFoundError("Source not found")
        
        # Parse CSV
        parser = CSVParser(column_mapping=column_mapping)
        try:
            parsed_transactions = parser.parse(file_content)
        except Exception as e:
            raise ValidationError(f"CSV parsing failed: {str(e)}")
        
        # Import transactions
        stats = self._import_transactions(
            user_id=user_id,
            transactions=parsed_transactions,
            source_id=source_id,
            import_source=f"CSV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            auto_categorize=auto_categorize,
            skip_duplicates=skip_duplicates,
        )
        
        return stats
    
    def import_excel(
        self,
        user_id: int,
        file_bytes: bytes,
        column_mapping: Dict[str, str],
        source_id: Optional[int] = None,
        sheet_name: Optional[str] = None,
        auto_categorize: bool = True,
        skip_duplicates: bool = True,
    ) -> Dict:
        """
        Import transactions from Excel file
        
        Args:
            user_id: User ID
            file_bytes: Raw Excel file bytes
            column_mapping: Dict mapping Excel columns to transaction fields
            source_id: Optional source ID to associate transactions with
            sheet_name: Sheet name to import (defaults to first sheet)
            auto_categorize: Whether to auto-categorize after import
            skip_duplicates: Whether to skip duplicate transactions
            
        Returns:
            Dict with import statistics
        """
        if not EXCEL_SUPPORT:
            raise ValidationError("Excel support not available. Install openpyxl: pip install openpyxl")
        
        # Validate user has access to source
        if source_id:
            source = self.db.query(Source).filter(
                Source.id == source_id,
                Source.user_id == user_id
            ).first()
            if not source:
                raise NotFoundError("Source not found")
        
        # Parse Excel
        parser = ExcelParser(column_mapping=column_mapping)
        try:
            parsed_transactions = parser.parse(file_bytes, sheet_name=sheet_name)
        except Exception as e:
            raise ValidationError(f"Excel parsing failed: {str(e)}")
        
        # Import transactions
        stats = self._import_transactions(
            user_id=user_id,
            transactions=parsed_transactions,
            source_id=source_id,
            import_source=f"Excel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            auto_categorize=auto_categorize,
            skip_duplicates=skip_duplicates,
        )
        
        return stats
    
    def _import_transactions(
        self,
        user_id: int,
        transactions: List[Dict],
        source_id: Optional[int],
        import_source: str,
        auto_categorize: bool,
        skip_duplicates: bool,
    ) -> Dict:
        """
        Import parsed transactions into database
        
        Args:
            user_id: User ID
            transactions: List of parsed transaction dicts
            source_id: Optional source ID
            import_source: Import source identifier
            auto_categorize: Whether to auto-categorize
            skip_duplicates: Whether to skip duplicates
            
        Returns:
            Dict with statistics
        """
        stats = {
            "total": len(transactions),
            "imported": 0,
            "skipped": 0,
            "duplicates": 0,
            "errors": [],
        }
        
        for idx, trans_dict in enumerate(transactions):
            try:
                # Validate and normalize transaction
                normalized = self._normalize_transaction(trans_dict, user_id, source_id)
                
                # Check for duplicates
                if skip_duplicates:
                    trans_hash = self._calculate_hash(normalized)
                    existing = self.db.query(Transaction).filter(
                        Transaction.user_id == user_id,
                        Transaction.transaction_hash == trans_hash
                    ).first()
                    
                    if existing:
                        stats["duplicates"] += 1
                        stats["skipped"] += 1
                        continue
                    
                    normalized["transaction_hash"] = trans_hash
                
                # Create transaction
                transaction = Transaction(**normalized)
                transaction.import_source = import_source
                transaction.import_date = datetime.utcnow()
                
                self.db.add(transaction)
                self.db.flush()  # Get ID for categorization
                
                # Auto-categorize if requested
                if auto_categorize:
                    self._auto_categorize_transaction(transaction)
                
                stats["imported"] += 1
                
            except Exception as e:
                stats["errors"].append(f"Row {idx + 1}: {str(e)}")
                stats["skipped"] += 1
                continue
        
        # Commit all transactions
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Failed to save transactions: {str(e)}")
        
        return stats
    
    def _normalize_transaction(
        self,
        trans_dict: Dict,
        user_id: int,
        source_id: Optional[int]
    ) -> Dict:
        """
        Normalize parsed transaction dict for database insertion
        
        Args:
            trans_dict: Parsed transaction dict
            user_id: User ID
            source_id: Optional source ID
            
        Returns:
            Normalized transaction dict
        """
        # Required fields
        if "date" not in trans_dict:
            raise ValidationError("Missing date field")
        if "amount" not in trans_dict:
            raise ValidationError("Missing amount field")
        
        # Parse date
        if isinstance(trans_dict["date"], str):
            try:
                trans_date = datetime.strptime(trans_dict["date"], "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError(f"Invalid date format: {trans_dict['date']}")
        elif isinstance(trans_dict["date"], date):
            trans_date = trans_dict["date"]
        else:
            raise ValidationError(f"Invalid date type: {type(trans_dict['date'])}")
        
        # Get amount (should already be in cents)
        amount = trans_dict["amount"]
        if not isinstance(amount, int):
            raise ValidationError(f"Amount must be integer (cents): {amount}")
        
        # Determine transaction type
        transaction_type = trans_dict.get("transaction_type")
        if not transaction_type:
            # Default based on amount sign
            transaction_type = "expense" if amount < 0 else "income"
        
        if transaction_type not in ["expense", "income", "transfer"]:
            raise ValidationError(f"Invalid transaction type: {transaction_type}")
        
        # Get description
        description = trans_dict.get("description", "Imported transaction")
        if not description or not description.strip():
            description = "Imported transaction"
        
        # Build normalized dict
        normalized = {
            "user_id": user_id,
            "source_id": source_id,
            "transaction_date": trans_date,
            "amount": abs(amount),  # Store as positive
            "transaction_type": transaction_type,
            "description": description[:500],  # Truncate to max length
            "original_description": description,
            "original_amount": trans_dict.get("original_amount"),
            "notes": trans_dict.get("notes"),
        }
        
        return normalized
    
    def _calculate_hash(self, transaction: Dict) -> str:
        """
        Calculate hash for duplicate detection
        
        Hash is based on: user_id + date + amount + description
        
        Args:
            transaction: Transaction dict
            
        Returns:
            SHA256 hash string
        """
        hash_parts = [
            str(transaction["user_id"]),
            str(transaction["transaction_date"]),
            str(transaction["amount"]),
            transaction["description"].lower().strip(),
        ]
        
        hash_input = "|".join(hash_parts).encode("utf-8")
        return hashlib.sha256(hash_input).hexdigest()
    
    def _auto_categorize_transaction(self, transaction: Transaction):
        """
        Auto-categorize transaction after import
        
        Args:
            transaction: Transaction object
        """
        # Import here to avoid circular dependency
        from src.services.categorization_service import CategorizationService
        
        categorization_service = CategorizationService(self.db)
        categorization_service.categorize_transaction(
            transaction.id,
            transaction.user_id,
            force=False
        )
    
    def validate_column_mapping(self, column_mapping: Dict[str, str]) -> bool:
        """
        Validate column mapping has required fields
        
        Args:
            column_mapping: Column mapping dict
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If mapping is invalid
        """
        # Check if date and amount are mapped
        has_date = any(v == "date" for v in column_mapping.values())
        has_amount = any(v == "amount" for v in column_mapping.values())
        
        if not has_date:
            raise ValidationError("Column mapping must include 'date' field")
        if not has_amount:
            raise ValidationError("Column mapping must include 'amount' field")
        
        # Valid field names
        valid_fields = ["date", "description", "amount", "transaction_type", "notes"]
        
        for field in column_mapping.values():
            if field not in valid_fields:
                raise ValidationError(f"Invalid field name: {field}")
        
        return True
