from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.database.schemas import PrivateUser, PublicUser, UpdateUser


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
    async def get_user(user_mail: str, db: AsyncSession) -> PrivateUser:
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
    async def update_user(mail: str, user: UpdateUser, db: AsyncSession) -> PrivateUser:
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
    async def delete_user(mail: str, db: AsyncSession) -> None:
        query = delete(User).where(User.mail == mail)
        await db.execute(query)
