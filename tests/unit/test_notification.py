"""
Unit tests for notification service
"""

import pytest
from datetime import datetime, timedelta
from src.services.notification_service import NotificationService
from src.models.category import Category
from src.models.transaction import Transaction
from src.utils.exceptions import NotFoundError, ValidationError
from tests.fixtures.database_fixtures import (
    test_db,
    test_user,
    test_category,
    test_source,
)


def test_check_uncategorized_transactions_none(test_db, test_user, test_category, test_source):
    """Test no uncategorized transactions"""
    # Create categorized transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Grocery Store",
        amount=5000,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_uncategorized_transactions(test_user.id)

    assert len(notifications) == 0


def test_check_uncategorized_transactions_found(test_db, test_user, test_source):
    """Test finding uncategorized transactions"""
    # Create uncategorized transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=None,  # No category
        transaction_date=datetime.now(),
        description="Unknown Store",
        amount=2500,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_uncategorized_transactions(test_user.id)

    assert len(notifications) == 1
    notif = notifications[0]
    assert notif["type"] == NotificationService.TYPE_UNCATEGORIZED
    assert notif["priority"] == NotificationService.PRIORITY_MEDIUM
    assert "Unknown Store" in notif["message"]
    assert "$25.00" in notif["message"]
    assert notif["data"]["transaction_id"] == transaction.id


def test_check_spending_anomalies_insufficient_data(test_db, test_user, test_category, test_source):
    """Test anomaly detection with insufficient data"""
    # Create only 5 transactions (need 10 minimum)
    for i in range(5):
        transaction = Transaction(
            user_id=test_user.id,
            source_id=test_source.id,
            category_id=test_category.id,
            transaction_date=datetime.now() - timedelta(days=i),
            description=f"Store {i}",
            amount=1000,
            transaction_type="expense",
        )
        test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_spending_anomalies(test_user.id)

    assert len(notifications) == 0  # Not enough data


def test_check_spending_anomalies_found(test_db, test_user, test_category, test_source):
    """Test detecting spending anomalies"""
    # Create 10 normal transactions (~$10)
    for i in range(10):
        transaction = Transaction(
            user_id=test_user.id,
            source_id=test_source.id,
            category_id=test_category.id,
            transaction_date=datetime.now() - timedelta(days=i),
            description=f"Normal Purchase {i}",
            amount=1000,  # $10
            transaction_type="expense",
        )
        test_db.add(transaction)

    # Create one anomalous transaction ($1000)
    anomaly = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Expensive Item",
        amount=100000,  # $1000
        transaction_type="expense",
    )
    test_db.add(anomaly)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_spending_anomalies(test_user.id, threshold=2.0)

    assert len(notifications) > 0
    # Find the expensive item notification
    expensive_notif = next(
        (n for n in notifications if "Expensive Item" in n["message"]), None
    )
    assert expensive_notif is not None
    assert expensive_notif["type"] == NotificationService.TYPE_ANOMALY
    assert "$1000.00" in expensive_notif["message"]


def test_check_spending_anomalies_no_std_dev(test_db, test_user, test_category, test_source):
    """Test anomaly detection when all amounts are the same"""
    # Create transactions with identical amounts
    for i in range(15):
        transaction = Transaction(
            user_id=test_user.id,
            source_id=test_source.id,
            category_id=test_category.id,
            transaction_date=datetime.now() - timedelta(days=i),
            description=f"Same Amount {i}",
            amount=1000,  # All same
            transaction_type="expense",
        )
        test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_spending_anomalies(test_user.id)

    # Should return empty list (std_dev = 0, no anomalies)
    assert len(notifications) == 0


def test_check_large_transactions_none(test_db, test_user, test_category, test_source):
    """Test no large transactions"""
    # Create small transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Small Purchase",
        amount=1000,  # $10
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_large_transactions(test_user.id, threshold_amount=50000)

    assert len(notifications) == 0


def test_check_large_transactions_found(test_db, test_user, test_category, test_source):
    """Test finding large transactions"""
    # Create large expense
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Expensive Purchase",
        amount=75000,  # $750
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_large_transactions(test_user.id, threshold_amount=50000)

    assert len(notifications) == 1
    notif = notifications[0]
    assert notif["type"] == NotificationService.TYPE_LARGE_TRANSACTION
    assert notif["priority"] == NotificationService.PRIORITY_MEDIUM
    assert "$750.00" in notif["message"]
    assert "Expensive Purchase" in notif["message"]


def test_check_large_transactions_income(test_db, test_user, test_category, test_source):
    """Test large income transactions"""
    # Create large income (negative amount)
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Salary Deposit",
        amount=-500000,  # -$5000 (income)
        transaction_type="income",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_large_transactions(test_user.id, threshold_amount=50000)

    assert len(notifications) == 1
    notif = notifications[0]
    assert notif["data"]["type"] == "income"
    assert "$5000.00" in notif["message"]


def test_check_large_transactions_priority(test_db, test_user, test_category, test_source):
    """Test priority levels for large transactions"""
    # Create very large transaction ($1500)
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Very Expensive",
        amount=150000,  # $1500
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    notifications = service.check_large_transactions(test_user.id, threshold_amount=50000)

    # Should be HIGH priority (>= $1000)
    assert notifications[0]["priority"] == NotificationService.PRIORITY_HIGH


