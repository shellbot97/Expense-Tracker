"""
Budget model - represents monthly budget limits for categories
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from src.config.database import Base


class Budget(Base):
    """
    Budget model for monthly spending limits
    
    Allows users to set budget limits for specific categories or overall spending.
    Budgets are typically set per month and category.
    """

    __tablename__ = "budgets"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True)

    # Budget details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Amount limit in cents (e.g., $500 = 50000)
    amount_limit = Column(Integer, nullable=False)
    
    # Time period
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Budget period: 'monthly', 'weekly', 'yearly', 'custom'
    period_type = Column(String(20), nullable=False, default="monthly")
    
    # Rollover unused budget to next period
    allow_rollover = Column(Boolean, default=False, nullable=False)
    
    # Alert thresholds (percentage of budget)
    alert_threshold_50 = Column(Boolean, default=True, nullable=False)
    alert_threshold_75 = Column(Boolean, default=True, nullable=False)
    alert_threshold_90 = Column(Boolean, default=True, nullable=False)
    alert_threshold_100 = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category")

    # Unique constraint: one budget per category per time period
    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "start_date", "end_date", name="uq_budget_user_category_period"),
    )

    def __repr__(self):
        return f"<Budget(id={self.id}, name='{self.name}', limit={self.amount_limit}, period={self.start_date} to {self.end_date})>"

    def to_dict(self):
        """Convert budget to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "amount_limit": self.amount_limit,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "period_type": self.period_type,
            "allow_rollover": self.allow_rollover,
            "alert_threshold_50": self.alert_threshold_50,
            "alert_threshold_75": self.alert_threshold_75,
            "alert_threshold_90": self.alert_threshold_90,
            "alert_threshold_100": self.alert_threshold_100,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_limit_dollars(self) -> float:
        """Convert amount limit from cents to dollars"""
        return self.amount_limit / 100.0 if self.amount_limit is not None else 0.0

    @staticmethod
    def dollars_to_cents(dollars: float) -> int:
        """Convert dollars to cents (for storage)"""
        return int(round(dollars * 100))
