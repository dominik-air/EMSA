from fastapi import FastAPI

from src.routes import health_check, user

app = FastAPI()

app.include_router(user.router, tags=["user"])
app.include_router(health_check.router, tags=["health"])
