"""Database connection and session management

This module handles:
- SQLAlchemy engine initialization
- Database session creation and dependency injection
- Connection pooling configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

# Create database engine with connection pooling
# NullPool: No connection pooling (useful for development/testing with SQLite)
# QueuePool: Connection pool with queue (recommended for production PostgreSQL)

if settings.ENV == "production":
    # Production: Use QueuePool for PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Test connections before using
        echo=False,
    )
else:
    # Development/Testing: Use NullPool for flexibility
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """
    Dependency function to get database session.
    
    Used in FastAPI endpoints with Depends() to inject database session.
    
    Example:
    ```python
    @router.get("/users")
    async def get_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
    ```
    
    The session is automatically closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    
    Creates all tables defined in SQLAlchemy models.
    Should be called once during application startup.
    
    Usage in main.py:
    ```python
    from app.database import init_db
    
    @app.on_event("startup")
    async def startup():
        init_db()
    ```
    """
    from app.models.user import Base as UserBase
    from app.models.video import Base as VideoBase
    
    # Create all tables
    UserBase.metadata.create_all(bind=engine)
    VideoBase.metadata.create_all(bind=engine)
    print("✅ Database tables initialized")


def drop_db():
    """
    Drop all database tables.
    
    WARNING: This is destructive and should only be used in development.
    Deletes all data from the database.
    """
    from app.models.user import Base as UserBase
    from app.models.video import Base as VideoBase
    
    UserBase.metadata.drop_all(bind=engine)
    VideoBase.metadata.drop_all(bind=engine)
    print("⚠️ Database tables dropped")
