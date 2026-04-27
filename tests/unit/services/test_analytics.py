"""
Unit tests for analytics service
"""

import pytest
from datetime import date, datetime, timedelta
from src.services.analytics_service import AnalyticsService
from src.models.user import User
from src.models.category import Category
from src.models.source import Source
from src.models.transaction import Transaction


@pytest.fixture
def db_session(tmp_path):
    """Create a temporary database for testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.config.database import Base
    
    # Import all models to ensure they're registered
    from src.models.user import User
    from src.models.category import Category
    from src.models.source import Source
    from src.models.transaction import Transaction
    from src.models.budget import Budget

    # Create temporary SQLite database
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    
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
def analytics_service(db_session):
    """Create analytics service instance"""
    return AnalyticsService(db_session)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="analytics@test.com",
        username="analytics_user",
        hashed_password="hashed",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_categories(db_session, test_user):
    """Create test categories"""
    categories = [
        Category(user_id=test_user.id, name="Food", category_type="expense"),
        Category(user_id=test_user.id, name="Transport", category_type="expense"),
        Category(user_id=test_user.id, name="Salary", category_type="income"),
    ]
    db_session.add_all(categories)
    db_session.commit()
    for cat in categories:
        db_session.refresh(cat)
    return categories


@pytest.fixture
def test_sources(db_session, test_user):
    """Create test sources"""
    sources = [
        Source(user_id=test_user.id, name="Checking", source_type="bank_account"),
        Source(user_id=test_user.id, name="Credit Card", source_type="credit_card"),
    ]
    db_session.add_all(sources)
    db_session.commit()
    for src in sources:
        db_session.refresh(src)
    return sources


@pytest.fixture
def test_transactions(db_session, test_user, test_categories, test_sources):
    """Create test transactions"""
    transactions = [
        # January expenses
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[0].id,  # Food
            source_id=test_sources[0].id,
            transaction_date=date(2024, 1, 5),
            amount=5000,  # $50.00
            transaction_type="expense",
            description="Grocery Store",
        ),
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[0].id,  # Food
            source_id=test_sources[1].id,
            transaction_date=date(2024, 1, 15),
            amount=3000,  # $30.00
            transaction_type="expense",
            description="Restaurant",
        ),
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[1].id,  # Transport
            source_id=test_sources[0].id,
            transaction_date=date(2024, 1, 20),
            amount=2000,  # $20.00
            transaction_type="expense",
            description="Uber",
        ),
        # February expenses
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[0].id,  # Food
            source_id=test_sources[0].id,
            transaction_date=date(2024, 2, 5),
            amount=6000,  # $60.00
            transaction_type="expense",
            description="Grocery Store",
        ),
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[1].id,  # Transport
            source_id=test_sources[0].id,
            transaction_date=date(2024, 2, 10),
            amount=1500,  # $15.00
            transaction_type="expense",
            description="Gas Station",
        ),
        # Income
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[2].id,  # Salary
            source_id=test_sources[0].id,
            transaction_date=date(2024, 1, 31),
            amount=500000,  # $5000.00
            transaction_type="income",
            description="Monthly Salary",
        ),
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[2].id,  # Salary
            source_id=test_sources[0].id,
            transaction_date=date(2024, 2, 28),
            amount=500000,  # $5000.00
            transaction_type="income",
            description="Monthly Salary",
        ),
        # Anomaly - very high expense
        Transaction(
            user_id=test_user.id,
            category_id=test_categories[0].id,
            source_id=test_sources[0].id,
            transaction_date=date(2024, 2, 20),
            amount=50000,  # $500.00 - much higher than usual
            transaction_type="expense",
            description="Electronics Store",
        ),
    ]
    db_session.add_all(transactions)
    db_session.commit()
    return transactions


class TestSpendingByCategory:
    """Test spending by category aggregation"""
    
    def test_spending_by_category_all_time(self, analytics_service, test_user, test_transactions):
        """Test aggregating all expenses by category"""
        results = analytics_service.get_spending_by_category(
            user_id=test_user.id,
            transaction_type="expense",
        )
        
        assert len(results) == 2  # Food and Transport
        
        # Should be sorted by total descending
        assert results[0]["category_name"] == "Food"
        assert results[0]["total_amount"] == 64000  # 50+30+60+500
        assert results[0]["count"] == 4
        
        assert results[1]["category_name"] == "Transport"
        assert results[1]["total_amount"] == 3500  # 20+15
        assert results[1]["count"] == 2
    
    def test_spending_by_category_date_range(self, analytics_service, test_user, test_transactions):
        """Test aggregating expenses by category with date range"""
        results = analytics_service.get_spending_by_category(
            user_id=test_user.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            transaction_type="expense",
        )
        
        # Only January transactions
        food_result = next(r for r in results if r["category_name"] == "Food")
        assert food_result["total_amount"] == 8000  # 50+30
        assert food_result["count"] == 2
        
        transport_result = next(r for r in results if r["category_name"] == "Transport")
        assert transport_result["total_amount"] == 2000  # 20
        assert transport_result["count"] == 1
    
    def test_spending_by_category_income(self, analytics_service, test_user, test_transactions):
        """Test aggregating income by category"""
        results = analytics_service.get_spending_by_category(
            user_id=test_user.id,
            transaction_type="income",
        )
        
        assert len(results) == 1
        assert results[0]["category_name"] == "Salary"
        assert results[0]["total_amount"] == 1000000  # 5000+5000
        assert results[0]["count"] == 2


class TestSpendingBySource:
    """Test spending by source aggregation"""
    
    def test_spending_by_source(self, analytics_service, test_user, test_transactions):
        """Test aggregating expenses by source"""
        results = analytics_service.get_spending_by_source(
            user_id=test_user.id,
            transaction_type="expense",
        )
        
        assert len(results) == 2
        
        # Checking account should have more
        checking = next(r for r in results if r["source_name"] == "Checking")
        assert checking["count"] == 5
        
        credit_card = next(r for r in results if r["source_name"] == "Credit Card")
        assert credit_card["count"] == 1
        assert credit_card["total_amount"] == 3000


class TestSpendingTrends:
    """Test time-series spending trends"""
    
    def test_trends_by_month(self, analytics_service, test_user, test_transactions):
        """Test monthly spending trends"""
        results = analytics_service.get_spending_trends(
            user_id=test_user.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 29),
            granularity="month",
            transaction_type="expense",
        )
        
        assert len(results) == 2
        assert results[0]["period"] == "2024-01"
        assert results[0]["total_amount"] == 10000  # 50+30+20
        assert results[0]["count"] == 3
        
        assert results[1]["period"] == "2024-02"
        assert results[1]["total_amount"] == 57500  # 60+15+500
        assert results[1]["count"] == 3
    
    def test_trends_by_day(self, analytics_service, test_user, test_transactions):
        """Test daily spending trends"""
        results = analytics_service.get_spending_trends(
            user_id=test_user.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            granularity="day",
            transaction_type="expense",
        )
        
        assert len(results) == 3  # 3 different days in January
    
    def test_trends_invalid_granularity(self, analytics_service, test_user):
        """Test invalid granularity raises error"""
        from src.utils.exceptions import ValidationError
        
        with pytest.raises(ValidationError) as exc:
            analytics_service.get_spending_trends(
                user_id=test_user.id,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                granularity="invalid",
            )
        assert "Invalid granularity" in str(exc.value)


class TestPeriodComparison:
    """Test period-to-period comparison"""
    
    def test_month_over_month_comparison(self, analytics_service, test_user, test_transactions):
        """Test comparing two months"""
        result = analytics_service.get_period_comparison(
            user_id=test_user.id,
            current_start=date(2024, 2, 1),
            current_end=date(2024, 2, 29),
            previous_start=date(2024, 1, 1),
            previous_end=date(2024, 1, 31),
            transaction_type="expense",
        )
        
        assert result["current_period"]["total"] == 57500  # Feb
        assert result["previous_period"]["total"] == 10000  # Jan
        assert result["change"] == 47500  # Increase
        assert result["change_percent"] == 475.0  # 475% increase
    
    def test_comparison_with_zero_previous(self, analytics_service, test_user, test_transactions):
        """Test comparison when previous period has no transactions"""
        result = analytics_service.get_period_comparison(
            user_id=test_user.id,
            current_start=date(2024, 1, 1),
            current_end=date(2024, 1, 31),
            previous_start=date(2023, 12, 1),
            previous_end=date(2023, 12, 31),
            transaction_type="expense",
        )
        
        assert result["current_period"]["total"] == 10000
        assert result["previous_period"]["total"] == 0
        assert result["change_percent"] == 0  # Avoid division by zero


class TestTopMerchants:
    """Test top merchants analysis"""
    
    def test_top_merchants(self, analytics_service, test_user, test_transactions):
        """Test getting top merchants by spending"""
        results = analytics_service.get_top_merchants(
            user_id=test_user.id,
            transaction_type="expense",
            limit=5,
        )
        
        assert len(results) <= 5
        
        # Electronics should be top (largest single transaction)
        assert results[0]["description"] == "Electronics Store"
        assert results[0]["total_amount"] == 50000
        assert results[0]["count"] == 1
    
    def test_top_merchants_with_date_range(self, analytics_service, test_user, test_transactions):
        """Test top merchants within date range"""
        results = analytics_service.get_top_merchants(
            user_id=test_user.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            transaction_type="expense",
            limit=10,
        )
        
        # Should only include January transactions
        descriptions = [r["description"] for r in results]
        assert "Electronics Store" not in descriptions  # Feb transaction


class TestAnomalyDetection:
    """Test anomaly detection"""
    
    def test_detect_anomalies(self, analytics_service, test_user, test_transactions):
        """Test detecting unusual spending"""
        results = analytics_service.detect_anomalies(
            user_id=test_user.id,
            lookback_days=90,
            threshold_multiplier=2.0,
        )
        
        # Should detect the $500 electronics purchase as anomaly
        assert len(results) >= 1
        electronics = next((r for r in results if "Electronics" in r["description"]), None)
        assert electronics is not None
        assert electronics["amount"] == 50000
    
    def test_anomaly_detection_insufficient_data(self, analytics_service, test_user, db_session):
        """Test anomaly detection with insufficient data"""
        # Create new user with no transactions
        new_user = User(
            email="newuser@test.com",
            username="newuser",
            hashed_password="hashed",
        )
        db_session.add(new_user)
        db_session.commit()
        
        results = analytics_service.detect_anomalies(
            user_id=new_user.id,
            lookback_days=90,
        )
        
        assert results == []  # No anomalies with no data


class TestSummaryStats:
    """Test summary statistics"""
    
    def test_summary_stats_all_time(self, analytics_service, test_user, test_transactions):
        """Test getting summary stats for all time"""
        stats = analytics_service.get_summary_stats(user_id=test_user.id)
        
        assert stats["total_expenses"] == 67500  # Sum of all expenses
        assert stats["total_income"] == 1000000  # Sum of all income
        assert stats["net_savings"] == 932500  # Income - Expenses
        assert stats["transaction_count"] == 8  # Total transactions
    
    def test_summary_stats_date_range(self, analytics_service, test_user, test_transactions):
        """Test summary stats within date range"""
        stats = analytics_service.get_summary_stats(
            user_id=test_user.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        
        assert stats["total_expenses"] == 10000  # Jan expenses
        assert stats["total_income"] == 500000  # Jan income
        assert stats["net_savings"] == 490000
        assert stats["transaction_count"] == 4  # Jan transactions
    
    def test_summary_stats_no_transactions(self, analytics_service, test_user, db_session):
        """Test summary stats with no transactions"""
        # Create new user
        new_user = User(
            email="empty@test.com",
            username="empty_user",
            hashed_password="hashed",
        )
        db_session.add(new_user)
        db_session.commit()
        
        stats = analytics_service.get_summary_stats(user_id=new_user.id)
        
        assert stats["total_expenses"] == 0
        assert stats["total_income"] == 0
        assert stats["net_savings"] == 0
        assert stats["transaction_count"] == 0
