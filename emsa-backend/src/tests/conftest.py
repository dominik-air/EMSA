import asyncio
from asyncio import current_task
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.crud.user import UserCRUD
from src.database.schemas import (
    GroupCreate,
    GroupGet,
    MediaCreate,
    MediaGet,
    PrivateUser,
)
from src.database.session import Base
from src.settings import settings

USER_1 = PrivateUser(mail="abc@gmail.com", name="Dominik", password_hash="321fdas532")
USER_2 = PrivateUser(mail="bzak@agh.pl", name="Bartosz", password_hash="emsa2137")
GROUP_1 = GroupCreate(name="Group 1", owner_mail="abc@gmail.com")
GROUP_2 = GroupCreate(name="Group 2", owner_mail="bzak@agh.pl")
MEDIA_DATA_1 = {"is_image": True, "image_path": "komixxy.pl"}
MEDIA_DATA_2 = {"is_image": False, "link": "tiktok.com/dominik-air"}


@pytest_asyncio.fixture(scope="session")
async def async_db_connection():
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
async def db_session(
    async_db_connection,
) -> AsyncGenerator[AsyncSession, None]:
    async for session in __session_within_transaction(async_db_connection):
        yield session


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
