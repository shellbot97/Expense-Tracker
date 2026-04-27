"""
CSV statement parser for importing bank transactions
"""

import csv
from datetime import datetime
from typing import List, Dict, Optional
from io import StringIO
from src.utils.exceptions import ValidationError


class CSVParser:
    """
    Parse CSV bank statements into structured transaction data
    
    Supports flexible column mapping to handle different bank formats.
    """
    
    def __init__(self, column_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize CSV parser with column mapping
        
        Args:
            column_mapping: Dict mapping CSV columns to transaction fields
                Example: {"Date": "date", "Description": "description", "Amount": "amount"}
                If None, uses default mapping
        """
        self.column_mapping = column_mapping or {
            "date": "date",
            "description": "description",
            "amount": "amount",
            "transaction_type": "transaction_type",
        }
    
    def parse(self, file_content: str, has_header: bool = True) -> List[Dict]:
        """
        Parse CSV content into transaction dictionaries
        
        Args:
            file_content: Raw CSV string content
            has_header: Whether CSV has header row
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            ValidationError: If CSV format is invalid
        """
        if not file_content or not file_content.strip():
            raise ValidationError("CSV content is empty")
        
        try:
            # Parse CSV
            reader = csv.DictReader(StringIO(file_content))
            
            if not has_header:
                # If no header, use first row as header
                reader = csv.DictReader(StringIO(file_content), fieldnames=None)
            
            transactions = []
            for row_num, row in enumerate(reader, start=1):
                try:
                    transaction = self._parse_row(row)
                    transactions.append(transaction)
                except Exception as e:
                    # Skip invalid rows but continue processing
                    continue
            
            if not transactions:
                raise ValidationError("No transactions found in CSV")
            
            return transactions
            
        except csv.Error as e:
            raise ValidationError(f"Invalid CSV format: {str(e)}")
    
    def _parse_row(self, row: Dict[str, str]) -> Dict:
        """
        Parse a single CSV row into transaction dict
        
        Args:
            row: CSV row as dictionary
            
        Returns:
            Transaction dictionary
        """
        transaction = {}
        
        # Map columns
        for csv_col, field_name in self.column_mapping.items():
            if csv_col in row:
                value = row[csv_col]
                
                # Parse based on field type
                if field_name == "date":
                    transaction[field_name] = self._parse_date(value)
                elif field_name == "amount":
                    transaction[field_name] = self._parse_amount(value)
                else:
                    transaction[field_name] = value.strip()
        
        # Validate required fields
        required_fields = ["date", "amount"]
        for field in required_fields:
            if field not in transaction:
                raise ValidationError(f"Missing required field: {field}")
        
        return transaction
    
    def _parse_date(self, date_str: str) -> str:
        """
        Parse date string into ISO format (YYYY-MM-DD)
        
        Tries multiple common date formats
        """
        if not date_str or not date_str.strip():
            raise ValidationError("Date is empty")
        
        date_str = date_str.strip()
        
        # Common date formats
        formats = [
            "%Y-%m-%d",      # 2024-01-15
            "%m/%d/%Y",      # 01/15/2024
            "%d/%m/%Y",      # 15/01/2024
            "%Y/%m/%d",      # 2024/01/15
            "%m-%d-%Y",      # 01-15-2024
            "%d-%m-%Y",      # 15-01-2024
            "%b %d, %Y",     # Jan 15, 2024
            "%B %d, %Y",     # January 15, 2024
            "%d %b %Y",      # 15 Jan 2024
            "%d %B %Y",      # 15 January 2024
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        raise ValidationError(f"Could not parse date: {date_str}")
    
    def _parse_amount(self, amount_str: str) -> int:
        """
        Parse amount string into cents (integer)
        
        Handles various formats:
        - $100.50 -> 10050
        - -100.50 -> -10050
        - 1,234.56 -> 123456
        """
        if not amount_str or not amount_str.strip():
            raise ValidationError("Amount is empty")
        
        amount_str = amount_str.strip()
        
        # Remove currency symbols and spaces
        amount_str = amount_str.replace("$", "").replace("€", "").replace("£", "")
        amount_str = amount_str.replace(",", "").replace(" ", "")
        
        # Handle parentheses as negative (e.g., "(100.50)" = -100.50)
        is_negative = False
        if amount_str.startswith("(") and amount_str.endswith(")"):
            is_negative = True
            amount_str = amount_str[1:-1]
        
        try:
            # Parse as float then convert to cents
            amount_float = float(amount_str)
            
            if is_negative:
                amount_float = -amount_float
            
            # Convert to cents and round to avoid float precision issues
            amount_cents = int(round(amount_float * 100))
            
            return amount_cents
            
        except ValueError:
            raise ValidationError(f"Could not parse amount: {amount_str}")
    
    def detect_columns(self, file_content: str) -> List[str]:
        """
        Detect column headers from CSV file
        
        Args:
            file_content: Raw CSV string content
            
        Returns:
            List of column names
        """
        if not file_content or not file_content.strip():
            return []
        
        try:
            reader = csv.reader(StringIO(file_content))
            first_row = next(reader, None)
            return first_row if first_row else []
        except csv.Error:
            return []
