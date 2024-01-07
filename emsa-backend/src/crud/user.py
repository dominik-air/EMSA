from jose import jwt
from pydantic import EmailStr
from sqlalchemy import delete, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import FriendRequest, Friendship, Token, User
from src.database.schemas import (
    FriendRequestCreate,
    FriendRequestGet,
    FriendshipCreate,
    PrivateUser,
    PublicUser,
    TokenCreate,
    TokenGet,
    UpdateUser,
)
from src.routes.contracts import GetPendingRequests, GetSentRequests
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
        if sender_mail == receiver_mail:
            raise ValueError("Can't send friend request to yourself")
        await UserCRUD.get_user(sender_mail, db)
        await UserCRUD.get_user(receiver_mail, db)
        if await FriendCRUD.check_if_friends(sender_mail, receiver_mail, db):
            raise ValueError("Users are already friends")

        existing_request_query = select(FriendRequest).where(
            FriendRequest.sender_mail == sender_mail,
            FriendRequest.receiver_mail == receiver_mail,
        )
        existing_request = (await db.execute(existing_request_query)).scalar()
        if existing_request:
            raise ValueError("Friend request already sent")

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
        if user_mail == friend_mail:
            raise ValueError("Can't add yourself as friend")
        await UserCRUD.get_user(user_mail, db)
        await UserCRUD.get_user(friend_mail, db)
        if await FriendCRUD.check_if_friends(user_mail, friend_mail, db):
            raise ValueError("Users are already friends")

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
