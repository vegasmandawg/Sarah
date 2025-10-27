"""
Database configuration for the Character Manager
Reuses tables from Memory Subsystem database
"""

import os
from datetime import datetime
from contextlib import asynccontextmanager

from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Text, DateTime, ForeignKey,
    Index
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    poolclass=NullPool
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create metadata
metadata = MetaData()

# Reference existing tables from the shared database
users_table = Table(
    "users",
    metadata,
    Column("user_id", String(255), primary_key=True),
    Column("username", String(255), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    autoload_with=None  # Will be loaded from existing DB
)

characters_table = Table(
    "characters",
    metadata,
    Column("character_id", String(255), primary_key=True),
    Column("user_id", String(255), ForeignKey("users.user_id"), nullable=False),
    Column("name", String(255), nullable=False),
    Column("persona_prompt", Text, nullable=False),
    Column("voice_id", String(255)),
    Column("appearance_seed", String(255)),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    autoload_with=None
)


async def init_db():
    """
    Initialize database connection
    Tables should already exist from Memory Subsystem
    """
    async with engine.begin() as conn:
        # Try to reflect existing tables
        try:
            await conn.run_sync(metadata.reflect)
            logger.info("Connected to existing database tables")
        except Exception as e:
            logger.warning(f"Could not reflect tables: {e}")
            # Create tables if they don't exist
            await conn.run_sync(metadata.create_all)
            logger.info("Created database tables")


@asynccontextmanager
async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Import logger after defining it
import logging
logger = logging.getLogger(__name__)
