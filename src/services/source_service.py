"""
Source service - Business logic for source (payment account) management
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.models.source import Source
from src.utils.exceptions import ValidationError, NotFoundError, AlreadyExistsError


class SourceService:
    """Service for managing payment sources"""

    VALID_SOURCE_TYPES = ["bank_account", "credit_card", "cash", "digital_wallet", "other"]

    def __init__(self, db: Session):
        self.db = db

    def create_source(
        self,
        user_id: int,
        name: str,
        source_type: str,
        description: Optional[str] = None,
        account_number_last4: Optional[str] = None,
        institution_name: Optional[str] = None,
        current_balance: Optional[int] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Source:
        """
        Create a new payment source
        
        Args:
            user_id: User ID
            name: Source name
            source_type: Type of source (bank_account, credit_card, etc.)
            description: Optional description
            account_number_last4: Last 4 digits of account
            institution_name: Bank/institution name
            current_balance: Current balance in cents
            color: UI color (hex)
            icon: UI icon name
            
        Returns:
            Created source
            
        Raises:
            ValidationError: If validation fails
            AlreadyExistsError: If source name already exists for user
        """
        # Validate inputs
        self._validate_name(name)
        self._validate_source_type(source_type)
        if account_number_last4:
            self._validate_last4(account_number_last4)
        
        # Check for duplicate name
        existing = self._get_source_by_name(user_id, name)
        if existing:
            raise AlreadyExistsError(f"Source with name '{name}' already exists")

        # Create source
        source = Source(
            user_id=user_id,
            name=name.strip(),
            source_type=source_type,
            description=description,
            account_number_last4=account_number_last4,
            institution_name=institution_name,
            current_balance=current_balance,
            color=color,
            icon=icon,
        )

        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)

        return source

    def get_source(self, source_id: int, user_id: int) -> Optional[Source]:
        """Get source by ID"""
        return (
            self.db.query(Source)
            .filter(
                Source.id == source_id,
                Source.user_id == user_id,
            )
            .first()
        )

    def list_sources(
        self,
        user_id: int,
        source_type: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> List[Source]:
        """List sources for user with optional filters"""
        query = self.db.query(Source).filter(Source.user_id == user_id)

        if source_type:
            query = query.filter(Source.source_type == source_type)
        if is_active is not None:
            query = query.filter(Source.is_active == is_active)

        query = query.order_by(Source.name)

        return query.all()

    def update_source(
        self,
        source_id: int,
        user_id: int,
        name: Optional[str] = None,
        source_type: Optional[str] = None,
        description: Optional[str] = None,
        account_number_last4: Optional[str] = None,
        institution_name: Optional[str] = None,
        current_balance: Optional[int] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Source:
        """Update source"""
        source = self.get_source(source_id, user_id)
        if not source:
            raise NotFoundError(f"Source with ID {source_id} not found")

        # Validate updates
        if name is not None:
            self._validate_name(name)
            # Check for duplicate if name changed
            if name != source.name:
                existing = self._get_source_by_name(user_id, name)
                if existing:
                    raise AlreadyExistsError(f"Source with name '{name}' already exists")
            source.name = name.strip()
        
        if source_type is not None:
            self._validate_source_type(source_type)
            source.source_type = source_type
        
        if account_number_last4 is not None:
            self._validate_last4(account_number_last4)
            source.account_number_last4 = account_number_last4
        
        if description is not None:
            source.description = description
        if institution_name is not None:
            source.institution_name = institution_name
        if current_balance is not None:
            source.current_balance = current_balance
        if color is not None:
            source.color = color
        if icon is not None:
            source.icon = icon
        if is_active is not None:
            source.is_active = is_active

        self.db.commit()
        self.db.refresh(source)

        return source

    def delete_source(self, source_id: int, user_id: int) -> bool:
        """Delete source"""
        source = self.get_source(source_id, user_id)
        if not source:
            raise NotFoundError(f"Source with ID {source_id} not found")

        self.db.delete(source)
        self.db.commit()

        return True

    # Private validation methods

    def _validate_name(self, name: str):
        """Validate source name"""
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty")
        if len(name) > 100:
            raise ValidationError("Name cannot exceed 100 characters")

    def _validate_source_type(self, source_type: str):
        """Validate source type"""
        if source_type not in self.VALID_SOURCE_TYPES:
            raise ValidationError(
                f"Invalid source_type. Must be one of: {', '.join(self.VALID_SOURCE_TYPES)}"
            )

    def _validate_last4(self, last4: str):
        """Validate last 4 digits"""
        if len(last4) != 4:
            raise ValidationError("account_number_last4 must be exactly 4 characters")
        if not last4.isdigit():
            raise ValidationError("account_number_last4 must contain only digits")

    def _get_source_by_name(self, user_id: int, name: str) -> Optional[Source]:
        """Get source by name for user"""
        return (
            self.db.query(Source)
            .filter(
                Source.user_id == user_id,
                Source.name == name.strip(),
            )
            .first()
        )
