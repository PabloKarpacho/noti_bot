from sqlalchemy.ext.declarative import declarative_base
from bot.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
from contextlib import asynccontextmanager

db_semaphore = asyncio.Semaphore(150)

async_engine = create_async_engine(
    settings.db_postgres_url,
    pool_size=50,
    max_overflow=100,
    pool_timeout=120,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo_pool=True,
    pool_use_lifo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


@asynccontextmanager
async def get_db():
    async with db_semaphore:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
