"""
AI-powered chat interface for transaction insights and queries
"""

import requests
import json
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from src.config.settings import settings
from src.models.user import User
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.source import Source
from src.services.privacy_service import PrivacyService
from src.utils.exceptions import ValidationError


class AIChatService:
    """
    AI-powered chat interface for natural language queries about transactions
    Uses local Ollama llama3 for chat interactions
    """

    def __init__(self, db: Session):
        self.db = db
        self.privacy_service = PrivacyService(db)
        self.ollama_base_url = settings.AI_API_BASE
        self.model = settings.AI_MODEL
        self.timeout = 30  # Longer timeout for chat

    def chat(
        self,
        user_id: int,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Dict[str, str]]:
        """
        Process a natural language query about transactions

        Args:
            user_id: User ID
            query: Natural language question
            conversation_history: Previous messages in conversation

        Returns:
            {
                "response": "Your total spending on groceries last month was $543.21",
                "data": {...},  # Optional structured data
                "method": "ai"
            }
            Or None if permission disabled or AI unavailable
        """
        # Check permission
        if not self.privacy_service.check_permission(user_id, "ai_chat"):
            return None

        # Get user context
        context = self._build_user_context(user_id, query)
        if not context:
            return {
                "response": "I don't have enough data to answer that question yet.",
                "method": "fallback",
            }

        # Build prompt with context
        prompt = self._build_chat_prompt(query, context, conversation_history)

        # Call Ollama API
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=self.timeout,
            )

            if response.status_code != 200:
                return None

            ai_response = response.json()
            response_text = ai_response.get("response", "")

            # Parse JSON response
            try:
                parsed = json.loads(response_text)
                return {
                    "response": parsed.get("answer", response_text),
                    "data": parsed.get("data"),
                    "method": "ai",
                }
            except json.JSONDecodeError:
                # Fallback to text response
                return {"response": response_text, "method": "ai"}

        except Exception:
            return None

    def _build_user_context(
        self, user_id: int, query: str
    ) -> Optional[Dict[str, any]]:
        """
        Build context about user's data based on query

        Args:
            user_id: User ID
            query: User's question

        Returns:
            Context dict with relevant data
        """
        context = {}

        # Get date range based on query
        date_range = self._extract_date_range(query)
        filters = [Transaction.user_id == user_id]

        if date_range:
            filters.append(Transaction.transaction_date >= date_range["start"])
            filters.append(Transaction.transaction_date <= date_range["end"])
            context["date_range"] = date_range

        # Get transaction summary
        transactions = self.db.query(Transaction).filter(and_(*filters)).all()
        if not transactions:
            return None

        context["transaction_count"] = len(transactions)
        context["total_expenses"] = sum(
            t.amount for t in transactions if t.transaction_type == "expense"
        )
        context["total_income"] = sum(
            t.amount for t in transactions if t.transaction_type == "income"
        )

        # Get category breakdown
        category_summary = (
            self.db.query(Category.name, func.sum(Transaction.amount))
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(and_(*filters))
            .filter(Transaction.transaction_type == "expense")
            .group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(10)
            .all()
        )

        context["top_categories"] = [
            {"name": cat, "amount": float(amt)} for cat, amt in category_summary
        ]

        # Get source breakdown
        source_summary = (
            self.db.query(Source.name, func.sum(Transaction.amount))
            .join(Transaction, Transaction.source_id == Source.id)
            .filter(and_(*filters))
            .filter(Transaction.transaction_type == "expense")
            .group_by(Source.name)
            .all()
        )

        context["sources"] = [
            {"name": src, "amount": float(amt)} for src, amt in source_summary
        ]

        # Get top merchants
        merchant_summary = (
            self.db.query(Transaction.description, func.sum(Transaction.amount))
            .filter(and_(*filters))
            .filter(Transaction.transaction_type == "expense")
            .group_by(Transaction.description)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(10)
            .all()
        )

        context["top_merchants"] = [
            {"name": desc, "amount": float(amt)} for desc, amt in merchant_summary
        ]

        return context

    def _extract_date_range(self, query: str) -> Optional[Dict[str, datetime]]:
        """
        Extract date range from natural language query

        Args:
            query: Natural language query

        Returns:
            {"start": datetime, "end": datetime} or None
        """
        query_lower = query.lower()
        now = datetime.now()

        # Last month
        if "last month" in query_lower:
            first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0)
            last_month_end = first_of_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return {"start": last_month_start, "end": last_month_end}

        # This month
        if "this month" in query_lower:
            return {"start": now.replace(day=1, hour=0, minute=0, second=0), "end": now}

        # Last year
        if "last year" in query_lower:
            last_year = now.year - 1
            return {
                "start": datetime(last_year, 1, 1),
                "end": datetime(last_year, 12, 31, 23, 59, 59),
            }

        # This year
        if "this year" in query_lower:
            return {"start": datetime(now.year, 1, 1), "end": now}

        # Last 30 days
        if "last 30 days" in query_lower or "last month" in query_lower:
            return {"start": now - timedelta(days=30), "end": now}

        # Last 7 days
        if "last week" in query_lower or "last 7 days" in query_lower:
            return {"start": now - timedelta(days=7), "end": now}

        # Default: all time
        return None

    def _build_chat_prompt(
        self,
        query: str,
        context: Dict[str, any],
        conversation_history: Optional[List[Dict[str, str]]],
    ) -> str:
        """
        Build AI prompt with user context

        Args:
            query: User's question
            context: Transaction context
            conversation_history: Previous messages

        Returns:
            Formatted prompt string
        """
        # Build conversation context
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages only
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role.capitalize()}: {content}\n"

        # Build data context
        date_info = ""
        if context.get("date_range"):
            start = context["date_range"]["start"].strftime("%Y-%m-%d")
            end = context["date_range"]["end"].strftime("%Y-%m-%d")
            date_info = f"Date Range: {start} to {end}\n"

        categories_text = "\n".join(
            [
                f"  - {cat['name']}: ${cat['amount'] / 100:.2f}"
                for cat in context.get("top_categories", [])[:5]
            ]
        )

        sources_text = "\n".join(
            [
                f"  - {src['name']}: ${src['amount'] / 100:.2f}"
                for src in context.get("sources", [])
            ]
        )

        prompt = f"""You are a personal finance assistant analyzing a user's transaction data.

{history_text}
User Question: {query}

Transaction Summary:
{date_info}Total Transactions: {context.get('transaction_count', 0)}
Total Expenses: ${context.get('total_expenses', 0) / 100:.2f}
Total Income: ${context.get('total_income', 0) / 100:.2f}

Top Spending Categories:
{categories_text if categories_text else '  (No categories yet)'}

Spending by Source:
{sources_text if sources_text else '  (No sources yet)'}

Instructions:
1. Answer the user's question based on the data provided
2. Be conversational and helpful
3. Use specific numbers and categories from the data
4. If asked about trends, compare to the data provided
5. If the data doesn't contain the answer, say so clearly

Respond ONLY with valid JSON in this format:
{{
  "answer": "your conversational response here",
  "data": {{  // optional structured data
    "key": "value"
  }}
}}"""

        return prompt

    def is_available(self) -> bool:
        """
        Check if Ollama service is available

        Returns:
            True if available, False otherwise
        """
        try:
            response = requests.get(
                f"{self.ollama_base_url}/api/tags", timeout=2
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_conversation_summary(
        self, conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a summary of the conversation

        Args:
            conversation_history: List of messages

        Returns:
            Summary string
        """
        if not conversation_history:
            return "No conversation yet"

        messages = [
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in conversation_history
        ]
        return "\n".join(messages[-10:])  # Last 10 messages
