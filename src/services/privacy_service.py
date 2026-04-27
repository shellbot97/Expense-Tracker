"""
Privacy and data control service
Manages user preferences for data sharing and AI features
"""

from sqlalchemy.orm import Session
from src.models.user import User
from src.utils.exceptions import NotFoundError, ValidationError
from typing import Dict, Optional
from datetime import datetime


class PrivacyService:
    """
    Service for managing user privacy preferences and data control
    
    For local-first applications with optional AI features.
    """
    
    def __init__(self, db: Session):
        """Initialize privacy service"""
        self.db = db
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """
        Get user's privacy and AI preferences
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with preference settings
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        # Default privacy-first settings
        preferences = {
            "ai_categorization_enabled": False,
            "ai_chat_enabled": False,
            "data_export_enabled": True,
            "analytics_enabled": True,
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        return preferences
    
    def update_preferences(
        self,
        user_id: int,
        ai_categorization_enabled: Optional[bool] = None,
        ai_chat_enabled: Optional[bool] = None,
        data_export_enabled: Optional[bool] = None,
        analytics_enabled: Optional[bool] = None,
    ) -> Dict:
        """
        Update user's privacy preferences
        
        Args:
            user_id: User ID
            ai_categorization_enabled: Enable AI auto-categorization
            ai_chat_enabled: Enable AI chat features
            data_export_enabled: Allow data export
            analytics_enabled: Enable analytics tracking
            
        Returns:
            Updated preferences
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        # In a real implementation, these would be stored in a preferences table
        # For now, we return the requested settings
        preferences = {
            "user_id": user_id,
            "ai_categorization_enabled": ai_categorization_enabled if ai_categorization_enabled is not None else False,
            "ai_chat_enabled": ai_chat_enabled if ai_chat_enabled is not None else False,
            "data_export_enabled": data_export_enabled if data_export_enabled is not None else True,
            "analytics_enabled": analytics_enabled if analytics_enabled is not None else True,
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        return preferences
    
    def check_permission(self, user_id: int, permission: str) -> bool:
        """
        Check if user has granted permission for a feature
        
        Args:
            user_id: User ID
            permission: Permission name (ai_categorization, ai_chat, data_export, analytics)
            
        Returns:
            True if permission granted, False otherwise
        """
        valid_permissions = {
            "ai_categorization",
            "ai_chat",
            "data_export",
            "analytics",
        }
        
        if permission not in valid_permissions:
            raise ValidationError(f"Invalid permission: {permission}")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        # Default to privacy-first (disabled for AI, enabled for local features)
        defaults = {
            "ai_categorization": False,
            "ai_chat": False,
            "data_export": True,
            "analytics": True,
        }
        
        return defaults.get(permission, False)
    
    def anonymize_description(self, description: str) -> str:
        """
        Anonymize transaction description for privacy
        
        Removes potential PII like names, addresses, phone numbers.
        Useful for sharing data or using external AI services.
        
        Args:
            description: Original transaction description
            
        Returns:
            Anonymized description
        """
        import re
        
        # Simple anonymization (can be enhanced)
        anonymized = description
        
        # Remove potential card numbers (partial cards in descriptions)
        anonymized = re.sub(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', '[CARD]', anonymized)
        anonymized = re.sub(r'\*+\d{4}', '[CARD]', anonymized)
        
        # Remove potential account numbers (8+ consecutive digits) - BEFORE phone numbers
        anonymized = re.sub(r'\b\d{8,}\b', '[ACCOUNT]', anonymized)
        
        # Remove potential phone numbers
        anonymized = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '[PHONE]', anonymized)
        
        # Remove potential email addresses
        anonymized = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', anonymized)
        
        return anonymized
    
    def get_data_summary(self, user_id: int) -> Dict:
        """
        Get summary of user's stored data
        
        For transparency and data control (GDPR-like).
        
        Args:
            user_id: User ID
            
        Returns:
            Summary of stored data
        """
        from src.models.transaction import Transaction
        from src.models.category import Category
        from src.models.source import Source
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        # Count user's data
        transaction_count = self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).count()
        
        category_count = self.db.query(Category).filter(
            Category.user_id == user_id
        ).count()
        
        source_count = self.db.query(Source).filter(
            Source.user_id == user_id
        ).count()
        
        return {
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "account_created": user.created_at.isoformat(),
            "data_summary": {
                "transactions": transaction_count,
                "categories": category_count,
                "sources": source_count,
            },
            "privacy_notice": "All data is stored locally. No data is shared with third parties.",
        }
