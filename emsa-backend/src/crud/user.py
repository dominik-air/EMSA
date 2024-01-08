from jose import jwt
from pydantic import EmailStr
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Friendship, Token, User
from src.database.schemas import (
    PrivateUser,
    PublicUser,
    TokenCreate,
    TokenGet,
    UpdateUser,
)
from src.settings import settings


class UserCRUD:
    @staticmethod
    async def create_user(user: PrivateUser, db: AsyncSession) -> PrivateUser:
        query = insert(User).returning(User).values(user.model_dump())
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return PrivateUser(**row)
        else:
            raise ValueError("Failed to create user. No row returned.")

    @staticmethod
    async def get_user(user_mail: EmailStr, db: AsyncSession) -> PrivateUser:
        query = select(User).where(User.mail == user_mail)
        result = await db.execute(query)
        user_data = result.fetchone()

        if user_data:
            return PrivateUser(**user_data[0].to_dict())
        else:
            raise ValueError(f"No user found with mail: {user_mail}")

    @staticmethod
    async def get_users(db: AsyncSession) -> list[PublicUser]:
        query = select(User)
        result = await db.execute(query)
        users_data = result.fetchall()
        return [PublicUser(**user[0].to_dict()) for user in users_data]

    @staticmethod
    async def update_user(
        mail: EmailStr, user: UpdateUser, db: AsyncSession
    ) -> PrivateUser:
        query = (
            update(User)
            .values(name=user.name, password_hash=user.password_hash)
            .returning(User)
            .where(User.mail == mail)
        )
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return PrivateUser(**row)
        else:
            raise ValueError(f"No user found with mail: {mail}")

    @staticmethod
    async def delete_user(mail: EmailStr, db: AsyncSession) -> None:
        await db.execute(
            delete(Friendship).where(
                or_(Friendship.user_mail == mail, Friendship.friend_mail == mail)
            )
        )
        await db.execute(delete(Token).where(Token.user_mail == mail))
        await db.execute(delete(User).where(User.mail == mail))

    @staticmethod
    async def create_token(access_token: str, db: AsyncSession) -> TokenGet:
        decoded_token = jwt.decode(
            access_token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
        user_mail = decoded_token["sub"]

        if await UserCRUD.get_token(user_mail, db):
            await db.execute(delete(Token).where(Token.user_mail == user_mail))

        token_data = TokenCreate(
            access_token=access_token,
            user_mail=user_mail,
            is_active=True,
        )
        query = (
            insert(Token)
            .returning(Token)
            .values(token_data.model_dump(exclude={"token_type"}))
        )
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return TokenGet(**row)
        else:
            raise ValueError("Failed to create token. No row returned.")

    @staticmethod
    async def get_token(user_mail: str, db: AsyncSession) -> TokenGet | None:
        query = select(Token).where(Token.user_mail == user_mail)
        result = await db.execute(query)
        token = result.fetchone()

        if token:
            return TokenGet(**token[0].to_dict())
        else:
            return None

    @staticmethod
    async def deactivate_token(current_user: PublicUser, db: AsyncSession) -> None:
        result = await db.execute(
            select(Token).filter(
                Token.user_mail == current_user.mail,
            )
        )
        current_token = result.scalar()
        if current_token:
            await db.execute(
                update(Token)
                .where(Token.user_mail == current_user.mail)
                .values(is_active=False)
            )
