"""
Unit tests for AI categorization service
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.ai_categorization_service import AICategorizationService
from src.models.category import Category
from src.models.transaction import Transaction
from tests.fixtures.database_fixtures import test_db, test_user, test_category, test_source


@pytest.fixture
def ai_service(test_db):
    """Create AI categorization service"""
    return AICategorizationService(test_db)


@pytest.fixture
def test_categories(test_db, test_user):
    """Create multiple test categories"""
    categories = [
        Category(
            user_id=test_user.id,
            name="Groceries",
            category_type="expense",
            description="Food and household items",
            is_active=True,
        ),
        Category(
            user_id=test_user.id,
            name="Transportation",
            category_type="expense",
            description="Uber, gas, parking",
            is_active=True,
        ),
        Category(
            user_id=test_user.id,
            name="Dining",
            category_type="expense",
            description="Restaurants and cafes",
            is_active=True,
        ),
    ]
    
    for cat in categories:
        test_db.add(cat)
    test_db.commit()
    
    for cat in categories:
        test_db.refresh(cat)
    
    return categories


@pytest.fixture
def test_transaction(test_db, test_user, test_source, test_category):
    """Create a test transaction"""
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=None,  # Uncategorized
        transaction_date=datetime(2024, 1, 15),
        amount=4599,  # $45.99
        transaction_type="expense",
        description="Whole Foods Market",
    )
    test_db.add(transaction)
    test_db.commit()
    test_db.refresh(transaction)
    
    return transaction


def test_categorize_permission_disabled(ai_service, test_user, test_categories):
    """Test that AI categorization respects privacy permissions"""
    # Privacy default: AI categorization disabled
    result = ai_service.categorize_transaction(
        user_id=test_user.id,
        description="Whole Foods",
        amount=5000,
        transaction_type="expense",
    )
    
    # Should return None when disabled
    assert result is None


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
@patch('requests.post')
def test_categorize_with_ollama(mock_post, mock_permission, ai_service, test_user, test_categories):
    """Test AI categorization with successful Ollama response"""
    # Enable AI categorization
    mock_permission.return_value = True
    
    # Mock Ollama API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": json.dumps({
            "category_name": "Groceries",
            "confidence": 0.95,
            "reasoning": "Transaction at Whole Foods is clearly a grocery store"
        })
    }
    mock_post.return_value = mock_response
    
    # Test categorization
    result = ai_service.categorize_transaction(
        user_id=test_user.id,
        description="Whole Foods Market",
        amount=5000,
        transaction_type="expense",
    )
    
    assert result is not None
    assert result["category_name"] == "Groceries"
    assert result["confidence"] == 0.95
    assert result["method"] == "ai"
    assert "reasoning" in result
    assert result["category_id"] == test_categories[0].id


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
@patch('requests.post')
def test_categorize_ollama_error(mock_post, mock_permission, ai_service, test_user, test_categories):
    """Test graceful degradation when Ollama is unavailable"""
    # Enable AI categorization
    mock_permission.return_value = True
    
    # Mock Ollama API error
    mock_response = Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response
    
    # Should return None on error
    result = ai_service.categorize_transaction(
        user_id=test_user.id,
        description="Whole Foods",
        amount=5000,
        transaction_type="expense",
    )
    
    assert result is None


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
@patch('requests.post')
def test_categorize_invalid_json_response(mock_post, mock_permission, ai_service, test_user, test_categories):
    """Test handling of invalid AI response"""
    # Enable AI categorization
    mock_permission.return_value = True
    
    # Mock Ollama with invalid JSON
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "This is not valid JSON"
    }
    mock_post.return_value = mock_response
    
    # Should return None on parse error
    result = ai_service.categorize_transaction(
        user_id=test_user.id,
        description="Whole Foods",
        amount=5000,
        transaction_type="expense",
    )
    
    assert result is None


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
@patch('requests.post')
def test_categorize_category_not_found(mock_post, mock_permission, ai_service, test_user, test_categories):
    """Test when AI suggests non-existent category"""
    # Enable AI categorization
    mock_permission.return_value = True
    
    # Mock Ollama suggesting invalid category
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": json.dumps({
            "category_name": "NonExistent Category",
            "confidence": 0.8,
            "reasoning": "Some reasoning"
        })
    }
    mock_post.return_value = mock_response
    
    # Should return None when category not found
    result = ai_service.categorize_transaction(
        user_id=test_user.id,
        description="Some transaction",
        amount=5000,
        transaction_type="expense",
    )
    
    assert result is None


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
@patch('requests.post')
def test_categorize_no_categories_available(mock_post, mock_permission, ai_service, test_user):
    """Test categorization with no categories"""
    # Enable AI categorization
    mock_permission.return_value = True
    
    # Should return None when no categories exist
    result = ai_service.categorize_transaction(
        user_id=test_user.id,
        description="Whole Foods",
        amount=5000,
        transaction_type="expense",
    )
    
    assert result is None


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
@patch('requests.post')
def test_categorize_connection_error(mock_post, mock_permission, ai_service, test_user, test_categories):
    """Test handling of network errors"""
    # Enable AI categorization
    mock_permission.return_value = True
    
    # Mock connection error
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    # Should return None on connection error
    result = ai_service.categorize_transaction(
        user_id=test_user.id,
        description="Whole Foods",
        amount=5000,
        transaction_type="expense",
    )
    
    assert result is None


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
def test_bulk_categorize_permission_disabled(mock_permission, ai_service, test_user, test_transaction):
    """Test bulk categorization with permissions disabled"""
    # Disable AI categorization
    mock_permission.return_value = False
    
    results = ai_service.bulk_categorize(
        user_id=test_user.id,
        transaction_ids=[test_transaction.id],
    )
    
    assert results[test_transaction.id] is None


@patch('src.services.ai_categorization_service.PrivacyService.check_permission')
@patch('requests.post')
def test_bulk_categorize_multiple_transactions(
    mock_post,
    mock_permission,
    ai_service,
    test_user,
    test_source,
    test_categories,
    test_db
):
    """Test bulk categorization of multiple transactions"""
    # Enable AI categorization
    mock_permission.return_value = True
    
    # Create multiple transactions
    transactions = [
        Transaction(
            user_id=test_user.id,
            source_id=test_source.id,
            category_id=None,
            transaction_date=datetime(2024, 1, 15),
            amount=5000,
            transaction_type="expense",
            description="Whole Foods",
        ),
        Transaction(
            user_id=test_user.id,
            source_id=test_source.id,
            category_id=None,
            transaction_date=datetime(2024, 1, 16),
            amount=2500,
            transaction_type="expense",
            description="Uber ride",
        ),
    ]
    
    for txn in transactions:
        test_db.add(txn)
    test_db.commit()
    
    for txn in transactions:
        test_db.refresh(txn)
    
    # Mock Ollama responses
    def mock_post_response(*args, **kwargs):
        prompt = kwargs.get("json", {}).get("prompt", "")
        
        if "Whole Foods" in prompt:
            response_data = {
                "category_name": "Groceries",
                "confidence": 0.95,
                "reasoning": "Grocery store"
            }
        elif "Uber" in prompt:
            response_data = {
                "category_name": "Transportation",
                "confidence": 0.90,
                "reasoning": "Ride sharing"
            }
        else:
            response_data = {
                "category_name": "Other",
                "confidence": 0.5,
                "reasoning": "Unknown"
            }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps(response_data)
        }
        return mock_response
    
    mock_post.side_effect = mock_post_response
    
    # Test bulk categorization
    results = ai_service.bulk_categorize(
        user_id=test_user.id,
        transaction_ids=[txn.id for txn in transactions],
    )
    
    assert len(results) == 2
    assert results[transactions[0].id]["category_name"] == "Groceries"
    assert results[transactions[1].id]["category_name"] == "Transportation"


@patch('requests.get')
def test_is_available_true(mock_get, ai_service):
    """Test checking if Ollama is available"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    assert ai_service.is_available() is True


@patch('requests.get')
def test_is_available_false(mock_get, ai_service):
    """Test checking if Ollama is unavailable"""
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()
    
    assert ai_service.is_available() is False


@patch('requests.get')
def test_get_model_info(mock_get, ai_service):
    """Test getting model information"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {
                "name": "llama3:latest",
                "size": 4661224192,
                "modified_at": "2024-01-15T10:30:00Z"
            }
        ]
    }
    mock_get.return_value = mock_response
    
    info = ai_service.get_model_info()
    
    assert info is not None
    assert info["name"] == "llama3:latest"
    assert info["available"] is True


@patch('requests.get')
def test_get_model_info_unavailable(mock_get, ai_service):
    """Test getting model info when Ollama is unavailable"""
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()
    
    info = ai_service.get_model_info()
    
    assert info is None
