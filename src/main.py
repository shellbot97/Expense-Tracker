"""
Personal Expense Tracker API
Privacy-first expense management system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.utils.exceptions import BaseAppException
from src.middleware.error_handler import app_exception_handler, generic_exception_handler

# API Metadata
tags_metadata = [
    {
        "name": "authentication",
        "description": "User registration, login, and token management. All endpoints except registration and login require Bearer token authentication.",
    },
    {
        "name": "transactions",
        "description": "Manage financial transactions (expenses, income, transfers). Supports CRUD operations, filtering, and pagination.",
    },
    {
        "name": "sources",
        "description": "Manage financial sources (bank accounts, credit cards, cash, etc.). Each transaction can be linked to a source.",
    },
    {
        "name": "categories",
        "description": "Manage transaction categories (groceries, rent, salary, etc.). Supports hierarchical categories and custom rules.",
    },
    {
        "name": "categorization",
        "description": "Automatic transaction categorization using rule-based engine. Can be augmented with AI (optional).",
    },
]

# Create FastAPI application
app = FastAPI(
    title="Personal Expense Tracker API",
    description="""
    ## Privacy-First Expense Management System
    
    A comprehensive expense tracking system with AI-augmented insights, designed for privacy and local-first operation.
    
    ### Key Features
    
    * **Authentication**: JWT-based secure authentication
    * **Transactions**: Full CRUD operations with filtering and pagination
    * **Categories**: Hierarchical category management with auto-categorization
    * **Sources**: Track expenses across multiple accounts and sources
    * **Analytics**: Spending insights, trends, and anomaly detection
    * **Import**: CSV/Excel statement parsing with duplicate detection
    * **Privacy**: Local-first design, optional AI features, user data control
    
    ### Authentication
    
    Most endpoints require authentication using JWT Bearer tokens:
    
    1. Register a new account: `POST /api/v1/auth/register`
    2. Login to get access token: `POST /api/v1/auth/login`
    3. Include token in requests: `Authorization: Bearer <your_token>`
    
    ### Getting Started
    
    1. **Register**: Create a user account
    2. **Login**: Obtain JWT access token
    3. **Create Categories**: Set up your expense categories
    4. **Add Sources**: Configure your bank accounts/credit cards
    5. **Import or Create Transactions**: Start tracking expenses
    6. **Analyze**: Use analytics endpoints for insights
    
    ### Error Handling
    
    All endpoints follow consistent error response format:
    
    ```json
    {
        "error": "Error message description"
    }
    ```
    
    Standard HTTP status codes are used:
    * 200: Success
    * 201: Created
    * 400: Bad Request (validation error)
    * 401: Unauthorized (missing/invalid token)
    * 404: Not Found
    * 409: Conflict (duplicate resource)
    * 500: Internal Server Error
    
    ### Rate Limiting
    
    Currently no rate limiting is enforced. Consider implementing rate limiting for production deployments.
    
    ### Data Privacy
    
    This API is designed for single-user, local-first operation. All data is stored locally in SQLite. AI features are optional and can use local models (Ollama) to maintain privacy.
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "Expense Tracker Support",
        "url": "https://github.com/your-repo/expense-tracker",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Exception handlers
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Personal Expense Tracker API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "status": "active",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns current health status and environment information.
    Use this endpoint for Docker health checks and monitoring systems.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
    }


# API Routers
from src.api import auth, transactions, sources, categories, categorization

app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(categorization.router, prefix="/api/v1/categorization", tags=["categorization"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )
