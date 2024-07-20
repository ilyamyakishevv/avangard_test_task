from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from models import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./currencies_pairs.db"

async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, future=True, echo=True)

async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_database():
    async with async_engine.begin() as conn:
        if not await conn.run_sync(async_engine.dialect.has_table, conn, "currencies_pairs"):
            await conn.run_sync(Base.metadata.create_all)
