"""
Analytics service - generate spending insights and statistics
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import func, and_, or_, extract
from sqlalchemy.orm import Session
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.source import Source
from src.utils.exceptions import ValidationError


class AnalyticsService:
    """
    Service for generating financial analytics and insights
    
    Provides spending summaries, trends, comparisons, and anomaly detection.
    """
    
    def __init__(self, db: Session):
        """Initialize analytics service"""
        self.db = db
    
    def get_spending_by_category(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: str = "expense",
    ) -> List[Dict]:
        """
        Get spending aggregated by category
        
        Args:
            user_id: User ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            transaction_type: Type filter (expense/income/transfer)
            
        Returns:
            List of dicts with category_id, category_name, total_amount, count
        """
        query = self.db.query(
            Transaction.category_id,
            Category.name.label("category_name"),
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("count"),
        ).join(
            Category, Transaction.category_id == Category.id, isouter=True
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
        )
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        query = query.group_by(Transaction.category_id, Category.name)
        query = query.order_by(func.sum(Transaction.amount).desc())
        
        results = []
        for row in query.all():
            results.append({
                "category_id": row.category_id,
                "category_name": row.category_name or "Uncategorized",
                "total_amount": row.total_amount,
                "count": row.count,
            })
        
        return results
    
    def get_spending_by_source(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: str = "expense",
    ) -> List[Dict]:
        """
        Get spending aggregated by source
        
        Args:
            user_id: User ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            transaction_type: Type filter (expense/income/transfer)
            
        Returns:
            List of dicts with source_id, source_name, total_amount, count
        """
        query = self.db.query(
            Transaction.source_id,
            Source.name.label("source_name"),
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("count"),
        ).join(
            Source, Transaction.source_id == Source.id, isouter=True
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
        )
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        query = query.group_by(Transaction.source_id, Source.name)
        query = query.order_by(func.sum(Transaction.amount).desc())
        
        results = []
        for row in query.all():
            results.append({
                "source_id": row.source_id,
                "source_name": row.source_name or "Unknown",
                "total_amount": row.total_amount,
                "count": row.count,
            })
        
        return results
    
    def get_spending_trends(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
        granularity: str = "month",
        transaction_type: str = "expense",
    ) -> List[Dict]:
        """
        Get spending trends over time
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            granularity: Time period (day/week/month/year)
            transaction_type: Type filter (expense/income/transfer)
            
        Returns:
            List of dicts with period, total_amount, avg_amount, count
        """
        if granularity not in ["day", "week", "month", "year"]:
            raise ValidationError(f"Invalid granularity: {granularity}")
        
        # Build query based on granularity
        if granularity == "day":
            period = func.date(Transaction.transaction_date)
        elif granularity == "week":
            period = func.strftime("%Y-W%W", Transaction.transaction_date)
        elif granularity == "month":
            period = func.strftime("%Y-%m", Transaction.transaction_date)
        else:  # year
            period = func.strftime("%Y", Transaction.transaction_date)
        
        query = self.db.query(
            period.label("period"),
            func.sum(Transaction.amount).label("total_amount"),
            func.avg(Transaction.amount).label("avg_amount"),
            func.count(Transaction.id).label("count"),
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        ).group_by(
            "period"
        ).order_by(
            "period"
        )
        
        results = []
        for row in query.all():
            results.append({
                "period": row.period,
                "total_amount": row.total_amount,
                "avg_amount": int(row.avg_amount) if row.avg_amount else 0,
                "count": row.count,
            })
        
        return results
    
    def get_period_comparison(
        self,
        user_id: int,
        current_start: date,
        current_end: date,
        previous_start: date,
        previous_end: date,
        transaction_type: str = "expense",
    ) -> Dict:
        """
        Compare spending between two periods
        
        Args:
            user_id: User ID
            current_start: Current period start
            current_end: Current period end
            previous_start: Previous period start
            previous_end: Previous period end
            transaction_type: Type filter (expense/income/transfer)
            
        Returns:
            Dict with current, previous, change, change_percent
        """
        # Current period
        current_total = self.db.query(
            func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.transaction_date >= current_start,
            Transaction.transaction_date <= current_end,
        ).scalar() or 0
        
        # Previous period
        previous_total = self.db.query(
            func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.transaction_date >= previous_start,
            Transaction.transaction_date <= previous_end,
        ).scalar() or 0
        
        # Calculate change
        change = current_total - previous_total
        change_percent = (change / previous_total * 100) if previous_total else 0
        
        return {
            "current_period": {
                "start": current_start.isoformat(),
                "end": current_end.isoformat(),
                "total": current_total,
            },
            "previous_period": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
                "total": previous_total,
            },
            "change": change,
            "change_percent": round(change_percent, 2),
        }
    
    def get_top_merchants(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: str = "expense",
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get top merchants/vendors by spending
        
        Args:
            user_id: User ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            transaction_type: Type filter (expense/income/transfer)
            limit: Number of results to return
            
        Returns:
            List of dicts with description, total_amount, count
        """
        query = self.db.query(
            Transaction.description,
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("count"),
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
        )
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        query = query.group_by(Transaction.description)
        query = query.order_by(func.sum(Transaction.amount).desc())
        query = query.limit(limit)
        
        results = []
        for row in query.all():
            results.append({
                "description": row.description,
                "total_amount": row.total_amount,
                "count": row.count,
            })
        
        return results
    
    def detect_anomalies(
        self,
        user_id: int,
        lookback_days: int = 90,
        threshold_multiplier: float = 2.0,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Detect unusual spending patterns (simple anomaly detection)
        
        Uses mean + standard deviation to identify outliers.
        
        Args:
            user_id: User ID
            lookback_days: Days to look back for baseline
            threshold_multiplier: Multiplier for std dev (higher = fewer anomalies)
            end_date: End date for analysis (default: today)
            
        Returns:
            List of transaction dicts that are anomalies
        """
        # Get baseline stats
        if end_date is None:
            # If no end_date, use the most recent transaction date
            latest = self.db.query(func.max(Transaction.transaction_date)).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
            ).scalar()
            
            if not latest:
                return []  # No transactions
            
            end_date = latest
        
        lookback_start = end_date - timedelta(days=lookback_days)
        
        # First query: Get mean and count
        base_stats = self.db.query(
            func.avg(Transaction.amount).label("avg_amount"),
            func.count(Transaction.id).label("count"),
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= lookback_start,
            Transaction.transaction_date <= end_date,
        ).first()
        
        if not base_stats or not base_stats.count or base_stats.count < 5:
            return []  # Not enough data
        
        avg_amount = base_stats.avg_amount or 0
        
        # Second query: Calculate variance manually
        # Get all amounts to calculate std dev
        amounts = self.db.query(Transaction.amount).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= lookback_start,
            Transaction.transaction_date <= end_date,
        ).all()
        
        # Calculate variance
        variance_sum = sum((amt[0] - avg_amount) ** 2 for amt in amounts)
        variance = variance_sum / len(amounts)
        std_dev = variance ** 0.5
        
        # Threshold = mean + (threshold_multiplier * stddev)
        threshold = avg_amount + (threshold_multiplier * std_dev)
        
        # Find transactions above threshold
        anomalous = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= lookback_start,
            Transaction.transaction_date <= end_date,
            Transaction.amount > threshold,
        ).order_by(
            Transaction.transaction_date.desc()
        ).limit(20).all()
        
        results = []
        for trans in anomalous:
            results.append({
                "id": trans.id,
                "date": trans.transaction_date.isoformat(),
                "description": trans.description,
                "amount": trans.amount,
                "expected_max": int(threshold),
                "deviation": int(trans.amount - avg_amount),
            })
        
        return results
    
    def get_summary_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Get summary statistics for all transaction types
        
        Args:
            user_id: User ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            
        Returns:
            Dict with total_expenses, total_income, net_savings, transaction_count
        """
        base_query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if start_date:
            base_query = base_query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            base_query = base_query.filter(Transaction.transaction_date <= end_date)
        
        # Expenses
        total_expenses = base_query.filter(
            Transaction.transaction_type == "expense"
        ).with_entities(
            func.sum(Transaction.amount)
        ).scalar() or 0
        
        # Income
        total_income = base_query.filter(
            Transaction.transaction_type == "income"
        ).with_entities(
            func.sum(Transaction.amount)
        ).scalar() or 0
        
        # Count
        transaction_count = base_query.count()
        
        # Net savings
        net_savings = total_income - total_expenses
        
        return {
            "total_expenses": total_expenses,
            "total_income": total_income,
            "net_savings": net_savings,
            "transaction_count": transaction_count,
        }
