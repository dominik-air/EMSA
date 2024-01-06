from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.authorization import (
    authenticate_user,
    create_access_token,
    decode_jwt_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from src.crud.user import UserCRUD
from src.database.schemas import PrivateUser
from src.exceptions import IncorrectUsernameOrPassword
from src.settings import settings


@pytest_asyncio.fixture
async def mock_user(db_session: AsyncSession):
    password = "password123"
    user_data = {
        "mail": "test@example.com",
        "password_hash": get_password_hash(password),
        "name": "Test User",
    }
    user = PrivateUser(**user_data)
    return await UserCRUD.create_user(user, db_session)


@pytest.mark.asyncio
async def test_verify_password():
    hashed_password = get_password_hash("password123")
    assert verify_password(hashed_password, "password123")
    assert not verify_password(hashed_password, "password321")


@pytest.mark.asyncio
async def test_authenticate_user_success(
    db_session: AsyncSession, mock_user: PrivateUser
):
    user = await authenticate_user(mock_user.mail, "password123", db_session)
    assert user == mock_user


@pytest.mark.asyncio
async def test_authenticate_user_failure(
    db_session: AsyncSession, mock_user: PrivateUser
):
    with pytest.raises(IncorrectUsernameOrPassword):
        await authenticate_user(mock_user.mail, "wrongpassword", db_session)


@pytest.mark.asyncio
async def test_create_access_token(db_session: AsyncSession, mock_user: PrivateUser):
    data = {"sub": mock_user.mail}
    expires_delta = timedelta(minutes=15)
    access_token = await create_access_token(data, db_session, expires_delta)
    decoded_token = decode_jwt_token(access_token)
    assert decoded_token["sub"] == mock_user.mail


@pytest.mark.asyncio
async def test_decode_jwt_token():
    data = {"sub": "test@example.com"}
    access_token = jwt.encode(
        data, key=settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM
    )
    decoded_token = decode_jwt_token(access_token)
    assert decoded_token["sub"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_success(
    db_session: AsyncSession, mock_user: PrivateUser
):
    delta = timedelta(minutes=999)
    await create_access_token(
        data={"sub": mock_user.mail},
        db=db_session,
        expires_delta=delta,
    )
    access_token = jwt.encode(
        {"sub": mock_user.mail, "exp": datetime.now() + delta},
        key=settings.AUTH_SECRET_KEY,
        algorithm=settings.AUTH_ALGORITHM,
    )
    user = await get_current_user(access_token, db_session)
    assert user == mock_user


@pytest.mark.asyncio
async def test_get_current_user_failure(
    db_session: AsyncSession, mock_user: PrivateUser
):
    # Token with incorrect user_mail
    access_token = jwt.encode(
        {"sub": "wrong@example.com", "exp": 9999999999},
        key=settings.AUTH_SECRET_KEY,
        algorithm=settings.AUTH_ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(access_token, db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
