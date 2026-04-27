"""
Unit tests for CSV parser
"""

import pytest
from src.parsers.csv_parser import CSVParser
from src.utils.exceptions import ValidationError


# ============= Basic Parsing Tests =============

@pytest.mark.unit
class TestCSVParserBasic:
    """Tests for basic CSV parsing"""

    def test_parse_simple_csv(self):
        """Test parsing simple CSV with default mapping"""
        csv_content = """date,description,amount,transaction_type
2024-01-15,Walmart,50.00,expense
2024-01-16,Paycheck,1500.00,income"""
        
        parser = CSVParser(column_mapping={
            "date": "date",
            "description": "description",
            "amount": "amount",
            "transaction_type": "transaction_type",
        })
        
        transactions = parser.parse(csv_content)
        
        assert len(transactions) == 2
        assert transactions[0]["date"] == "2024-01-15"
        assert transactions[0]["description"] == "Walmart"
        assert transactions[0]["amount"] == 5000  # cents
        assert transactions[0]["transaction_type"] == "expense"

    def test_parse_empty_csv_raises_error(self):
        """Test that empty CSV raises ValidationError"""
        parser = CSVParser()
        
        with pytest.raises(ValidationError, match="empty"):
            parser.parse("")

    def test_parse_no_transactions_raises_error(self):
        """Test that CSV with only header raises error"""
        csv_content = "date,description,amount"
        parser = CSVParser(column_mapping={
            "date": "date",
            "description": "description",
            "amount": "amount",
        })
        
        with pytest.raises(ValidationError, match="No transactions found"):
            parser.parse(csv_content)


# ============= Date Parsing Tests =============

@pytest.mark.unit
class TestCSVDateParsing:
    """Tests for date parsing"""

    def test_parse_iso_date(self):
        """Test parsing ISO format date"""
        parser = CSVParser()
        date_str = parser._parse_date("2024-01-15")
        assert date_str == "2024-01-15"

    def test_parse_us_date(self):
        """Test parsing US format date"""
        parser = CSVParser()
        date_str = parser._parse_date("01/15/2024")
        assert date_str == "2024-01-15"

    def test_parse_named_month_date(self):
        """Test parsing named month date"""
        parser = CSVParser()
        date_str = parser._parse_date("Jan 15, 2024")
        assert date_str == "2024-01-15"

    def test_parse_empty_date_raises_error(self):
        """Test that empty date raises error"""
        parser = CSVParser()
        with pytest.raises(ValidationError, match="empty"):
            parser._parse_date("")

    def test_parse_invalid_date_raises_error(self):
        """Test that invalid date raises error"""
        parser = CSVParser()
        with pytest.raises(ValidationError, match="Could not parse date"):
            parser._parse_date("invalid-date")


# ============= Amount Parsing Tests =============

@pytest.mark.unit
class TestCSVAmountParsing:
    """Tests for amount parsing"""

    def test_parse_simple_amount(self):
        """Test parsing simple amount"""
        parser = CSVParser()
        amount = parser._parse_amount("100.50")
        assert amount == 10050

    def test_parse_amount_with_dollar_sign(self):
        """Test parsing amount with currency symbol"""
        parser = CSVParser()
        amount = parser._parse_amount("$100.50")
        assert amount == 10050

    def test_parse_amount_with_comma(self):
        """Test parsing amount with thousands separator"""
        parser = CSVParser()
        amount = parser._parse_amount("1,234.56")
        assert amount == 123456

    def test_parse_negative_amount(self):
        """Test parsing negative amount"""
        parser = CSVParser()
        amount = parser._parse_amount("-100.50")
        assert amount == -10050

    def test_parse_amount_with_parentheses(self):
        """Test parsing amount with parentheses (negative)"""
        parser = CSVParser()
        amount = parser._parse_amount("(100.50)")
        assert amount == -10050

    def test_parse_empty_amount_raises_error(self):
        """Test that empty amount raises error"""
        parser = CSVParser()
        with pytest.raises(ValidationError, match="empty"):
            parser._parse_amount("")

    def test_parse_invalid_amount_raises_error(self):
        """Test that invalid amount raises error"""
        parser = CSVParser()
        with pytest.raises(ValidationError, match="Could not parse amount"):
            parser._parse_amount("not-a-number")


# ============= Column Mapping Tests =============

@pytest.mark.unit
class TestCSVColumnMapping:
    """Tests for custom column mapping"""

    def test_parse_with_custom_mapping(self):
        """Test parsing CSV with custom column names"""
        csv_content = """Date,Memo,Amount,Type
2024-01-15,Groceries,50.00,expense"""
        
        parser = CSVParser(column_mapping={
            "Date": "date",
            "Memo": "description",
            "Amount": "amount",
            "Type": "transaction_type",
        })
        
        transactions = parser.parse(csv_content)
        
        assert len(transactions) == 1
        assert transactions[0]["date"] == "2024-01-15"
        assert transactions[0]["description"] == "Groceries"

    def test_detect_columns(self):
        """Test detecting CSV columns"""
        csv_content = """Date,Description,Amount
2024-01-15,Test,100.00"""
        
        parser = CSVParser()
        columns = parser.detect_columns(csv_content)
        
        assert columns == ["Date", "Description", "Amount"]

    def test_detect_columns_empty_csv(self):
        """Test detecting columns from empty CSV"""
        parser = CSVParser()
        columns = parser.detect_columns("")
        assert columns == []


# ============= Error Handling Tests =============

@pytest.mark.unit
class TestCSVErrorHandling:
    """Tests for error handling"""

    def test_parse_missing_required_field(self):
        """Test parsing CSV with missing required field"""
        csv_content = """description,transaction_type
Walmart,expense"""
        
        parser = CSVParser(column_mapping={
            "description": "description",
            "transaction_type": "transaction_type",
        })
        
        # Should skip row with missing required field
        with pytest.raises(ValidationError, match="No transactions found"):
            parser.parse(csv_content)

    def test_parse_invalid_csv_format(self):
        """Test parsing malformed CSV"""
        csv_content = '''date,description,amount
2024-01-15,"broken quote,50.00'''
        
        parser = CSVParser(column_mapping={
            "date": "date",
            "description": "description",
            "amount": "amount",
        })
        
        # Should handle gracefully
        try:
            transactions = parser.parse(csv_content)
            assert len(transactions) >= 0
        except ValidationError:
            pass  # Expected

    def test_parse_row_error_skips_invalid_rows(self):
        """Test that invalid rows are skipped"""
        csv_content = """date,description,amount
2024-01-15,Valid,100.00
invalid-date,Invalid,50.00
2024-01-17,Valid,75.00"""
        
        parser = CSVParser(column_mapping={
            "date": "date",
            "description": "description",
            "amount": "amount",
        })
        
        # Should skip row 2 and return 2 transactions
        transactions = parser.parse(csv_content)
        assert len(transactions) == 2
        assert transactions[0]["description"] == "Valid"
        assert transactions[1]["description"] == "Valid"
