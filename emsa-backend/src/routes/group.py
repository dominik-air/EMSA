from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from fastapi_async_sqlalchemy import db


router = APIRouter()


@router.get(
    "/user_groups",
    summary="Get user groups",
    description="Retrieve a list of groups that the user is a part of.",
    response_model=dict,
    responses={
        200: {
            "description": "Groups retrieved successfully",
            "content": {"application/json": {}},
        },
        404: {"description": "User not found", "content": {"application/json": {}}},
    },
)
async def user_groups():
    user_mail = "abc@gmail.com"
    try:
        groups = await GroupCRUD.get_user_groups(user_mail)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"groups": [group.model_dump() for group in groups]}


@router.get("/group_members")
async def group_members(group_id: int):
    try:
        users = await GroupCRUD.get_users_in_group(group_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"group_members": [user.model_dump() for user in users]}


@router.get("/group_content")
async def group_content():
    pass
