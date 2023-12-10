import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import FriendCRUD, UserCRUD
from src.database.models import Friendship, User
from src.database.schemas import PrivateUser, PublicUser, UpdateUser
from src.tests.conftest import USER_1, USER_2


@pytest.mark.asyncio
async def test_user_create(db_session: AsyncSession):
    before_creation_select = await db_session.execute(select(User))
    before_creation_count = len(before_creation_select.fetchall())

    await UserCRUD.create_user(USER_1, db_session)

    after_creation_select = await db_session.execute(select(User))
    after_creation_count = len(after_creation_select.fetchall())

    assert after_creation_count == before_creation_count + 1


@pytest.mark.asyncio
async def test_user_get(db_session: AsyncSession):
    await UserCRUD.create_user(USER_1, db_session)
    user = await UserCRUD.get_user(USER_1.mail, db_session)

    assert user == USER_1


@pytest.mark.asyncio
async def test_user_list(db_session: AsyncSession):
    users_ref = [USER_1, USER_2]
    await UserCRUD.create_user(users_ref[0], db_session)
    await UserCRUD.create_user(users_ref[1], db_session)
    users = await UserCRUD.get_users(db_session)

    assert len(users) == 2
    for i, user in enumerate(users):
        assert user == PublicUser(**users_ref[i].model_dump())


@pytest.mark.asyncio
async def test_user_update(db_session: AsyncSession):
    update_model = UpdateUser(**{"password_hash": "jestemgigachad", "name": "Nerd"})
    await UserCRUD.create_user(USER_1, db_session)
    updated_user = await UserCRUD.update_user(USER_1.mail, update_model, db_session)
    get_updated_user = await UserCRUD.get_user(USER_1.mail, db_session)

    assert updated_user.mail == get_updated_user.mail == USER_1.mail
    assert updated_user.name == get_updated_user.name == update_model.name
    assert (
        updated_user.password_hash
        == get_updated_user.password_hash
        == update_model.password_hash
    )


@pytest.mark.asyncio
async def test_user_delete(db_session: AsyncSession):
    insert_user = insert(User).returning(User).values(USER_1.model_dump())
    await db_session.execute(insert_user)
    before_creation_select = await db_session.execute(select(User))
    before_creation_count = len(before_creation_select.fetchall())

    await UserCRUD.delete_user(USER_1.mail, db_session)

    after_creation_select = await db_session.execute(select(User))
    after_creation_count = len(after_creation_select.fetchall())

    assert after_creation_count == before_creation_count - 1


@pytest.mark.asyncio
async def test_user_add_friend(db_session: AsyncSession, two_users: list[PrivateUser]):
    user_1, user_2 = two_users
    await FriendCRUD.add_friend(user_1.mail, user_2.mail, db_session)

    query = select(Friendship).where(
        Friendship.user_mail == user_1.mail, Friendship.friend_mail == user_2.mail
    )
    result = await db_session.execute(query)
    friendship_1 = result.fetchone()

    query = select(Friendship).where(
        Friendship.user_mail == user_2.mail, Friendship.friend_mail == user_1.mail
    )
    result = await db_session.execute(query)
    friendship_2 = result.fetchone()

    assert friendship_1
    assert friendship_2


@pytest.mark.asyncio
async def test_user_remove_friend(
    db_session: AsyncSession, two_users: list[PrivateUser]
):
    user_1, user_2 = two_users
    await FriendCRUD.add_friend(user_1.mail, user_2.mail, db_session)
    await FriendCRUD.remove_friend(user_1.mail, user_2.mail, db_session)

    query = select(Friendship).where(
        Friendship.user_mail == user_1.mail, Friendship.friend_mail == user_2.mail
    )
    result = await db_session.execute(query)
    friendship_1 = result.fetchone()

    query = select(Friendship).where(
        Friendship.user_mail == user_2.mail, Friendship.friend_mail == user_1.mail
    )
    result = await db_session.execute(query)
    friendship_2 = result.fetchone()

    assert friendship_1 is None
    assert friendship_2 is None
