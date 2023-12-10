import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from src.settings import settings

from src.database.session import Base, engine
from src.routes import group, health_check, user

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.DATABASE_URL,
    engine_args={              # engine arguments example
        "echo": True,          # print all SQL statements
        "pool_pre_ping": True, # feature will normally emit SQL equivalent to “SELECT 1” each time a connection is checked out from the pool
        "pool_size": 5,        # number of connections to keep open at a time
        "max_overflow": 10,    # number of connections to allow to be opened above pool_size
    },
)

app.include_router(user.router, tags=["user"])
app.include_router(group.router, tags=["group"])
app.include_router(health_check.router, tags=["health"])
