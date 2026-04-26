"""
Database connection and session management
SQLite with SQLAlchemy
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": settings.SQLITE_TIMEOUT},
    echo=settings.is_development,  # Log SQL in development
)


# Enable SQLite pragmas for better performance and foreign key support
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas on connection"""
    cursor = dbapi_conn.cursor()
    if settings.SQLITE_PRAGMA_FOREIGN_KEYS:
        cursor.execute("PRAGMA foreign_keys=ON")
    if settings.SQLITE_PRAGMA_WAL_MODE:
        cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session
    Use with FastAPI Depends()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database (create all tables)
    Call this from migration scripts or first run
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Drop all tables (use with caution!)
    Only for development/testing
    """
    if not settings.is_development:
        raise RuntimeError("Cannot drop tables in production!")
    Base.metadata.drop_all(bind=engine)
