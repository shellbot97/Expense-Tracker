"""
AI-powered categorization service using local Ollama
"""

import requests
from typing import Optional, Dict
from sqlalchemy.orm import Session
from src.config.settings import settings
from src.models.transaction import Transaction
from src.models.category import Category
from src.services.privacy_service import PrivacyService
from src.utils.exceptions import ValidationError
import json


class AICategorizationService:
    """
    AI-powered transaction categorization using local Ollama (llama3)
    
    Optional feature that requires user consent via privacy settings.
    Falls back to rule-based categorization if disabled or unavailable.
    """
    
    def __init__(self, db: Session):
        """Initialize AI categorization service"""
        self.db = db
        self.privacy_service = PrivacyService(db)
        self.ollama_url = f"{settings.AI_API_BASE}/api/generate"
    
    def categorize_transaction(
        self,
        user_id: int,
        description: str,
        amount: int,
        transaction_type: str,
    ) -> Optional[Dict]:
        """
        Use AI to suggest category for a transaction
        
        Args:
            user_id: User ID (for permission check)
            description: Transaction description
            amount: Transaction amount in cents
            transaction_type: Type (expense, income, transfer)
            
        Returns:
            Dict with category_id, confidence, reasoning or None if disabled/unavailable
        """
        # Check if user has enabled AI categorization
        if not self.privacy_service.check_permission(user_id, "ai_categorization"):
            return None
        
        # Get user's categories
        categories = self.db.query(Category).filter(
            Category.user_id == user_id,
            Category.category_type == transaction_type,
            Category.is_active == True
        ).all()
        
        if not categories:
            return None
        
        # Build prompt for Ollama
        category_list = "\n".join([
            f"- {cat.name}: {cat.description or 'No description'}"
            for cat in categories
        ])
        
        amount_str = f"${abs(amount)/100:.2f}"
        
        prompt = f"""You are a financial categorization assistant. Analyze this transaction and suggest the most appropriate category.

Transaction:
- Description: {description}
- Amount: {amount_str}
- Type: {transaction_type}

Available Categories:
{category_list}

Instructions:
1. Choose the ONE most appropriate category from the list above
2. Provide a confidence score between 0 and 1
3. Briefly explain your reasoning

Respond ONLY with valid JSON in this exact format:
{{
  "category_name": "exact category name from list",
  "confidence": 0.95,
  "reasoning": "brief explanation"
}}"""
        
        try:
            # Call Ollama API
            response = requests.post(
                self.ollama_url,
                json={
                    "model": settings.AI_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=10,
            )
            
            if response.status_code != 200:
                # Ollama unavailable - gracefully degrade
                return None
            
            # Parse Ollama response
            ollama_result = response.json()
            ai_response = ollama_result.get("response", "")
            
            # Parse AI JSON response
            try:
                result = json.loads(ai_response)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', ai_response)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValidationError("Invalid AI response format")
            
            # Find matching category
            category_name = result.get("category_name", "")
            matching_cat = next(
                (cat for cat in categories if cat.name.lower() == category_name.lower()),
                None
            )
            
            if not matching_cat:
                return None
            
            return {
                "category_id": matching_cat.id,
                "category_name": matching_cat.name,
                "confidence": float(result.get("confidence", 0.5)),
                "reasoning": result.get("reasoning", ""),
                "method": "ai",
            }
            
        except requests.exceptions.RequestException as e:
            # Ollama unavailable - gracefully degrade
            return None
        except (json.JSONDecodeError, ValidationError):
            # AI returned invalid response - gracefully degrade
            return None
    
    def bulk_categorize(
        self,
        user_id: int,
        transaction_ids: list[int],
    ) -> Dict[int, Optional[Dict]]:
        """
        Categorize multiple transactions using AI
        
        Args:
            user_id: User ID
            transaction_ids: List of transaction IDs to categorize
            
        Returns:
            Dict mapping transaction_id to categorization result
        """
        # Check permission
        if not self.privacy_service.check_permission(user_id, "ai_categorization"):
            return {tid: None for tid in transaction_ids}
        
        results = {}
        
        for transaction_id in transaction_ids:
            transaction = self.db.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id
            ).first()
            
            if not transaction:
                results[transaction_id] = None
                continue
            
            result = self.categorize_transaction(
                user_id=user_id,
                description=transaction.description,
                amount=transaction.amount,
                transaction_type=transaction.transaction_type,
            )
            
            results[transaction_id] = result
        
        return results
    
    def is_available(self) -> bool:
        """
        Check if Ollama is available and responding
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(
                f"{settings.AI_API_BASE}/api/tags",
                timeout=2,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_model_info(self) -> Optional[Dict]:
        """
        Get information about the configured AI model
        
        Returns:
            Dict with model info or None if unavailable
        """
        try:
            response = requests.get(
                f"{settings.AI_API_BASE}/api/tags",
                timeout=2,
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            models = data.get("models", [])
            
            # Find configured model
            model_info = next(
                (m for m in models if m.get("name", "").startswith(settings.AI_MODEL)),
                None
            )
            
            if not model_info:
                return None
            
            return {
                "name": model_info.get("name"),
                "size": model_info.get("size"),
                "modified_at": model_info.get("modified_at"),
                "available": True,
            }
            
        except requests.exceptions.RequestException:
            return None
