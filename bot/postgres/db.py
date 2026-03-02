from sqlalchemy.ext.declarative import declarative_base
from bot.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
from contextlib import asynccontextmanager

from bot.common.logging import get_logger

logger = get_logger()

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
logger.info("Async PostgreSQL engine initialized")

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
        logger.debug("Acquired DB semaphore")
        async with AsyncSessionLocal() as session:
            try:
                logger.debug("DB session opened")
                yield session
            finally:
                logger.debug("Closing DB session")
                await session.close()
