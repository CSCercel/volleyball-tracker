from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


if settings.environment == "development":
    engine_args = {}
else:
    engine_args = {
        "connect_args" : {
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0
        },
        "pool_recycle": 300,
        "pool_pre_ping": True
    }

engine = create_async_engine(settings.database_url, **engine_args)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
