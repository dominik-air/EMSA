from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.settings import settings

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
)
async_session_global = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    db = async_session_global()
    try:
        yield db
    finally:
        await db.close()
