"""
Notification and alert system for action items
"""

from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.user import User
from src.utils.exceptions import NotFoundError, ValidationError


class NotificationService:
    """
    Service for managing user notifications and alerts
    """

    # Notification types
    TYPE_UNCATEGORIZED = "uncategorized_transaction"
    TYPE_ANOMALY = "spending_anomaly"
    TYPE_BUDGET_WARNING = "budget_warning"
    TYPE_LARGE_TRANSACTION = "large_transaction"
    TYPE_SYSTEM = "system"

    # Notification priorities
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"

    def __init__(self, db: Session):
        self.db = db

    def check_uncategorized_transactions(self, user_id: int) -> List[Dict]:
        """
        Find uncategorized transactions for a user

        Args:
            user_id: User ID

        Returns:
            List of notification dicts for uncategorized transactions
        """
        # Find transactions without categories
        uncategorized = (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.category_id.is_(None),
                )
            )
            .order_by(Transaction.transaction_date.desc())
            .all()
        )

        notifications = []
        for txn in uncategorized:
            notifications.append(
                {
                    "type": self.TYPE_UNCATEGORIZED,
                    "priority": self.PRIORITY_MEDIUM,
                    "title": "Uncategorized Transaction",
                    "message": f"Transaction '{txn.description}' for ${abs(txn.amount) / 100:.2f} needs a category",
                    "data": {
                        "transaction_id": txn.id,
                        "description": txn.description,
                        "amount": txn.amount,
                        "date": txn.transaction_date.isoformat(),
                    },
                    "action_url": f"/transactions/{txn.id}/categorize",
                    "created_at": datetime.utcnow().isoformat(),
                }
            )

        return notifications

    def check_spending_anomalies(
        self, user_id: int, threshold: float = 2.0
    ) -> List[Dict]:
        """
        Detect unusual spending patterns

        Args:
            user_id: User ID
            threshold: Standard deviations from mean (default 2.0)

        Returns:
            List of notification dicts for anomalies
        """
        # Get expense transactions
        transactions = (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == "expense",
                    Transaction.amount > 0,
                )
            )
            .all()
        )

        if len(transactions) < 10:
            return []  # Need enough data for statistical analysis

        # Calculate mean and std deviation
        amounts = [t.amount for t in transactions]
        mean = sum(amounts) / len(amounts)

        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
        std_dev = variance**0.5

        # Find anomalies
        notifications = []
        for txn in transactions:
            z_score = (txn.amount - mean) / std_dev if std_dev > 0 else 0

            if abs(z_score) > threshold:
                # This is an anomaly
                notifications.append(
                    {
                        "type": self.TYPE_ANOMALY,
                        "priority": self.PRIORITY_HIGH
                        if abs(z_score) > 3.0
                        else self.PRIORITY_MEDIUM,
                        "title": "Unusual Spending Detected",
                        "message": f"Transaction '{txn.description}' for ${abs(txn.amount) / 100:.2f} is {abs(z_score):.1f}x your average spending",
                        "data": {
                            "transaction_id": txn.id,
                            "description": txn.description,
                            "amount": txn.amount,
                            "date": txn.transaction_date.isoformat(),
                            "z_score": round(z_score, 2),
                            "mean": round(mean),
                            "std_dev": round(std_dev),
                        },
                        "action_url": f"/transactions/{txn.id}",
                        "created_at": datetime.utcnow().isoformat(),
                    }
                )

        # Return most recent anomalies first
        notifications.sort(
            key=lambda x: x["data"]["date"], reverse=True
        )

        return notifications[:10]  # Limit to top 10

    def check_large_transactions(
        self, user_id: int, threshold_amount: int = 50000
    ) -> List[Dict]:
        """
        Flag large transactions for review

        Args:
            user_id: User ID
            threshold_amount: Minimum amount in cents (default $500)

        Returns:
            List of notification dicts for large transactions
        """
        large_transactions = (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    or_(
                        Transaction.amount >= threshold_amount,
                        Transaction.amount <= -threshold_amount,
                    ),
                )
            )
            .order_by(Transaction.transaction_date.desc())
            .limit(20)
            .all()
        )

        notifications = []
        for txn in large_transactions:
            txn_type = "income" if txn.amount < 0 else "expense"
            notifications.append(
                {
                    "type": self.TYPE_LARGE_TRANSACTION,
                    "priority": self.PRIORITY_HIGH
                    if abs(txn.amount) >= 100000
                    else self.PRIORITY_MEDIUM,
                    "title": f"Large {txn_type.capitalize()}",
                    "message": f"{txn_type.capitalize()} of ${abs(txn.amount) / 100:.2f} from '{txn.description}'",
                    "data": {
                        "transaction_id": txn.id,
                        "description": txn.description,
                        "amount": txn.amount,
                        "date": txn.transaction_date.isoformat(),
                        "type": txn_type,
                    },
                    "action_url": f"/transactions/{txn.id}",
                    "created_at": datetime.utcnow().isoformat(),
                }
            )

        return notifications

    def get_all_notifications(self, user_id: int) -> Dict[str, List[Dict]]:
        """
        Get all notifications for a user

        Args:
            user_id: User ID

        Returns:
            Dict with notification categories:
            {
                "uncategorized": [...],
                "anomalies": [...],
                "large_transactions": [...],
                "total_count": 15
            }
        """
        uncategorized = self.check_uncategorized_transactions(user_id)
        anomalies = self.check_spending_anomalies(user_id)
        large = self.check_large_transactions(user_id)

        return {
            "uncategorized": uncategorized,
            "anomalies": anomalies,
            "large_transactions": large,
            "total_count": len(uncategorized) + len(anomalies) + len(large),
        }

    def get_notification_summary(self, user_id: int) -> Dict[str, int]:
        """
        Get count of notifications by type

        Args:
            user_id: User ID

        Returns:
            Dict with counts: {"uncategorized": 5, "anomalies": 2, ...}
        """
        uncategorized_count = (
            self.db.query(func.count(Transaction.id))
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.category_id.is_(None),
                )
            )
            .scalar()
        )

        # For anomalies and large transactions, we'd need to run the full checks
        # For performance, we can estimate or cache these
        anomalies = self.check_spending_anomalies(user_id)
        large = self.check_large_transactions(user_id)

        return {
            "uncategorized": uncategorized_count or 0,
            "anomalies": len(anomalies),
            "large_transactions": len(large),
            "total": uncategorized_count + len(anomalies) + len(large),
        }

    def dismiss_notification(
        self, user_id: int, notification_type: str, transaction_id: int
    ) -> bool:
        """
        Mark a notification as dismissed (by handling the underlying issue)

        For uncategorized: Assign a category
        For anomalies/large: Just acknowledge (nothing to do)

        Args:
            user_id: User ID
            notification_type: Type of notification
            transaction_id: Related transaction ID

        Returns:
            True if dismissed successfully
        """
        # Verify transaction belongs to user
        transaction = (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id,
                )
            )
            .first()
        )

        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found")

        # For uncategorized notifications, check if it now has a category
        if notification_type == self.TYPE_UNCATEGORIZED:
            if transaction.category_id is not None:
                return True  # Already categorized
            else:
                return False  # Still needs categorization

        # For other notification types, we just acknowledge them
        # In a real system, you'd store dismissal state in a notifications table
        return True

    def create_system_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        priority: str = PRIORITY_MEDIUM,
        action_url: Optional[str] = None,
    ) -> Dict:
        """
        Create a custom system notification

        Args:
            user_id: User ID
            title: Notification title
            message: Notification message
            priority: Priority level
            action_url: Optional action URL

        Returns:
            Notification dict
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        if priority not in [
            self.PRIORITY_LOW,
            self.PRIORITY_MEDIUM,
            self.PRIORITY_HIGH,
            self.PRIORITY_URGENT,
        ]:
            raise ValidationError(f"Invalid priority: {priority}")

        return {
            "type": self.TYPE_SYSTEM,
            "priority": priority,
            "title": title,
            "message": message,
            "data": {},
            "action_url": action_url,
            "created_at": datetime.utcnow().isoformat(),
        }
