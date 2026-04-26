"""
Test fixtures for user-related tests
"""

import pytest
from datetime import datetime


@pytest.fixture
def valid_user_data():
    """Valid user registration data"""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "SecureP@ssw0rd123",
    }


@pytest.fixture
def valid_user_data_2():
    """Second valid user for testing"""
    return {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "AnotherSecure123!",
    }


@pytest.fixture
def invalid_user_data():
    """Invalid user data for testing validation"""
    return {
        "username": "",  # Empty username
        "email": "not-an-email",  # Invalid email
        "password": "123",  # Too short
    }


@pytest.fixture
def user_login_data():
    """Login credentials"""
    return {"username": "testuser", "password": "SecureP@ssw0rd123"}


@pytest.fixture
def invalid_login_data():
    """Invalid login credentials"""
    return {"username": "testuser", "password": "WrongPassword"}
