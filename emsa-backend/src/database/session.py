from databases import Database
from sqlalchemy.ext.asyncio import create_async_engine

from src.database.models import Base
from src.database.settings import settings

database = Database(settings.DATABASE_URL)
engine = create_async_engine(settings.DATABASE_URL)


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
