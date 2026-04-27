"""
Transaction model - represents individual financial transactions
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from src.config.database import Base


class Transaction(Base):
    """
    Transaction model for individual financial transactions
    
    Core model storing all expense/income/transfer records.
    Money is stored as integers (cents) to avoid floating point issues.
    """

    __tablename__ = "transactions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True)

    # Transaction details
    description = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Amount in cents (e.g., $10.50 = 1050)
    amount = Column(Integer, nullable=False)
    
    # Transaction type: 'expense', 'income', 'transfer'
    transaction_type = Column(String(20), nullable=False, default="expense", index=True)
    
    # Transaction date (when it actually occurred)
    transaction_date = Column(Date, nullable=False, index=True)
    
    # Original data from statement (if imported)
    original_description = Column(Text, nullable=True)
    original_amount = Column(String(50), nullable=True)  # Store as string to preserve format
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False, nullable=False)
    reconciled_at = Column(DateTime, nullable=True)
    
    # Categorization
    is_manually_categorized = Column(Boolean, default=False, nullable=False)
    categorized_by_ai = Column(Boolean, default=False, nullable=False)
    ai_confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Tags (comma-separated for simple implementation)
    tags = Column(String(500), nullable=True)
    
    # Statement import tracking
    import_source = Column(String(100), nullable=True)  # e.g., "Chase_Statement_2024_01.csv"
    import_date = Column(DateTime, nullable=True)
    
    # Hash for duplicate detection
    transaction_hash = Column(String(64), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    source = relationship("Source", back_populates="transactions")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "transaction_date"),
        Index("ix_transactions_user_category", "user_id", "category_id"),
        Index("ix_transactions_user_type", "user_id", "transaction_type"),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, desc='{self.description[:30]}', amount={self.amount}, date={self.transaction_date})>"

    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "source_id": self.source_id,
            "description": self.description,
            "notes": self.notes,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "original_description": self.original_description,
            "original_amount": self.original_amount,
            "is_reconciled": self.is_reconciled,
            "reconciled_at": self.reconciled_at.isoformat() if self.reconciled_at else None,
            "is_manually_categorized": self.is_manually_categorized,
            "categorized_by_ai": self.categorized_by_ai,
            "ai_confidence_score": self.ai_confidence_score,
            "tags": self.tags,
            "import_source": self.import_source,
            "import_date": self.import_date.isoformat() if self.import_date else None,
            "transaction_hash": self.transaction_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_amount_dollars(self) -> float:
        """Convert amount from cents to dollars"""
        return self.amount / 100.0 if self.amount is not None else 0.0

    @staticmethod
    def dollars_to_cents(dollars: float) -> int:
        """Convert dollars to cents (for storage)"""
        return int(round(dollars * 100))
