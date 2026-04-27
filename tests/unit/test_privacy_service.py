"""
Unit tests for privacy service
"""

import pytest
from datetime import datetime
from src.services.privacy_service import PrivacyService
from src.models.user import User
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.source import Source
from src.utils.exceptions import NotFoundError, ValidationError
from tests.fixtures.database_fixtures import test_db, test_user, test_category, test_source


def test_get_user_preferences(test_db, test_user):
    """Test getting user privacy preferences"""
    service = PrivacyService(test_db)
    
    preferences = service.get_user_preferences(test_user.id)
    
    assert preferences["ai_categorization_enabled"] is False
    assert preferences["ai_chat_enabled"] is False
    assert preferences["data_export_enabled"] is True
    assert preferences["analytics_enabled"] is True
    assert "last_updated" in preferences


def test_get_preferences_user_not_found(test_db):
    """Test getting preferences for non-existent user"""
    service = PrivacyService(test_db)
    
    with pytest.raises(NotFoundError):
        service.get_user_preferences(999)


def test_update_preferences(test_db, test_user):
    """Test updating user preferences"""
    service = PrivacyService(test_db)
    
    updated = service.update_preferences(
        user_id=test_user.id,
        ai_categorization_enabled=True,
        ai_chat_enabled=True,
    )
    
    assert updated["user_id"] == test_user.id
    assert updated["ai_categorization_enabled"] is True
    assert updated["ai_chat_enabled"] is True
    assert updated["data_export_enabled"] is True  # Default
    assert updated["analytics_enabled"] is True  # Default


def test_update_preferences_partial(test_db, test_user):
    """Test partial preference update"""
    service = PrivacyService(test_db)
    
    updated = service.update_preferences(
        user_id=test_user.id,
        ai_categorization_enabled=True,
    )
    
    assert updated["ai_categorization_enabled"] is True
    assert updated["ai_chat_enabled"] is False  # Not updated
    assert updated["data_export_enabled"] is True


def test_update_preferences_disable_features(test_db, test_user):
    """Test disabling features"""
    service = PrivacyService(test_db)
    
    updated = service.update_preferences(
        user_id=test_user.id,
        ai_categorization_enabled=False,
        analytics_enabled=False,
    )
    
    assert updated["ai_categorization_enabled"] is False
    assert updated["analytics_enabled"] is False


def test_update_preferences_user_not_found(test_db):
    """Test updating preferences for non-existent user"""
    service = PrivacyService(test_db)
    
    with pytest.raises(NotFoundError):
        service.update_preferences(
            user_id=999,
            ai_categorization_enabled=True,
        )


def test_check_permission_ai_categorization(test_db, test_user):
    """Test checking AI categorization permission"""
    service = PrivacyService(test_db)
    
    # Default should be False (privacy-first)
    has_permission = service.check_permission(test_user.id, "ai_categorization")
    assert has_permission is False


def test_check_permission_ai_chat(test_db, test_user):
    """Test checking AI chat permission"""
    service = PrivacyService(test_db)
    
    # Default should be False (privacy-first)
    has_permission = service.check_permission(test_user.id, "ai_chat")
    assert has_permission is False


def test_check_permission_data_export(test_db, test_user):
    """Test checking data export permission"""
    service = PrivacyService(test_db)
    
    # Default should be True (local feature)
    has_permission = service.check_permission(test_user.id, "data_export")
    assert has_permission is True


def test_check_permission_analytics(test_db, test_user):
    """Test checking analytics permission"""
    service = PrivacyService(test_db)
    
    # Default should be True (local feature)
    has_permission = service.check_permission(test_user.id, "analytics")
    assert has_permission is True


def test_check_permission_invalid(test_db, test_user):
    """Test checking invalid permission"""
    service = PrivacyService(test_db)
    
    with pytest.raises(ValidationError):
        service.check_permission(test_user.id, "invalid_permission")


def test_check_permission_user_not_found(test_db):
    """Test checking permission for non-existent user"""
    service = PrivacyService(test_db)
    
    with pytest.raises(NotFoundError):
        service.check_permission(999, "ai_categorization")


def test_anonymize_description_card_numbers(test_db):
    """Test anonymizing card numbers"""
    service = PrivacyService(test_db)
    
    # Full card number
    result = service.anonymize_description("Payment with 4532-1234-5678-9012")
    assert "[CARD]" in result
    assert "4532" not in result
    
    # Partial card
    result = service.anonymize_description("Card ending ****1234")
    assert "[CARD]" in result
    assert "1234" not in result


def test_anonymize_description_phone_numbers(test_db):
    """Test anonymizing phone numbers"""
    service = PrivacyService(test_db)
    
    # Various formats with separators (without separators would match account pattern)
    result = service.anonymize_description("Call (555) 123-4567")
    assert "[PHONE]" in result
    assert "555" not in result
    
    result = service.anonymize_description("Phone: 555-123-4567")
    assert "[PHONE]" in result
    
    result = service.anonymize_description("Contact (555)123-4567")
    assert "[PHONE]" in result


def test_anonymize_description_emails(test_db):
    """Test anonymizing email addresses"""
    service = PrivacyService(test_db)
    
    result = service.anonymize_description("Email john@example.com for info")
    assert "[EMAIL]" in result
    assert "john@example.com" not in result


def test_anonymize_description_account_numbers(test_db):
    """Test anonymizing account numbers"""
    service = PrivacyService(test_db)
    
    result = service.anonymize_description("Account 12345678901")
    assert "[ACCOUNT]" in result
    assert "12345678" not in result


def test_anonymize_description_multiple(test_db):
    """Test anonymizing multiple PII types"""
    service = PrivacyService(test_db)
    
    description = "Payment from 4532123456789012 to john@example.com, call 555-123-4567"
    result = service.anonymize_description(description)
    
    assert "[CARD]" in result
    assert "[EMAIL]" in result
    assert "[PHONE]" in result
    assert "4532" not in result
    assert "john@example.com" not in result
    assert "555" not in result


def test_anonymize_description_no_pii(test_db):
    """Test anonymizing description with no PII"""
    service = PrivacyService(test_db)
    
    description = "Grocery shopping at Whole Foods"
    result = service.anonymize_description(description)
    
    # Should remain unchanged
    assert result == description


def test_get_data_summary(test_db, test_user, test_category, test_source):
    """Test getting user data summary"""
    # Create some transactions
    transaction1 = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime(2024, 1, 15),
        amount=1000,
        transaction_type="expense",
        description="Test 1",
    )
    transaction2 = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime(2024, 1, 16),
        amount=2000,
        transaction_type="expense",
        description="Test 2",
    )
    test_db.add_all([transaction1, transaction2])
    test_db.commit()
    
    service = PrivacyService(test_db)
    summary = service.get_data_summary(test_user.id)
    
    assert summary["user_id"] == test_user.id
    assert summary["username"] == test_user.username
    assert summary["email"] == test_user.email
    assert "account_created" in summary
    assert summary["data_summary"]["transactions"] == 2
    assert summary["data_summary"]["categories"] >= 1
    assert summary["data_summary"]["sources"] >= 1
    assert "privacy_notice" in summary


def test_get_data_summary_empty(test_db, test_user):
    """Test getting data summary with no data"""
    service = PrivacyService(test_db)
    summary = service.get_data_summary(test_user.id)
    
    assert summary["user_id"] == test_user.id
    assert summary["data_summary"]["transactions"] == 0


def test_get_data_summary_user_not_found(test_db):
    """Test getting summary for non-existent user"""
    service = PrivacyService(test_db)
    
    with pytest.raises(NotFoundError):
        service.get_data_summary(999)
