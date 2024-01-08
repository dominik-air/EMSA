from pydantic import EmailStr
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.validators import validate_not_self, validate_user_exist
from src.database.models import FriendRequest, Friendship, User
from src.database.schemas import (
    FriendRequestCreate,
    FriendRequestGet,
    FriendshipCreate,
    PublicUser,
)
from src.routes.contracts import GetPendingRequests, GetSentRequests


class FriendCRUD:
    @staticmethod
    async def check_if_friends(
        user_mail: EmailStr, friend_mail: EmailStr, db: AsyncSession
    ) -> bool:
        query = select(Friendship).where(
            Friendship.user_mail == user_mail, Friendship.friend_mail == friend_mail
        )
        result = await db.execute(query)
        friendship = result.fetchone()

        return friendship is not None

    @staticmethod
    async def get_user_friends(
        user_mail: EmailStr, db: AsyncSession
    ) -> list[PublicUser]:
        query = (
            select(User)
            .join(Friendship, User.mail == Friendship.friend_mail)
            .where(Friendship.user_mail == user_mail)
        )
        result = await db.execute(query)
        friends_data = result.fetchall()
        return [PublicUser(**friend[0].to_dict()) for friend in friends_data]

    @staticmethod
    async def create_friend_request(
        sender_mail: EmailStr,
        receiver_mail: EmailStr,
        db: AsyncSession,
    ) -> FriendRequestGet:
        validate_not_self(sender_mail, receiver_mail)
        await validate_user_exist(sender_mail, db)
        await validate_user_exist(receiver_mail, db)
        if await FriendCRUD.check_if_friends(sender_mail, receiver_mail, db):
            raise ValueError("Users are already friends")

        existing_request_query = select(FriendRequest).where(
            FriendRequest.sender_mail == sender_mail,
            FriendRequest.receiver_mail == receiver_mail,
        )
        existing_request = (await db.execute(existing_request_query)).scalar()
        if existing_request:
            raise ValueError("Friend request already sent")

        if sender_mail in await FriendCRUD.get_sent_requests(receiver_mail, db):
            await FriendCRUD.add_friend(receiver_mail, sender_mail, db)

        friend_request = FriendRequestCreate(
            sender_mail=sender_mail,
            receiver_mail=receiver_mail,
        )
        query = (
            insert(FriendRequest)
            .returning(FriendRequest)
            .values(friend_request.model_dump())
        )
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return FriendRequestGet(**row)
        else:
            raise ValueError("Failed to create FriendRequest. No row returned.")

    @staticmethod
    async def get_pending_requests(
        user_mail: EmailStr,
        db: AsyncSession,
    ) -> list[GetPendingRequests]:
        query = (
            select(FriendRequest, User)
            .join(User, FriendRequest.sender_mail == User.mail)
            .where(FriendRequest.receiver_mail == user_mail)
        )
        result = await db.execute(query)
        requests_data = result.fetchall()
        return [
            GetPendingRequests(name=request[1].name, mail=request[0].sender_mail)
            for request in requests_data
        ]

    @staticmethod
    async def get_sent_requests(
        user_mail: EmailStr,
        db: AsyncSession,
    ) -> list[GetSentRequests]:
        query = (
            select(FriendRequest, User)
            .join(User, FriendRequest.receiver_mail == User.mail)
            .where(FriendRequest.sender_mail == user_mail)
        )
        result = await db.execute(query)
        requests_data = result.fetchall()
        return [
            GetSentRequests(name=request[1].name, mail=request[0].receiver_mail)
            for request in requests_data
        ]

    @staticmethod
    async def handle_delete_request(
        sender_mail: EmailStr,
        receiver_mail: EmailStr,
        db: AsyncSession,
    ) -> None:
        validate_not_self(sender_mail, receiver_mail)
        await validate_user_exist(sender_mail, db)
        await validate_user_exist(receiver_mail, db)
        existing_request_query = select(FriendRequest).where(
            FriendRequest.sender_mail == sender_mail,
            FriendRequest.receiver_mail == receiver_mail,
        )
        existing_request = (await db.execute(existing_request_query)).scalar()
        if not existing_request:
            raise ValueError("Friend request doesn't exist")
        await FriendCRUD.delete_request(
            sender_mail,
            receiver_mail,
            db,
        )

    @staticmethod
    async def delete_request(
        sender_mail: EmailStr,
        receiver_mail: EmailStr,
        db: AsyncSession,
    ) -> None:
        query = delete(FriendRequest).where(
            FriendRequest.sender_mail == sender_mail,
            FriendRequest.receiver_mail == receiver_mail,
        )
        await db.execute(query)

    @staticmethod
    async def add_friend(
        user_mail: EmailStr, friend_mail: EmailStr, db: AsyncSession
    ) -> None:
        validate_not_self(user_mail, friend_mail)
        await validate_user_exist(user_mail, db)
        await validate_user_exist(friend_mail, db)
        if await FriendCRUD.check_if_friends(user_mail, friend_mail, db):
            raise ValueError("Users are already friends")

        await FriendCRUD.delete_request(friend_mail, user_mail, db)
        await FriendCRUD.delete_request(user_mail, friend_mail, db)
        friendships = [
            FriendshipCreate(user_mail=user_mail, friend_mail=friend_mail),
            FriendshipCreate(user_mail=friend_mail, friend_mail=user_mail),
        ]
        query = insert(Friendship).values(
            [friendship.model_dump() for friendship in friendships]
        )
        await db.execute(query)

    @staticmethod
    async def remove_friend(
        user_mail: EmailStr, friend_mail: EmailStr, db: AsyncSession
    ) -> None:
        query = delete(Friendship).where(
            Friendship.user_mail == user_mail, Friendship.friend_mail == friend_mail
        )
        await db.execute(query)
        query = delete(Friendship).where(
            Friendship.user_mail == friend_mail, Friendship.friend_mail == user_mail
        )
        await db.execute(query)
