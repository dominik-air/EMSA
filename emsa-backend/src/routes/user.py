from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.authorization import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
from src.crud.friend import FriendCRUD
from src.crud.group import GroupCRUD
from src.crud.user import UserCRUD
from src.database.schemas import FriendRequestGet, PrivateUser, PublicUser, UpdateUser
from src.database.session import get_db
from src.exceptions import IncorrectUsernameOrPassword
from src.routes.contracts import (
    AddFriendRequest,
    GetPendingRequests,
    GetSentRequests,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from src.settings import settings

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Register a new user.",
    response_model=PublicUser,
    responses={
        status.HTTP_201_CREATED: {
            "description": "User registered successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request",
            "content": {"application/json": {}},
        },
        status.HTTP_409_CONFLICT: {
            "description": "User already exists",
            "content": {"application/json": {}},
        },
    },
)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> PublicUser:
    try:
        user = await UserCRUD.get_user(user_data.mail, db)
    except ValueError:
        user = None
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    password_hash = get_password_hash(user_data.password)
    user_db_data = PrivateUser(
        **user_data.model_dump(exclude={"password"}), password_hash=password_hash
    )

    try:
        user = await UserCRUD.create_user(user_db_data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return PublicUser(**user.model_dump())


@router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Register a new user.",
    response_model=TokenResponse,
    responses={
        status.HTTP_201_CREATED: {
            "description": "User registered successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Incorrect username or password or user does not exist",
            "content": {"application/json": {}},
        },
    },
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        await UserCRUD.get_user(request.mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    try:
        user = await authenticate_user(request.mail, request.password, db)
    except IncorrectUsernameOrPassword as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail,
        )

    access_token_expires = timedelta(minutes=settings.AUTH_TOKEN_EXPIRE_MIN)
    access_token = await create_access_token(
        data={"sub": user.mail},
        db=db,
        expires_delta=access_token_expires,
    )
    return TokenResponse(**{"access_token": access_token})


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Logout the user by invalidating the access token.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "User logged out successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized or invalid token",
            "content": {"application/json": {}},
        },
    },
)
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> None:
    await UserCRUD.deactivate_token(current_user, db)


@router.get(
    "/user_details",
    status_code=status.HTTP_200_OK,
    summary="Get user account details",
    description="Get user account details like name and email.",
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
async def user_details(
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> PublicUser:
    try:
        user = await UserCRUD.get_user(current_user.mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return PublicUser(**user.model_dump())


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
    update_data: UpdateUser,
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> PublicUser:
    try:
        updated_user = await UserCRUD.update_user(current_user.mail, update_data, db)
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
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> None:
    try:
        await UserCRUD.get_user(current_user.mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    user_groups = await GroupCRUD.get_user_groups(current_user.mail, db)
    owned_groups = await GroupCRUD.get_user_owned_groups(current_user.mail, db)
    for owned_group_id in [group.id for group in owned_groups]:
        await GroupCRUD.delete_group(owned_group_id, db)
    for user_group_id in [
        group.id for group in user_groups if group not in owned_groups
    ]:
        await GroupCRUD.remove_user_from_group(user_group_id, current_user.mail, db)
    await UserCRUD.delete_user(current_user.mail, db)


@router.post(
    "/create_friend_request",
    status_code=status.HTTP_201_CREATED,
    summary="Create friend request",
    description="Send a friend request to another user.",
    response_model=FriendRequestGet,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Friend request sent successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad request or friend request already sent",
            "content": {"application/json": {}},
        },
    },
)
async def create_friend_request(
    body: AddFriendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> FriendRequestGet:
    try:
        return await FriendCRUD.create_friend_request(
            sender_mail=current_user.mail,
            receiver_mail=body.friend_mail,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/pending_friend_requests",
    summary="Get pending friend requests",
    description="Retrieve a list of pending friend requests for the user.",
    response_model=list[GetPendingRequests],
    responses={
        status.HTTP_200_OK: {
            "description": "Pending friend requests retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found or no pending friend requests",
            "content": {"application/json": {}},
        },
    },
)
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> list[GetPendingRequests]:
    try:
        pending_requests = await FriendCRUD.get_pending_requests(current_user.mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return pending_requests


@router.get(
    "/sent_friend_requests",
    summary="Get sent friend requests",
    description="Retrieve a list of sent friend requests by the user.",
    response_model=list[GetSentRequests],
    responses={
        status.HTTP_200_OK: {
            "description": "Sent friend requests retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found or no sent friend requests",
            "content": {"application/json": {}},
        },
    },
)
async def get_sent_requests(
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> list[GetSentRequests]:
    try:
        sent_requests = await FriendCRUD.get_sent_requests(current_user.mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return sent_requests


@router.delete(
    "/decline_friend_request/{mail}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove friend sent friend requests",
    description="Remove friend request received by current user from {mail}.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Sent friend requests retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found or no sent friend requests",
            "content": {"application/json": {}},
        },
    },
)
async def decline_friend_request(
    mail: EmailStr,
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> None:
    try:
        await FriendCRUD.handle_delete_request(
            receiver_mail=current_user.mail,
            sender_mail=mail,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    body: AddFriendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> None:
    pending_requests = await FriendCRUD.get_pending_requests(current_user.mail, db)
    if not any(request.mail == body.friend_mail for request in pending_requests):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request wasn't sent"
        )
    try:
        await FriendCRUD.add_friend(current_user.mail, body.friend_mail, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/remove_friend/{friend_mail}",
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
    friend_mail: EmailStr,
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> None:
    if not await FriendCRUD.check_if_friends(current_user.mail, friend_mail, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users are not friends"
        )
    try:
        await FriendCRUD.remove_friend(current_user.mail, friend_mail, db)
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
async def get_user_friends(
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> list[PublicUser]:
    user = await UserCRUD.get_user(current_user.mail, db)
    return await FriendCRUD.get_user_friends(user.mail, db)
