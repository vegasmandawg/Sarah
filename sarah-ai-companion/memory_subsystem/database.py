"""
Database configuration and models for the Memory Subsystem
"""

import os
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Text, DateTime, ForeignKey,
    Index, UniqueConstraint
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from config import settings

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    poolclass=NullPool  # Use NullPool for async connections
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create metadata
metadata = MetaData()

# Define tables
users_table = Table(
    "users",
    metadata,
    Column("user_id", String(255), primary_key=True),
    Column("username", String(255), nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Index("idx_users_username", "username")
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
    Index("idx_characters_user_id", "user_id")
)

key_facts_table = Table(
    "key_facts",
    metadata,
    Column("fact_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String(255), ForeignKey("users.user_id"), nullable=False),
    Column("character_id", String(255), ForeignKey("characters.character_id"), nullable=False),
    Column("fact_type", String(50), nullable=False),  # preference, event, relationship, etc.
    Column("fact_key", String(255), nullable=False),
    Column("fact_value", Text, nullable=False),
    Column("timestamp", DateTime, default=datetime.utcnow),
    UniqueConstraint("user_id", "character_id", "fact_key", name="uq_user_character_fact"),
    Index("idx_facts_user_character", "user_id", "character_id"),
    Index("idx_facts_type", "fact_type"),
    Index("idx_facts_timestamp", "timestamp")
)

conversation_sessions_table = Table(
    "conversation_sessions",
    metadata,
    Column("session_id", String(255), primary_key=True),
    Column("user_id", String(255), ForeignKey("users.user_id"), nullable=False),
    Column("character_id", String(255), ForeignKey("characters.character_id"), nullable=False),
    Column("started_at", DateTime, default=datetime.utcnow),
    Column("ended_at", DateTime),
    Column("message_count", Integer, default=0),
    Index("idx_sessions_user_character", "user_id", "character_id"),
    Index("idx_sessions_started", "started_at")
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(metadata.create_all)


async def drop_db():
    """Drop all database tables (use with caution)"""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


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


# Database helper functions
async def ensure_user_exists(db: AsyncSession, user_id: str, username: str) -> None:
    """Ensure a user exists in the database"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(users_table).where(users_table.c.user_id == user_id)
    )
    
    if not result.first():
        await db.execute(
            users_table.insert().values(
                user_id=user_id,
                username=username,
                created_at=datetime.utcnow()
            )
        )
        await db.commit()


async def ensure_character_exists(
    db: AsyncSession,
    character_id: str,
    user_id: str,
    name: str,
    persona_prompt: str
) -> None:
    """Ensure a character exists in the database"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(characters_table).where(characters_table.c.character_id == character_id)
    )
    
    if not result.first():
        await db.execute(
            characters_table.insert().values(
                character_id=character_id,
                user_id=user_id,
                name=name,
                persona_prompt=persona_prompt,
                created_at=datetime.utcnow()
            )
        )
        await db.commit()
