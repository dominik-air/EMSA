import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

app.include_router(user.router, tags=["user"])
app.include_router(group.router, tags=["group"])
app.include_router(health_check.router, tags=["health"])
