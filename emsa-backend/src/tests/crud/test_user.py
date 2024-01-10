import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.authorization import verify_password
from src.crud.friend import FriendCRUD
from src.crud.user import UserCRUD
from src.database.models import FriendRequest, Friendship, User
from src.database.schemas import FriendRequestGet, PrivateUser, PublicUser
from src.routes.contracts import UpdateUserRequest
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


@pytest.mark.parametrize(
    "password, name",
    [
        ("jestemgigachad", "Nerd"),
        ("jestemgigachad", None),
        (None, "Nerd"),
    ],
)
@pytest.mark.asyncio
async def test_user_update(password, name, db_session: AsyncSession):
    update_model = UpdateUserRequest(password=password, name=name)
    await UserCRUD.create_user(USER_1, db_session)
    updated_user = await UserCRUD.update_user(USER_1.mail, update_model, db_session)
    get_updated_user = await UserCRUD.get_user(USER_1.mail, db_session)

    assert updated_user.mail == get_updated_user.mail == USER_1.mail
    if name:
        assert updated_user.name == get_updated_user.name == update_model.name
    if password:
        assert verify_password(get_updated_user.password_hash, password) is True


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


@pytest.mark.asyncio
async def test_get_user_friends(db_session: AsyncSession, two_users: list[PrivateUser]):
    user_1, user_2 = two_users
    await FriendCRUD.add_friend(user_1.mail, user_2.mail, db_session)

    friends = await FriendCRUD.get_user_friends(user_1.mail, db_session)

    assert len(friends) == 1
    assert friends[0] == PublicUser(**user_2.model_dump())


@pytest.mark.asyncio
async def test_user_add_friend_request(
    db_session: AsyncSession, two_users: list[PrivateUser]
):
    user_1, user_2 = two_users
    created_request = await FriendCRUD.create_friend_request(
        user_1.mail, user_2.mail, db_session
    )

    query = select(FriendRequest).where(
        FriendRequest.sender_mail == user_1.mail,
        FriendRequest.receiver_mail == user_2.mail,
    )
    result = await db_session.execute(query)
    friend_request = result.fetchone()
    assert FriendRequestGet(**friend_request[0].to_dict()) == created_request  # type: ignore


@pytest.mark.asyncio
async def test_user_get_pending_requests(
    db_session: AsyncSession, two_users: list[PrivateUser]
):
    user_1, user_2 = two_users
    await FriendCRUD.create_friend_request(user_1.mail, user_2.mail, db_session)

    pending_requests = await FriendCRUD.get_pending_requests(user_2.mail, db_session)

    assert len(pending_requests) == 1
    assert pending_requests[0].mail == user_1.mail
    assert pending_requests[0].name == user_1.name


@pytest.mark.asyncio
async def test_user_get_sent_requests(
    db_session: AsyncSession, two_users: list[PrivateUser]
):
    user_1, user_2 = two_users
    await FriendCRUD.create_friend_request(user_1.mail, user_2.mail, db_session)

    sent_requests = await FriendCRUD.get_sent_requests(user_1.mail, db_session)

    assert len(sent_requests) == 1
    assert sent_requests[0].mail == user_2.mail
    assert sent_requests[0].name == user_2.name


@pytest.mark.asyncio
async def test_user_delete_request(
    db_session: AsyncSession, two_users: list[PrivateUser]
):
    user_1, user_2 = two_users
    await FriendCRUD.create_friend_request(user_1.mail, user_2.mail, db_session)
    await FriendCRUD.delete_request(user_1.mail, user_2.mail, db_session)

    query = select(FriendRequest).where(
        FriendRequest.sender_mail == user_1.mail,
        FriendRequest.receiver_mail == user_2.mail,
    )
    result = await db_session.execute(query)
    friend_request = result.fetchone()

    assert friend_request is None
