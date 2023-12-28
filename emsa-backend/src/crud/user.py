from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Friendship, User
from src.database.schemas import FriendshipCreate, PrivateUser, PublicUser, UpdateUser


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


class FriendCRUD:
    @staticmethod
    async def check_if_friends(
        user_mail: str, friend_mail: str, db: AsyncSession
    ) -> bool:
        query = select(Friendship).where(
            Friendship.user_mail == user_mail, Friendship.friend_mail == friend_mail
        )
        result = await db.execute(query)
        friendship = result.fetchone()

        return friendship is not None

    @staticmethod
    async def get_user_friends(user_mail: str, db: AsyncSession) -> list[PublicUser]:
        query = (
            select(User)
            .join(Friendship, User.mail == Friendship.friend_mail)
            .where(Friendship.user_mail == user_mail)
        )
        result = await db.execute(query)
        friends_data = result.fetchall()
        return [PublicUser(**friend[0].to_dict()) for friend in friends_data]

    @staticmethod
    async def add_friend(user_mail: str, friend_mail: str, db: AsyncSession) -> None:
        await UserCRUD.get_user(user_mail, db)
        await UserCRUD.get_user(friend_mail, db)

        if await FriendCRUD.check_if_friends(user_mail, friend_mail, db):
            raise ValueError("Users are already friends")

        friendships = [
            FriendshipCreate(user_mail=user_mail, friend_mail=friend_mail),
            FriendshipCreate(user_mail=friend_mail, friend_mail=user_mail),
        ]

        query = insert(Friendship).values(
            [friendship.model_dump() for friendship in friendships]
        )
        await db.execute(query)

    @staticmethod
    async def remove_friend(user_mail: str, friend_mail: str, db: AsyncSession) -> None:
        query = delete(Friendship).where(
            Friendship.user_mail == user_mail, Friendship.friend_mail == friend_mail
        )
        await db.execute(query)
        query = delete(Friendship).where(
            Friendship.user_mail == friend_mail, Friendship.friend_mail == user_mail
        )
        await db.execute(query)
