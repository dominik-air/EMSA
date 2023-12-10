from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.crud.user import FriendCRUD
from src.database.schemas import GroupGet, MediaList, PublicUser
from src.database.session import get_db

router = APIRouter()


@router.get(
    "/user_groups",
    summary="Get user groups",
    description="Retrieve a list of groups that the user is a part of.",
    response_model=list[GroupGet],
    responses={
        status.HTTP_200_OK: {
            "description": "Groups retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {"application/json": {}},
        },
    },
)
async def user_groups(
    user_mail: str, db: AsyncSession = Depends(get_db)
) -> list[GroupGet]:
    try:
        groups = await GroupCRUD.get_user_groups(user_mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return groups


@router.get(
    "/mutual_groups",
    summary="Get mutual groups",
    description="Retrieve a list of groups that are mutual between two friends.",
    response_model=list[GroupGet],
    responses={
        status.HTTP_200_OK: {
            "description": "Mutual groups retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Users are not friends or not found",
            "content": {"application/json": {}},
        },
    },
)
async def mutual_groups(
    user_mail: str, friend_mail: str, db: AsyncSession = Depends(get_db)
):
    if not await FriendCRUD.check_if_friends(user_mail, friend_mail, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users are not friends"
        )

    groups_of_user = await GroupCRUD.get_user_groups(user_mail, db)
    groups_of_friend = await GroupCRUD.get_user_groups(friend_mail, db)

    return [group for group in groups_of_user if group in groups_of_friend]


@router.get(
    "/group_members",
    summary="Get group members",
    description="Retrieve a list of members related to group by group_id.",
    response_model=list[PublicUser],
    responses={
        status.HTTP_200_OK: {
            "description": "Group members retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Group not found",
            "content": {"application/json": {}},
        },
    },
)
async def group_members(
    group_id: int, db: AsyncSession = Depends(get_db)
) -> list[PublicUser]:
    try:
        return await GroupCRUD.get_users_in_group(group_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/group_content",
    summary="Get group content",
    description="Retrieve a list of media related to group by group_id.",
    response_model=list[MediaList],
    responses={
        status.HTTP_200_OK: {
            "description": "Group media retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Group not found",
            "content": {"application/json": {}},
        },
    },
)
async def group_content(
    group_id: int, db: AsyncSession = Depends(get_db)
) -> list[MediaList]:
    try:
        return await MediaCRUD.get_media_by_group(group_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
