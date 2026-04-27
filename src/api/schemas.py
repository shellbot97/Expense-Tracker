"""
Pydantic schemas for authentication API
Request and response models
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional


class UserRegisterRequest(BaseModel):
    """Request schema for user registration"""

    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLoginRequest(BaseModel):
    """Request schema for user login"""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Response schema for successful login"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """Response schema for user data (no password)"""

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


# ============= Transaction Schemas =============

class TransactionCreateRequest(BaseModel):
    """Schema for creating a transaction"""
    description: str = Field(..., min_length=1, max_length=500)
    amount: int = Field(..., gt=0, description="Amount in cents")
    transaction_type: str = Field(..., pattern="^(expense|income|transfer)$")
    transaction_date: date
    category_id: Optional[int] = None
    source_id: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[str] = None


class TransactionUpdateRequest(BaseModel):
    """Schema for updating a transaction"""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[int] = Field(None, gt=0)
    transaction_type: Optional[str] = Field(None, pattern="^(expense|income|transfer)$")
    transaction_date: Optional[date] = None
    category_id: Optional[int] = None
    source_id: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    is_reconciled: Optional[bool] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    user_id: int
    category_id: Optional[int]
    source_id: Optional[int]
    description: str
    notes: Optional[str]
    amount: int
    transaction_type: str
    transaction_date: date
    is_reconciled: bool
    is_manually_categorized: bool
    categorized_by_ai: bool
    ai_confidence_score: Optional[int]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for transaction list response"""
    transactions: list[TransactionResponse]
    total: int
    limit: int
    offset: int


class TransactionSummaryResponse(BaseModel):
    """Schema for transaction summary statistics"""
    total_expenses: int
    total_income: int
    net: int
    transaction_count: int


# ============= Source Schemas =============

class SourceCreateRequest(BaseModel):
    """Schema for creating a source"""
    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., pattern="^(bank_account|credit_card|cash|digital_wallet|other)$")
    description: Optional[str] = None
    account_number_last4: Optional[str] = Field(None, min_length=4, max_length=4, pattern="^[0-9]{4}$")
    institution_name: Optional[str] = None
    current_balance: Optional[int] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None


class SourceUpdateRequest(BaseModel):
    """Schema for updating a source"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = Field(None, pattern="^(bank_account|credit_card|cash|digital_wallet|other)$")
    description: Optional[str] = None
    account_number_last4: Optional[str] = Field(None, min_length=4, max_length=4, pattern="^[0-9]{4}$")
    institution_name: Optional[str] = None
    current_balance: Optional[int] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class SourceResponse(BaseModel):
    """Schema for source response"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    source_type: str
    account_number_last4: Optional[str]
    institution_name: Optional[str]
    current_balance: Optional[int]
    color: Optional[str]
    icon: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Category Schemas =============

class CategoryCreateRequest(BaseModel):
    """Schema for creating a category"""
    name: str = Field(..., min_length=1, max_length=100)
    category_type: str = Field(..., pattern="^(expense|income)$")
    description: Optional[str] = None
    parent_id: Optional[int] = None
    matching_pattern: Optional[str] = None
    is_system: bool = False
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None


class CategoryUpdateRequest(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_type: Optional[str] = Field(None, pattern="^(expense|income)$")
    description: Optional[str] = None
    parent_id: Optional[int] = None
    matching_pattern: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    category_type: str
    parent_id: Optional[int]
    matching_pattern: Optional[str]
    is_system: bool
    color: Optional[str]
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Categorization Schemas =============

class CategorizeTransactionRequest(BaseModel):
    """Schema for categorizing a transaction"""
    force: bool = False


class BulkCategorizeRequest(BaseModel):
    """Schema for bulk categorization"""
    transaction_type: Optional[str] = Field(None, pattern="^(expense|income|transfer)$")
    force: bool = False
    limit: Optional[int] = Field(None, ge=1, le=10000)


class CategorizeResponse(BaseModel):
    """Schema for categorization response"""
    category_id: Optional[int]
    confidence: float
    manually_categorized: bool


class BulkCategorizeResponse(BaseModel):
    """Schema for bulk categorization response"""
    processed: int
    categorized: int
    uncategorized: int
    skipped: int


class CategorySuggestion(BaseModel):
    """Schema for category suggestion"""
    category_id: int
    category_name: str
    confidence: float


class CategorySuggestionsResponse(BaseModel):
    """Schema for category suggestions response"""
    suggestions: List[CategorySuggestion]


class UncategorizedCountResponse(BaseModel):
    """Schema for uncategorized count response"""
    count: int
    transaction_type: Optional[str]


class ManualCategorizeRequest(BaseModel):
    """Schema for manual categorization"""
    category_id: Optional[int] = None
