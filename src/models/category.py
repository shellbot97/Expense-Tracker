"""
Category model - represents expense/income categories
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.config.database import Base


class Category(Base):
    """
    Category model for organizing transactions
    
    Categories can be hierarchical (parent-child relationships)
    and support user-defined categorization rules (regex patterns)
    """

    __tablename__ = "categories"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Category details
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Category type: 'expense', 'income', 'transfer'
    category_type = Column(String(20), nullable=False, default="expense")
    
    # Color for UI visualization (hex code)
    color = Column(String(7), nullable=True)  # e.g., "#FF5733"
    
    # Icon name (for UI)
    icon = Column(String(50), nullable=True)
    
    # Hierarchical structure
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Auto-categorization rule (regex pattern for matching transaction descriptions)
    matching_pattern = Column(Text, nullable=True)
    
    # System vs user-defined
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Active status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    transactions = relationship("Transaction", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.category_type}', user_id={self.user_id})>"

    def to_dict(self):
        """Convert category to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "category_type": self.category_type,
            "color": self.color,
            "icon": self.icon,
            "parent_id": self.parent_id,
            "matching_pattern": self.matching_pattern,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
