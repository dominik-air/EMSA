from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.crud.user import FriendCRUD
from src.database.schemas import GroupCreate, GroupGet, MediaGet, MediaQuery, PublicUser
from src.database.session import get_db

router = APIRouter()


@router.post(
    "/create_group",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new group",
    description="Create a new group provided with a name and related owner user.",
    response_model=GroupGet,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Group created successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input",
            "content": {"application/json": {}},
        },
    },
)
async def create_group(
    group_info: GroupCreate,
    db: AsyncSession = Depends(get_db),
) -> GroupGet:
    try:
        group = await GroupCRUD.create_group(group_info, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return group


@router.post(
    "/add_group_members",
    status_code=status.HTTP_200_OK,
    summary="Add members to a group",
    description="Add members through list of emails related to app users to an existing group by group_id.",
    responses={
        status.HTTP_200_OK: {
            "description": "Members added successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Group not found",
            "content": {"application/json": {}},
        },
    },
)
async def add_group_members(
    group_id: int, members: list[EmailStr], db: AsyncSession = Depends(get_db)
) -> None:
    try:
        await GroupCRUD.add_users_to_group(group_id, members, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/remove_member",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from a group",
    description="Remove a member from an existing group by group_id.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Member removed successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Group or member not found",
            "content": {"application/json": {}},
        },
    },
)
async def remove_member(
    group_id: int, member_mail: EmailStr, db: AsyncSession = Depends(get_db)
) -> None:
    try:
        await GroupCRUD.remove_user_from_group(group_id, member_mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    user_mail: EmailStr, db: AsyncSession = Depends(get_db)
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
    user_mail: EmailStr, friend_mail: EmailStr, db: AsyncSession = Depends(get_db)
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
    response_model=list[MediaGet],
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
    group_id: int,
    search_query: MediaQuery = Depends(),
    db: AsyncSession = Depends(get_db),
) -> list[MediaGet]:
    try:
        return await MediaCRUD.get_media_by_group(
            group_id=group_id,
            query_params=search_query,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/remove_group",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a group",
    description="Remove an existing group by group_id.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Group removed successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Group not found",
            "content": {"application/json": {}},
        },
    },
)
async def remove_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await GroupCRUD.get_group(group_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    await GroupCRUD.delete_group(group_id, db)
