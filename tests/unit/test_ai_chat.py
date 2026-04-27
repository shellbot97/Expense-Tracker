"""
Unit tests for AI chat service
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.services.ai_chat_service import AIChatService
from src.models.category import Category
from src.models.transaction import Transaction
from tests.fixtures.database_fixtures import (
    test_db,
    test_user,
    test_category,
    test_source,
)


def test_chat_permission_disabled(test_db, test_user):
    """Test chat respects disabled AI permission"""
    service = AIChatService(test_db)

    # Mock permission check to return False
    with patch.object(
        service.privacy_service, "check_permission", return_value=False
    ):
        result = service.chat(test_user.id, "How much did I spend last month?")

    assert result is None


@patch("requests.post")
def test_chat_with_ollama(mock_post, test_db, test_user, test_category, test_source):
    """Test successful chat with Ollama"""
    # Create test transactions
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now() - timedelta(days=15),
        description="Whole Foods",
        amount=5499,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = AIChatService(test_db)

    # Mock Ollama response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": json.dumps(
            {
                "answer": "You spent $54.99 on groceries in the last 30 days.",
                "data": {"total": 54.99, "category": "Groceries"},
            }
        )
    }
    mock_post.return_value = mock_response

    # Mock permission check
    with patch.object(
        service.privacy_service, "check_permission", return_value=True
    ):
        result = service.chat(
            test_user.id, "How much did I spend on groceries last 30 days?"
        )

    assert result is not None
    assert result["response"] == "You spent $54.99 on groceries in the last 30 days."
    assert result["data"]["total"] == 54.99
    assert result["method"] == "ai"


@patch("requests.post")
def test_chat_ollama_error(mock_post, test_db, test_user, test_category, test_source):
    """Test chat gracefully handles Ollama errors"""
    # Create test transaction so we get past data check
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Test",
        amount=1000,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = AIChatService(test_db)

    # Mock Ollama error
    mock_response = Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    with patch.object(
        service.privacy_service, "check_permission", return_value=True
    ):
        result = service.chat(test_user.id, "How much did I spend?")

    assert result is None


@patch("requests.post")
def test_chat_no_data(mock_post, test_db, test_user):
    """Test chat with no transaction data"""
    service = AIChatService(test_db)

    with patch.object(
        service.privacy_service, "check_permission", return_value=True
    ):
        result = service.chat(test_user.id, "How much did I spend last month?")

    assert result is not None
    assert result["method"] == "fallback"
    assert "don't have enough data" in result["response"]


@patch("requests.post")
def test_chat_invalid_json_response(
    mock_post, test_db, test_user, test_category, test_source
):
    """Test chat handles invalid JSON from AI"""
    # Create test transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Test",
        amount=1000,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = AIChatService(test_db)

    # Mock invalid JSON response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Not valid JSON at all"}
    mock_post.return_value = mock_response

    with patch.object(
        service.privacy_service, "check_permission", return_value=True
    ):
        result = service.chat(test_user.id, "Summary?")

    # Should fallback to text response
    assert result is not None
    assert result["response"] == "Not valid JSON at all"
    assert result["method"] == "ai"


@patch("requests.post")
def test_chat_connection_error(mock_post, test_db, test_user, test_category, test_source):
    """Test chat handles connection errors"""
    # Create test transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Test",
        amount=1000,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = AIChatService(test_db)

    # Mock connection error
    mock_post.side_effect = Exception("Connection refused")

    with patch.object(
        service.privacy_service, "check_permission", return_value=True
    ):
        result = service.chat(test_user.id, "Summary?")

    assert result is None


@patch("requests.post")
def test_chat_with_conversation_history(
    mock_post, test_db, test_user, test_category, test_source
):
    """Test chat with conversation history"""
    # Create test transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Coffee Shop",
        amount=450,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = AIChatService(test_db)

    # Mock Ollama response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": json.dumps({"answer": "Yes, you spent $4.50 at a coffee shop."})
    }
    mock_post.return_value = mock_response

    conversation_history = [
        {"role": "user", "content": "What did I spend today?"},
        {"role": "assistant", "content": "You spent $4.50."},
        {"role": "user", "content": "Where?"},
    ]

    with patch.object(
        service.privacy_service, "check_permission", return_value=True
    ):
        result = service.chat(
            test_user.id, "Where?", conversation_history=conversation_history
        )

    assert result is not None
    assert "coffee shop" in result["response"].lower()


def test_extract_date_range_last_month(test_db):
    """Test date range extraction for 'last month'"""
    service = AIChatService(test_db)

    result = service._extract_date_range("How much did I spend last month?")

    assert result is not None
    assert "start" in result
    assert "end" in result
    # Should be previous calendar month
    now = datetime.now()
    expected_end = now.replace(day=1, hour=0, minute=0, second=0) - timedelta(days=1)
    assert result["end"].month == expected_end.month


def test_extract_date_range_this_month(test_db):
    """Test date range extraction for 'this month'"""
    service = AIChatService(test_db)

    result = service._extract_date_range("What's my spending this month?")

    assert result is not None
    now = datetime.now()
    assert result["start"].day == 1
    assert result["start"].month == now.month


def test_extract_date_range_last_week(test_db):
    """Test date range extraction for 'last week'"""
    service = AIChatService(test_db)

    result = service._extract_date_range("Show me spending from last week")

    assert result is not None
    now = datetime.now()
    expected_start = now - timedelta(days=7)
    assert abs((result["start"] - expected_start).days) <= 1


def test_extract_date_range_this_year(test_db):
    """Test date range extraction for 'this year'"""
    service = AIChatService(test_db)

    result = service._extract_date_range("What did I spend this year?")

    assert result is not None
    now = datetime.now()
    assert result["start"].year == now.year
    assert result["start"].month == 1
    assert result["start"].day == 1


def test_extract_date_range_no_match(test_db):
    """Test date range extraction with no time reference"""
    service = AIChatService(test_db)

    result = service._extract_date_range("What's my total spending?")

    assert result is None  # All time


@patch("requests.get")
def test_is_available_true(mock_get, test_db):
    """Test Ollama availability check (available)"""
    service = AIChatService(test_db)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    assert service.is_available() is True


@patch("requests.get")
def test_is_available_false(mock_get, test_db):
    """Test Ollama availability check (unavailable)"""
    service = AIChatService(test_db)

    mock_get.side_effect = Exception("Connection refused")

    assert service.is_available() is False


def test_conversation_summary_empty(test_db):
    """Test conversation summary with no history"""
    service = AIChatService(test_db)

    summary = service.get_conversation_summary([])

    assert summary == "No conversation yet"


def test_conversation_summary_with_messages(test_db):
    """Test conversation summary with messages"""
    service = AIChatService(test_db)

    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How much did I spend?"},
    ]

    summary = service.get_conversation_summary(history)

    assert "Hello" in summary
    assert "Hi there!" in summary
    assert "How much did I spend?" in summary


def test_build_user_context(test_db, test_user, test_category, test_source):
    """Test building user context from transactions"""
    # Create test transactions
    t1 = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now() - timedelta(days=5),
        description="Grocery Store",
        amount=5000,
        transaction_type="expense",
    )
    t2 = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now() - timedelta(days=3),
        description="Gas Station",
        amount=3500,
        transaction_type="expense",
    )
    test_db.add_all([t1, t2])
    test_db.commit()

    service = AIChatService(test_db)

    context = service._build_user_context(test_user.id, "How much last week?")

    assert context is not None
    assert context["transaction_count"] == 2
    assert context["total_expenses"] == 8500
    assert len(context["top_categories"]) > 0
