from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.scripts import add_data_for_local_dev
from src.settings import settings
from src.crud.user import UserCRUD

router = APIRouter()


@router.get(
    "/heartbeat",
    summary="Heartbeat Endpoint",
    description="Check the status of the service. Returns 'alive' if the service is running.",
    response_model=dict,
    responses={
        200: {"description": "Service is alive", "content": {"application/json": {}}}
    },
)
async def heartbeat(db: AsyncSession = Depends(get_db)):
    if settings.ENV == "local-dev":
        if not await UserCRUD.get_users(db):
            data = await add_data_for_local_dev(db)
            return data
    return {"status": "alive"}


@router.get(
    "/health",
    summary="Health Endpoint",
    description="Check the overall health status of the service. Returns 'healthy' if the service is healthy.",
    response_model=dict,
    responses={
        200: {"description": "Service is healthy", "content": {"application/json": {}}}
    },
)
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
