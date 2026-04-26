"""
Custom exception classes
Provides consistent error handling across the application
"""


class BaseAppException(Exception):
    """Base exception for all application exceptions"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Authentication & Authorization Exceptions
class AuthenticationError(BaseAppException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(BaseAppException):
    """Raised when user lacks permission"""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""

    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired"""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid"""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


# Resource Exceptions
class NotFoundError(BaseAppException):
    """Raised when requested resource doesn't exist"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class AlreadyExistsError(BaseAppException):
    """Raised when trying to create a resource that already exists"""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


# Validation Exceptions
class ValidationError(BaseAppException):
    """Raised when input validation fails"""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class InvalidDateRangeError(ValidationError):
    """Raised when date range is invalid"""

    def __init__(self, message: str = "Invalid date range"):
        super().__init__(message)


class InvalidAmountError(ValidationError):
    """Raised when amount is invalid"""

    def __init__(self, message: str = "Invalid amount"):
        super().__init__(message)


# Database Exceptions
class DatabaseError(BaseAppException):
    """Raised when database operation fails"""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""

    def __init__(self, message: str = "Could not connect to database"):
        super().__init__(message)


# File Processing Exceptions
class FileProcessingError(BaseAppException):
    """Raised when file processing fails"""

    def __init__(self, message: str = "File processing failed"):
        super().__init__(message, status_code=400)


class UnsupportedFileTypeError(FileProcessingError):
    """Raised when file type is not supported"""

    def __init__(self, message: str = "Unsupported file type"):
        super().__init__(message)


class FileParseError(FileProcessingError):
    """Raised when file parsing fails"""

    def __init__(self, message: str = "Could not parse file"):
        super().__init__(message)


# AI Service Exceptions
class AIServiceError(BaseAppException):
    """Raised when AI service operation fails"""

    def __init__(self, message: str = "AI service error"):
        super().__init__(message, status_code=503)


class AIServiceUnavailableError(AIServiceError):
    """Raised when AI service is unavailable"""

    def __init__(self, message: str = "AI service is not available"):
        super().__init__(message)


class AIQuotaExceededError(AIServiceError):
    """Raised when AI service quota is exceeded"""

    def __init__(self, message: str = "AI service quota exceeded"):
        super().__init__(message)
