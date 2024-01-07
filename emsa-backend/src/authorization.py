from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JOSEError, JWTError, jwt
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash, generate_password_hash

from src.crud.user import UserCRUD
from src.database.schemas import PrivateUser, PublicUser, TokenData
from src.database.session import get_db
from src.exceptions import IncorrectUsernameOrPassword
from src.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(hashed_password: str, plain_password: str):
    return check_password_hash(pwhash=hashed_password, password=plain_password)


def get_password_hash(password: str):
    return generate_password_hash(password)


async def authenticate_user(
    mail: EmailStr, password: str, db: AsyncSession
) -> PrivateUser:
    user = await UserCRUD.get_user(mail, db)
    if not user:
        raise IncorrectUsernameOrPassword
    if not verify_password(user.password_hash, password):
        raise IncorrectUsernameOrPassword
    return user


async def create_access_token(
    data: dict, db: AsyncSession, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        key=settings.AUTH_SECRET_KEY,
        algorithm=settings.AUTH_ALGORITHM,
    )

    token = await UserCRUD.create_token(encoded_jwt, db)
    return token.access_token


def decode_jwt_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
    except JOSEError:
        raise JWTError("Invalid credentials")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> PrivateUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, key=settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
        user_mail: str = payload.get("sub")
        if not user_mail:
            raise credentials_exception
        token_data = TokenData(user_mail=user_mail)
    except JWTError:
        raise credentials_exception
    try:
        user = await UserCRUD.get_user(token_data.user_mail, db)
    except ValueError:
        raise credentials_exception

    db_token = await UserCRUD.get_token(user.mail, db)
    if not db_token or not db_token.is_active or db_token.access_token != token:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[PrivateUser, Depends(get_current_user)]
) -> PublicUser:
    # TODO: remove when users soft delete will be done
    # if current_user.disabled:
    # raise HTTPException(status_code=400, detail="Inactive user")
    return PublicUser(**current_user.model_dump())
