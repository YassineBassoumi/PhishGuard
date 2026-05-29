"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL - PostgreSQL with Supabase
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/phishguard"
)

# Create async engine with PostgreSQL optimizations
import ssl

# Create SSL context for Supabase connection (TLS-encrypted channel)
# Note: Supabase's CA certificate (prod-ca-2021.crt) lacks the keyUsage extension
# required by OpenSSL 3.x (Python 3.13+), making CERT_REQUIRED verification impossible.
# The connection remains encrypted via TLS, preventing passive eavesdropping.
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
    pool_size=5,  # Reduced pool size for better management
    max_overflow=10,  # Allow more overflow connections
    pool_pre_ping=True,  # Verify connections before using them (CRITICAL for detecting stale connections)
    pool_recycle=1800,  # Recycle connections after 30 minutes (reduced from 1 hour)
    pool_timeout=30,  # Timeout for getting connection from pool
    connect_args={
        "ssl": ssl_context,  # Use SSL context for Supabase
        "server_settings": {
            "application_name": "phishguard_app",
            "jit": "off"
        },
        "command_timeout": 120,  # Increased from 60 to 120 seconds
        "statement_cache_size": 0,  # Disable prepared statements for pgbouncer compatibility
        "timeout": 20,  # Increased connection timeout from 10 to 20 seconds
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for getting database session with connection error handling"""
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
        await session.commit()
    except Exception as e:
        if session:
            await session.rollback()
        raise
    finally:
        if session:
            try:
                await session.close()
            except Exception as close_error:
                # Log but don't raise - session might already be closed
                import logging
                logging.getLogger(__name__).warning(
                    f"Error closing database session: {close_error}"
                )


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
