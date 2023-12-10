from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import UserCRUD
from src.database.schemas import FriendshipCreate, PrivateUser
from fastapi_async_sqlalchemy import db

router = APIRouter()


@router.get("/register")
async def register(
    mail: str, name: str, password_hash: str
):
    # TODO: change this code (it was added just for local development)
    user_data = PrivateUser(mail=mail, name=name, password_hash=password_hash)
    user = await UserCRUD.create_user(user_data, db)

    return user.model_dump()


@router.post("/login")
async def login():
    pass


@router.post(
    "/add_friend",
    summary="Add friend",
    description="Add a friend for the user.",
    response_model=dict,
    responses={
        201: {
            "description": "Friend added successfully",
            "content": {"application/json": {}},
        },
        400: {
            "description": "Bad request or users are already friends",
            "content": {"application/json": {}},
        },
    },
)
async def add_friend(
    user_mail: str, friend_mail: str
):
    try:
        await UserCRUD.add_friend(user_mail, friend_mail, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": f"Friend {friend_mail} added successfully"}


@router.delete("/remove_friend")
async def remove_friend(
    user_mail: str, friend_mail: str
):
    try:
        await UserCRUD.remove_friend(user_mail, friend_mail, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": f"Friend {friend_mail} removed successfully"}


@router.get(
    "/user_friends",
    summary="Get user friends",
    description="Retrieve a list of friends for the user.",
    response_model=dict,
    responses={
        200: {
            "description": "Friends retrieved successfully",
            "content": {"application/json": {}},
        },
        404: {"description": "User not found", "content": {"application/json": {}}},
    },
)
async def user_friends(user_mail: str):
    user = await UserCRUD.get_user(user_mail, db)
    return {"friends": [friend.to_dict() for friend in user.friendships]}


@router.get(
    "/mutual_groups",
    summary="Get mutual groups",
    description="Retrieve a list of groups that are mutual between two friends.",
    response_model=dict,
    responses={
        200: {
            "description": "Mutual groups retrieved successfully",
            "content": {"application/json": {}},
        },
        404: {
            "description": "Users are not friends or not found",
            "content": {"application/json": {}},
        },
    },
)
async def mutual_groups(
    user_mail: str, friend_mail: str
):
    if not await UserCRUD.check_if_friends(user_mail, friend_mail, db):
        raise HTTPException(status_code=404, detail="Users are not friends")

    user = await UserCRUD.get_user(user_mail, db)
    friend = await UserCRUD.get_user(friend_mail, db)

    same_groups = [group.to_dict() for group in user.groups if group in friend.groups]

    return {"mutual_groups": same_groups}
