"""
Source model - represents payment sources (bank accounts, credit cards, etc.)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.config.database import Base


class Source(Base):
    """
    Source model for payment sources
    
    Represents where money comes from or goes to:
    - Bank accounts
    - Credit cards
    - Cash
    - Digital wallets (PayPal, Venmo, etc.)
    """

    __tablename__ = "sources"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Source details
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Source type: 'bank_account', 'credit_card', 'cash', 'digital_wallet', 'other'
    source_type = Column(String(50), nullable=False, default="bank_account")
    
    # Account details
    account_number_last4 = Column(String(4), nullable=True)  # Last 4 digits for reference
    institution_name = Column(String(100), nullable=True)  # Bank/institution name
    
    # Balance tracking (in cents to avoid floating point issues)
    current_balance = Column(Integer, nullable=True)  # None = not tracked
    
    # Color for UI visualization
    color = Column(String(7), nullable=True)  # e.g., "#4CAF50"
    
    # Icon name (for UI)
    icon = Column(String(50), nullable=True)
    
    # Active status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="sources")
    transactions = relationship("Transaction", back_populates="source")

    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', type='{self.source_type}', user_id={self.user_id})>"

    def to_dict(self):
        """Convert source to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "source_type": self.source_type,
            "account_number_last4": self.account_number_last4,
            "institution_name": self.institution_name,
            "current_balance": self.current_balance,
            "color": self.color,
            "icon": self.icon,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