def test_get_all_notifications(test_db, test_user, test_category, test_source):
    """Test getting all notifications at once"""
    # Create uncategorized transaction
    uncategorized = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=None,
        transaction_date=datetime.now(),
        description="Uncategorized",
        amount=1000,
        transaction_type="expense",
    )
    test_db.add(uncategorized)

    # Create large transaction
    large = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Large Purchase",
        amount=100000,
        transaction_type="expense",
    )
    test_db.add(large)
    test_db.commit()

    service = NotificationService(test_db)
    all_notifications = service.get_all_notifications(test_user.id)

    assert "uncategorized" in all_notifications
    assert "anomalies" in all_notifications
    assert "large_transactions" in all_notifications
    assert "total_count" in all_notifications
    assert all_notifications["total_count"] >= 2  # At least 2 notifications


def test_get_notification_summary(test_db, test_user, test_category, test_source):
    """Test getting notification counts"""
    # Create uncategorized transactions
    for i in range(3):
        transaction = Transaction(
            user_id=test_user.id,
            source_id=test_source.id,
            category_id=None,
            transaction_date=datetime.now() - timedelta(days=i),
            description=f"Uncategorized {i}",
            amount=1000,
            transaction_type="expense",
        )
        test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    summary = service.get_notification_summary(test_user.id)

    assert summary["uncategorized"] == 3
    assert "anomalies" in summary
    assert "large_transactions" in summary
    assert "total" in summary
    assert summary["total"] >= 3


def test_dismiss_notification_not_found(test_db, test_user):
    """Test dismissing notification for non-existent transaction"""
    service = NotificationService(test_db)

    with pytest.raises(NotFoundError):
        service.dismiss_notification(
            test_user.id, NotificationService.TYPE_UNCATEGORIZED, 99999
        )


def test_dismiss_notification_uncategorized_still_pending(
    test_db, test_user, test_source
):
    """Test dismissing uncategorized notification when still uncategorized"""
    # Create uncategorized transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=None,
        transaction_date=datetime.now(),
        description="Uncategorized",
        amount=1000,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    result = service.dismiss_notification(
        test_user.id, NotificationService.TYPE_UNCATEGORIZED, transaction.id
    )

    assert result is False  # Still needs categorization


def test_dismiss_notification_uncategorized_resolved(
    test_db, test_user, test_category, test_source
):
    """Test dismissing uncategorized notification after categorization"""
    # Create transaction
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=None,
        transaction_date=datetime.now(),
        description="Uncategorized",
        amount=1000,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    # Categorize it
    transaction.category_id = test_category.id
    test_db.commit()

    service = NotificationService(test_db)
    result = service.dismiss_notification(
        test_user.id, NotificationService.TYPE_UNCATEGORIZED, transaction.id
    )

    assert result is True  # Already resolved


def test_dismiss_notification_other_types(test_db, test_user, test_category, test_source):
    """Test dismissing non-uncategorized notifications"""
    transaction = Transaction(
        user_id=test_user.id,
        source_id=test_source.id,
        category_id=test_category.id,
        transaction_date=datetime.now(),
        description="Large Purchase",
        amount=100000,
        transaction_type="expense",
    )
    test_db.add(transaction)
    test_db.commit()

    service = NotificationService(test_db)
    result = service.dismiss_notification(
        test_user.id, NotificationService.TYPE_LARGE_TRANSACTION, transaction.id
    )

    assert result is True  # Just acknowledge


def test_create_system_notification(test_db, test_user):
    """Test creating custom system notification"""
    service = NotificationService(test_db)

    notification = service.create_system_notification(
        user_id=test_user.id,
        title="Welcome",
        message="Welcome to the expense tracker!",
        priority=NotificationService.PRIORITY_LOW,
        action_url="/dashboard",
    )

    assert notification["type"] == NotificationService.TYPE_SYSTEM
    assert notification["priority"] == NotificationService.PRIORITY_LOW
    assert notification["title"] == "Welcome"
    assert notification["message"] == "Welcome to the expense tracker!"
    assert notification["action_url"] == "/dashboard"
    assert "created_at" in notification


def test_create_system_notification_user_not_found(test_db):
    """Test creating notification for non-existent user"""
    service = NotificationService(test_db)

    with pytest.raises(NotFoundError):
        service.create_system_notification(
            user_id=99999, title="Test", message="Test message"
        )


def test_create_system_notification_invalid_priority(test_db, test_user):
    """Test creating notification with invalid priority"""
    service = NotificationService(test_db)

    with pytest.raises(ValidationError):
        service.create_system_notification(
            user_id=test_user.id,
            title="Test",
            message="Test",
            priority="invalid_priority",
        )


def test_notification_types_constants(test_db):
    """Test notification type constants are defined"""
    service = NotificationService(test_db)

    assert hasattr(service, "TYPE_UNCATEGORIZED")
    assert hasattr(service, "TYPE_ANOMALY")
    assert hasattr(service, "TYPE_BUDGET_WARNING")
    assert hasattr(service, "TYPE_LARGE_TRANSACTION")
    assert hasattr(service, "TYPE_SYSTEM")


def test_notification_priorities_constants(test_db):
    """Test notification priority constants are defined"""
    service = NotificationService(test_db)

    assert hasattr(service, "PRIORITY_LOW")
    assert hasattr(service, "PRIORITY_MEDIUM")
    assert hasattr(service, "PRIORITY_HIGH")
    assert hasattr(service, "PRIORITY_URGENT")
