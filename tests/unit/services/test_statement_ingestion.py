"""
Unit tests for StatementIngestionService
"""

import pytest
from datetime import date
import openpyxl
from io import BytesIO
from src.services.statement_ingestion_service import StatementIngestionService
from src.services.auth_service import AuthService
from src.services.source_service import SourceService
from src.models.user import User
from src.models.source import Source
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.budget import Budget
from src.utils.exceptions import ValidationError, NotFoundError


# ============= Fixtures =============

@pytest.fixture
def db_session(tmp_path):
    """Create a temporary database for testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.config.database import Base

    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    auth_service = AuthService(db_session)
    return auth_service.register_user("testuser", "test@example.com", "password123")


@pytest.fixture
def test_source(db_session, test_user):
    """Create a test source"""
    source_service = SourceService(db_session)
    return source_service.create_source(
        test_user.id,
        name="Test Bank",
        source_type="bank_account",
    )


@pytest.fixture
def ingestion_service(db_session):
    """Create StatementIngestionService instance"""
    return StatementIngestionService(db_session)


def create_test_excel(data, headers=None):
    """Helper function to create test Excel file"""
    wb = openpyxl.Workbook()
    ws = wb.active
    
    if headers:
        ws.append(headers)
    
    for row in data:
        ws.append(row)
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


# ============= CSV Import Tests =============

@pytest.mark.unit
class TestCSVImport:
    """Tests for CSV import"""

    def test_import_simple_csv(self, ingestion_service, test_user, db_session):
        """Test importing simple CSV"""
        csv_content = """date,description,amount,transaction_type
2024-01-15,Walmart,-50.00,expense
2024-01-16,Paycheck,1500.00,income"""
        
        column_mapping = {
            "date": "date",
            "description": "description",
            "amount": "amount",
            "transaction_type": "transaction_type",
        }
        
        stats = ingestion_service.import_csv(
            user_id=test_user.id,
            file_content=csv_content,
            column_mapping=column_mapping,
            auto_categorize=False,
        )
        
        assert stats["total"] == 2
        assert stats["imported"] == 2
        assert stats["skipped"] == 0
        assert stats["duplicates"] == 0
        
        # Verify transactions in database
        transactions = db_session.query(Transaction).filter_by(user_id=test_user.id).all()
        assert len(transactions) == 2

    def test_import_csv_with_source(self, ingestion_service, test_user, test_source):
        """Test importing CSV with source association"""
        csv_content = """date,description,amount
2024-01-15,Walmart,50.00"""
        
        column_mapping = {
            "date": "date",
            "description": "description",
            "amount": "amount",
        }
        
        stats = ingestion_service.import_csv(
            user_id=test_user.id,
            file_content=csv_content,
            column_mapping=column_mapping,
            source_id=test_source.id,
            auto_categorize=False,
        )
        
        assert stats["imported"] == 1

    def test_import_csv_invalid_source_raises_error(self, ingestion_service, test_user):
        """Test that invalid source ID raises error"""
        csv_content = """date,description,amount
2024-01-15,Walmart,50.00"""
        
        column_mapping = {
            "date": "date",
            "description": "description",
            "amount": "amount",
        }
        
        with pytest.raises(NotFoundError, match="Source not found"):
            ingestion_service.import_csv(
                user_id=test_user.id,
                file_content=csv_content,
                column_mapping=column_mapping,
                source_id=99999,
            )

    def test_import_csv_duplicate_detection(self, ingestion_service, test_user, db_session):
        """Test that duplicate transactions are detected"""
        csv_content = """date,description,amount
2024-01-15,Walmart,50.00
2024-01-15,Walmart,50.00"""
        
        column_mapping = {
            "date": "date",
            "description": "description",
            "amount": "amount",
        }
        
        stats = ingestion_service.import_csv(
            user_id=test_user.id,
            file_content=csv_content,
            column_mapping=column_mapping,
            skip_duplicates=True,
            auto_categorize=False,
        )
        
        assert stats["total"] == 2
        assert stats["imported"] == 1
        assert stats["duplicates"] == 1

    def test_import_csv_with_errors(self, ingestion_service, test_user):
        """Test importing CSV with some invalid rows skipped during parsing"""
        csv_content = """date,description,amount
