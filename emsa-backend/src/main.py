import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.session import create_database, database
from src.routes import health_check, user

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_database()
    await database.connect()

    yield

    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(user.router, tags=["user"])
app.include_router(health_check.router, tags=["health"])
