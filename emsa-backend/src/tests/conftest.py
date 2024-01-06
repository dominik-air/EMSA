import asyncio
from asyncio import current_task
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from src.authorization import create_access_token
from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.crud.user import FriendCRUD, UserCRUD
from src.database.schemas import (
    GroupCreate,
    GroupGet,
    MediaCreate,
    MediaGet,
    PrivateUser,
)
from src.database.session import Base, engine, get_db
from src.routes import group, health_check, media, user
from src.settings import settings

USER_1 = PrivateUser(mail="abc@gmail.com", name="Dominik", password_hash="321fdas532")
USER_2 = PrivateUser(mail="bzak@agh.pl", name="Bartosz", password_hash="emsa2137")
USER_3 = PrivateUser(
    mail="ewa@example.com", name="EL_wariatka", password_hash="password123"
)
USER_4 = PrivateUser(
    mail="radek@example.com", name="Radik", password_hash="password456"
)

GROUP_1 = GroupCreate(name="Group 1", owner_mail="abc@gmail.com")
GROUP_2 = GroupCreate(name="Group 2", owner_mail="bzak@agh.pl")

TAGS_1 = ["Bike", "FUNNY", "fall"]
TAGS_2 = ["Travel", "Adventure"]

MEDIA_DATA_1 = {
    "is_image": True,
    "image_path": "our-storage.com/1",
    "tags": TAGS_1,
    "name": "Old but funny",
}
MEDIA_DATA_2 = {
    "is_image": False,
    "link": "tiktok.com/dominik-air",
    "tags": TAGS_1[1::],
    "name": "Old tiktok star",
}
MEDIA_DATA_3 = {"is_image": True, "image_path": "our-storage.com/2", "tags": TAGS_2}
MEDIA_DATA_4 = {"is_image": False, "link": "example.com/video", "tags": TAGS_2[1::]}


def start_application() -> FastAPI:
    app = FastAPI()
    app.include_router(user.router, tags=["user"])
    app.include_router(group.router, tags=["group"])
    app.include_router(media.router, tags=["health"])
    app.include_router(health_check.router, tags=["health"])
    return app


@pytest_asyncio.fixture(scope="session")
async def app():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _app = start_application()
        yield _app
    finally:
        async with engine.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def async_db_connection(app: FastAPI):
    async_engine = create_async_engine(
        settings.DATABASE_URL, echo=False, connect_args={"timeout": 0.5}
    )

    async with async_engine.begin() as conn:
        # separate connection because .create_all makes .commit inside
        await conn.run_sync(Base.metadata.create_all)

    conn = await async_engine.connect()
    try:
        yield conn
    except Exception:
        raise
    finally:
        await conn.rollback()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


async def __session_within_transaction(async_db_connection):  # noqa: E701
    async_session_maker = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_connection,
        class_=AsyncSession,
    )
    transaction = await async_db_connection.begin()

    yield async_scoped_session(async_session_maker, scopefunc=current_task)

    # no need to truncate, all data will be rolled back
    await transaction.rollback()


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_db_connection) -> AsyncGenerator[AsyncSession, None]:
    async for session in __session_within_transaction(async_db_connection):
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(
    app: FastAPI, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def two_users(db_session: AsyncSession) -> list[PrivateUser]:
    user_1 = await UserCRUD.create_user(USER_1, db_session)
    user_2 = await UserCRUD.create_user(USER_2, db_session)
    return [user_1, user_2]


@pytest_asyncio.fixture(scope="function")
async def two_groups(
    db_session: AsyncSession, two_users: list[PrivateUser]
) -> list[GroupGet]:
    group_1 = await GroupCRUD.create_group(
        GroupCreate(name=GROUP_1.name, owner_mail=two_users[0].mail), db_session
    )
    group_2 = await GroupCRUD.create_group(
        GroupCreate(name=GROUP_2.name, owner_mail=two_users[0].mail), db_session
    )
    return [group_1, group_2]


@pytest_asyncio.fixture(scope="function")
async def two_media_on_groups(
    db_session: AsyncSession,
    two_groups: list[GroupGet],
) -> list[MediaGet]:
    media_1 = MediaCreate(**{"group_id": two_groups[0].id, **MEDIA_DATA_1})
    media_2 = MediaCreate(**{"group_id": two_groups[1].id, **MEDIA_DATA_2})
    media_1 = await MediaCRUD.create_media(media_1, db_session)
    media_2 = await MediaCRUD.create_media(media_2, db_session)
    return [media_1, media_2]


@pytest_asyncio.fixture(scope="function")
async def advanced_use_case(db_session: AsyncSession) -> dict:
    users = [
        USER_1,
        USER_2,
        USER_3,
        USER_4,
    ]
    user_1, user_2, user_3, user_4 = await asyncio.gather(
        *[UserCRUD.create_user(user, db_session) for user in users]
    )

    # 2 groups owned by user 1 and 2
    group_1 = await GroupCRUD.create_group(GROUP_1, db_session)
    group_2 = await GroupCRUD.create_group(GROUP_2, db_session)

    # Make user_1, user_2, and user_3 friends and add them to group_1
    await FriendCRUD.add_friend(user_1.mail, user_2.mail, db_session)
    await FriendCRUD.add_friend(user_1.mail, user_3.mail, db_session)
    await FriendCRUD.add_friend(user_2.mail, user_3.mail, db_session)
    await GroupCRUD.add_users_to_group(
        group_1.id, [user_1.mail, user_2.mail, user_3.mail], db_session
    )

    # Make user_2 and user_4 friends and add them to group_2
    await FriendCRUD.add_friend(user_2.mail, user_4.mail, db_session)
    await GroupCRUD.add_users_to_group(
        group_2.id, [user_2.mail, user_4.mail], db_session
    )

    # Add content into group 1 and 2
    media_1 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_1})
    media_2 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_2})
    media_3 = MediaCreate(**{"group_id": group_2.id, **MEDIA_DATA_3})
    media_4 = MediaCreate(**{"group_id": group_2.id, **MEDIA_DATA_4})
    media_1 = await MediaCRUD.create_media(media_1, db_session)
    media_2 = await MediaCRUD.create_media(media_2, db_session)
    media_3 = await MediaCRUD.create_media(media_3, db_session)
    media_4 = await MediaCRUD.create_media(media_4, db_session)

    return {
        "user_ids": [user.mail for user in users],
        "group_ids": [group_1.id, group_2.id],
        "media_ids": [media_1.id, media_2.id, media_3.id, media_4.id],
    }


async def headers_for_user1(db_session) -> dict:
    access_token = await create_access_token(
        data={"sub": USER_1.mail},
        db=db_session,
    )
    return {"Authorization": f"Bearer {access_token}"}


async def headers_for_user2(db_session) -> dict:
    access_token = await create_access_token(
        data={"sub": USER_2.mail},
        db=db_session,
    )
    return {"Authorization": f"Bearer {access_token}"}


async def headers_for_user3(db_session) -> dict:
    access_token = await create_access_token(
        data={"sub": USER_3.mail},
        db=db_session,
    )
    return {"Authorization": f"Bearer {access_token}"}


async def headers_for_user4(db_session) -> dict:
    access_token = await create_access_token(
        data={"sub": USER_4.mail},
        db=db_session,
    )
    return {"Authorization": f"Bearer {access_token}"}
