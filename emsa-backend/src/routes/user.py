from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.crud.user import FriendCRUD, UserCRUD
from src.database.schemas import PrivateUser, PublicUser, UpdateUser
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


@router.put(
    "/update_account",
    status_code=status.HTTP_200_OK,
    summary="Update user account",
    description="Update the authenticated user account.",
    response_model=PublicUser,
    responses={
        status.HTTP_200_OK: {
            "description": "Account updated successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User account not found",
            "content": {"application/json": {}},
        },
    },
)
async def update_account(
    mail: EmailStr,
    update_data: UpdateUser,
    db: AsyncSession = Depends(get_db),
) -> PublicUser:
    try:
        updated_user = await UserCRUD.update_user(mail, update_data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return PublicUser(**updated_user.model_dump())


@router.delete(
    "/remove_account",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove user account",
    description="Remove the authenticated user account.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Account removed successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User account not found",
            "content": {"application/json": {}},
        },
    },
)
async def remove_account(
    mail: EmailStr,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await UserCRUD.get_user(mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    user_groups = await GroupCRUD.get_user_groups(mail, db)
    owned_groups = await GroupCRUD.get_user_owned_groups(mail, db)
    for owned_group_id in [group.id for group in owned_groups]:
        await GroupCRUD.delete_group(owned_group_id, db)
    for user_group_id in [
        group.id for group in user_groups if group not in owned_groups
    ]:
        await GroupCRUD.remove_user_from_group(user_group_id, mail, db)
    await UserCRUD.delete_user(mail, db)


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