2024-01-15,Valid,50.00
invalid-date,Invalid,50.00
2024-01-17,Valid,75.00"""
        
        column_mapping = {
            "date": "date",
            "description": "description",
            "amount": "amount",
        }
        
        stats = ingestion_service.import_csv(
            user_id=test_user.id,
            file_content=csv_content,
            column_mapping=column_mapping,
            auto_categorize=False,
        )
        
        # Invalid row is skipped during parsing, so total is 2 not 3
        assert stats["total"] == 2
        assert stats["imported"] == 2
        assert stats["skipped"] == 0


# ============= Excel Import Tests =============

@pytest.mark.unit
class TestExcelImport:
    """Tests for Excel import"""

    def test_import_simple_excel(self, ingestion_service, test_user, db_session):
        """Test importing simple Excel"""
        data = [
            ("2024-01-15", "Walmart", -50.00, "expense"),
            ("2024-01-16", "Paycheck", 1500.00, "income"),
        ]
        headers = ["date", "description", "amount", "transaction_type"]
        excel_bytes = create_test_excel(data, headers)
        
        column_mapping = {
            "date": "date",
            "description": "description",
            "amount": "amount",
            "transaction_type": "transaction_type",
        }
        
        stats = ingestion_service.import_excel(
            user_id=test_user.id,
            file_bytes=excel_bytes,
            column_mapping=column_mapping,
            auto_categorize=False,
        )
        
        assert stats["total"] == 2
        assert stats["imported"] == 2
        assert stats["skipped"] == 0
        
        # Verify transactions in database
        transactions = db_session.query(Transaction).filter_by(user_id=test_user.id).all()
        assert len(transactions) == 2

    def test_import_excel_with_source(self, ingestion_service, test_user, test_source):
        """Test importing Excel with source association"""
        data = [("2024-01-15", "Walmart", 50.00)]
        headers = ["date", "description", "amount"]
        excel_bytes = create_test_excel(data, headers)
        
        column_mapping = {
            "date": "date",
            "description": "description",
            "amount": "amount",
        }
        
        stats = ingestion_service.import_excel(
            user_id=test_user.id,
            file_bytes=excel_bytes,
            column_mapping=column_mapping,
            source_id=test_source.id,
            auto_categorize=False,
        )
        
        assert stats["imported"] == 1


# ============= Normalization Tests =============

@pytest.mark.unit
class TestTransactionNormalization:
    """Tests for transaction normalization"""

    def test_normalize_with_negative_amount(self, ingestion_service, test_user):
        """Test that negative amounts are converted to positive with type"""
        trans_dict = {
            "date": "2024-01-15",
            "amount": -5000,
            "description": "Walmart",
        }
        
        normalized = ingestion_service._normalize_transaction(trans_dict, test_user.id, None)
        
        assert normalized["amount"] == 5000  # Positive
        assert normalized["transaction_type"] == "expense"

    def test_normalize_with_positive_amount(self, ingestion_service, test_user):
        """Test that positive amounts default to income"""
        trans_dict = {
            "date": "2024-01-15",
            "amount": 5000,
            "description": "Paycheck",
        }
        
        normalized = ingestion_service._normalize_transaction(trans_dict, test_user.id, None)
        
        assert normalized["amount"] == 5000
        assert normalized["transaction_type"] == "income"

    def test_normalize_missing_date_raises_error(self, ingestion_service, test_user):
        """Test that missing date raises error"""
        trans_dict = {
            "amount": 5000,
            "description": "Test",
        }
        
        with pytest.raises(ValidationError, match="Missing date"):
            ingestion_service._normalize_transaction(trans_dict, test_user.id, None)

    def test_normalize_missing_amount_raises_error(self, ingestion_service, test_user):
        """Test that missing amount raises error"""
        trans_dict = {
            "date": "2024-01-15",
            "description": "Test",
        }
        
        with pytest.raises(ValidationError, match="Missing amount"):
            ingestion_service._normalize_transaction(trans_dict, test_user.id, None)

    def test_normalize_truncates_long_description(self, ingestion_service, test_user):
        """Test that long descriptions are truncated"""
        trans_dict = {
            "date": "2024-01-15",
            "amount": 5000,
            "description": "A" * 600,  # Longer than 500 chars
        }
        
        normalized = ingestion_service._normalize_transaction(trans_dict, test_user.id, None)
        
        assert len(normalized["description"]) == 500


# ============= Duplicate Detection Tests =============

@pytest.mark.unit
class TestDuplicateDetection:
    """Tests for duplicate detection"""

    def test_calculate_hash(self, ingestion_service):
        """Test hash calculation for duplicate detection"""
        transaction = {
            "user_id": 1,
            "transaction_date": date(2024, 1, 15),
            "amount": 5000,
            "description": "Walmart",
        }
        
        hash1 = ingestion_service._calculate_hash(transaction)
        hash2 = ingestion_service._calculate_hash(transaction)
        
        # Same transaction should have same hash
        assert hash1 == hash2

    def test_different_transactions_different_hash(self, ingestion_service):
        """Test that different transactions have different hashes"""
        transaction1 = {
            "user_id": 1,
            "transaction_date": date(2024, 1, 15),
            "amount": 5000,
            "description": "Walmart",
        }
        
        transaction2 = {
            "user_id": 1,
            "transaction_date": date(2024, 1, 15),
            "amount": 5000,
            "description": "Target",  # Different description
        }
        
        hash1 = ingestion_service._calculate_hash(transaction1)
        hash2 = ingestion_service._calculate_hash(transaction2)
        
        assert hash1 != hash2


# ============= Column Mapping Validation Tests =============

@pytest.mark.unit
class TestColumnMappingValidation:
    """Tests for column mapping validation"""

    def test_validate_valid_mapping(self, ingestion_service):
        """Test that valid mapping passes validation"""
        mapping = {
            "Date": "date",
            "Description": "description",
            "Amount": "amount",
        }
        
        assert ingestion_service.validate_column_mapping(mapping) is True

    def test_validate_missing_date_raises_error(self, ingestion_service):
        """Test that missing date mapping raises error"""
        mapping = {
            "Description": "description",
            "Amount": "amount",
        }
        
        with pytest.raises(ValidationError, match="must include 'date'"):
            ingestion_service.validate_column_mapping(mapping)

    def test_validate_missing_amount_raises_error(self, ingestion_service):
        """Test that missing amount mapping raises error"""
        mapping = {
            "Date": "date",
            "Description": "description",
        }
        
        with pytest.raises(ValidationError, match="must include 'amount'"):
            ingestion_service.validate_column_mapping(mapping)

    def test_validate_invalid_field_name_raises_error(self, ingestion_service):
        """Test that invalid field name raises error"""
        mapping = {
            "Date": "date",
            "Amount": "amount",
            "InvalidField": "invalid_field",
        }
        
        with pytest.raises(ValidationError, match="Invalid field name"):
            ingestion_service.validate_column_mapping(mapping)
