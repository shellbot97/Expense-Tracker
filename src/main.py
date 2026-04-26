"""
Personal Expense Tracker API
Privacy-first expense management system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.utils.exceptions import BaseAppException
from src.middleware.error_handler import app_exception_handler, generic_exception_handler

# Create FastAPI application
app = FastAPI(
    title="Personal Expense Tracker",
    description="Privacy-first expense management system with AI-augmented insights",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Personal Expense Tracker API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "active",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


# API Routers
from src.api import auth

app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])

# TODO: Add additional routers as features are implemented
# from src.api import transactions, categories, sources
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
# app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
# app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )
