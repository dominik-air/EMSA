from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import FriendCRUD, UserCRUD
from src.database.schemas import PrivateUser, PublicUser
from src.database.session import get_db

router = APIRouter()


@router.post("/register")
async def register(
    mail: EmailStr, name: str, password_hash: str, db: AsyncSession = Depends(get_db)
):
    # TODO: change this code in issue-31 (it was added just for local development)
    user_data = PrivateUser(mail=mail, name=name, password_hash=password_hash)
    user = await UserCRUD.create_user(user_data, db)

    return user.model_dump()


@router.post("/login")
async def login():
    pass


@router.post(
    "/add_friend",
    status_code=status.HTTP_201_CREATED,
    summary="Add friend",
    description="Add a friend for the user.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Friend added successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request or users are already friends",
            "content": {"application/json": {}},
        },
    },
)
async def add_friend(
    user_mail: EmailStr, friend_mail: EmailStr, db: AsyncSession = Depends(get_db)
) -> None:
    try:
        await FriendCRUD.add_friend(user_mail, friend_mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/remove_friend",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove friend",
    description="Add a friend for the passed user.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Friend removed successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Users are not friends",
            "content": {"application/json": {}},
        },
    },
)
async def remove_friend(
    user_mail: EmailStr, friend_mail: EmailStr, db: AsyncSession = Depends(get_db)
) -> None:
    if not await FriendCRUD.check_if_friends(user_mail, friend_mail, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users are not friends"
        )
    try:
        await FriendCRUD.remove_friend(user_mail, friend_mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/user_friends",
    summary="Get user friends",
    description="Retrieve a list of friends for the user.",
    response_model=list[PublicUser],
    responses={
        status.HTTP_200_OK: {
            "description": "Friends retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {"application/json": {}},
        },
    },
)
async def user_friends(
    user_mail: EmailStr, db: AsyncSession = Depends(get_db)
) -> list[PublicUser]:
    user = await UserCRUD.get_user(user_mail, db)
    return await FriendCRUD.get_user_friends(user.mail, db)
