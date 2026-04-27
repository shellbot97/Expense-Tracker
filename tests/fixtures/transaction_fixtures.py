"""
Test fixtures for transaction tests
"""

import pytest
from datetime import date, timedelta


@pytest.fixture
def valid_transaction_data():
    """Valid transaction data for testing"""
    return {
        "description": "Grocery shopping at Whole Foods",
        "amount": 8543,  # $85.43 in cents
        "transaction_type": "expense",
        "transaction_date": date.today(),  # Changed from .isoformat()
        "notes": "Weekly groceries",
    }


@pytest.fixture
def valid_transaction_with_category_source(valid_transaction_data):
    """Transaction data with category and source IDs"""
    data = valid_transaction_data.copy()
    data.update({
        "category_id": 1,
        "source_id": 1,
    })
    return data


@pytest.fixture
def invalid_transaction_data():
    """Invalid transaction data for testing"""
    return {
        "description": "",  # Empty description
        "amount": -100,  # Negative amount
        "transaction_type": "invalid_type",
        "transaction_date": "invalid_date",
    }


@pytest.fixture
def transaction_filter_params():
    """Filter parameters for transaction queries"""
    return {
        "start_date": (date.today() - timedelta(days=30)).isoformat(),
        "end_date": date.today().isoformat(),
        "transaction_type": "expense",
        "min_amount": 1000,
        "max_amount": 10000,
    }
