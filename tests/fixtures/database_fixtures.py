"""
Database and model fixtures for tests
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.database import Base
from src.models.user import User
from src.models.category import Category
from src.models.source import Source
from src.models.transaction import Transaction
from src.models.budget import Budget  # Import all models to resolve relationships


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary database for testing"""
    # Create temporary SQLite database
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    from src.services.auth_service import AuthService
    
    auth_service = AuthService(test_db)
    user = auth_service.register_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123!"
    )
    test_db.commit()
    test_db.refresh(user)
    
    return user


@pytest.fixture
def test_category(test_db, test_user):
    """Create a test category"""
    category = Category(
        user_id=test_user.id,
        name="Groceries",
        category_type="expense",
        description="Food and household items",
        is_active=True,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    
    return category


@pytest.fixture
def test_source(test_db, test_user):
    """Create a test source"""
    source = Source(
        user_id=test_user.id,
        name="Chase Checking",
        source_type="bank_account",
        description="Primary checking account",
        is_active=True,
    )
    test_db.add(source)
    test_db.commit()
    test_db.refresh(source)
    
    return source
