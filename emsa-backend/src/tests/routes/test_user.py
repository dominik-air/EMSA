import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import FriendCRUD, UserCRUD
from src.tests.conftest import USER_1, USER_2, USER_3, USER_4


@pytest.mark.asyncio
async def test_remove_account(client: AsyncClient, advanced_use_case, db_session):
    user_to_delete = advanced_use_case["user_ids"][1]
    users_before = await UserCRUD.get_users(db_session)

    response = await client.delete(f"/remove_account?mail={user_to_delete}")
    users_after = await UserCRUD.get_users(db_session)

    assert user_to_delete in [user.mail for user in users_before]
    assert user_to_delete not in [user.mail for user in users_after]
    assert len(users_after) == len(users_before) - 1
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


@pytest.mark.asyncio
async def test_update_account(client: AsyncClient, advanced_use_case, db_session):
    user_to_update = advanced_use_case["user_ids"][0]
    update_data = {"name": "UpdatedName", "password_hash": "UpdatedPassword"}

    response = await client.put(
        f"/update_account?mail={user_to_update}",
        json=update_data,
    )
    response_data = response.json()
    updated_user = await UserCRUD.get_user(user_to_update, db_session)

    assert response.status_code == 200, response.json()
    assert updated_user.name == update_data["name"]
    assert updated_user.password_hash == update_data["password_hash"]
    assert response_data["mail"] == updated_user.mail
    assert response_data["name"] == updated_user.name


@pytest.mark.asyncio
async def test_add_friend(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    friends_before = await FriendCRUD.get_user_friends(USER_1.mail, db_session)
    response = await client.post(
        f"/add_friend?user_mail={USER_1.mail}&friend_mail={USER_4.mail}",
    )
    friends_after = await FriendCRUD.get_user_friends(USER_1.mail, db_session)

    assert response.status_code == status.HTTP_201_CREATED
    assert len(friends_after) == len(friends_before) + 1
    assert not response.json()


@pytest.mark.asyncio
async def test_remove_friend(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    friends_before = await FriendCRUD.get_user_friends(USER_1.mail, db_session)
    response = await client.delete(
        f"/remove_friend?user_mail={USER_1.mail}&friend_mail={USER_3.mail}",
    )
    friends_after = await FriendCRUD.get_user_friends(USER_1.mail, db_session)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(friends_after) == len(friends_before) - 1


@pytest.mark.asyncio
async def test_get_user_friends(client: AsyncClient, advanced_use_case):
    expected_friends = [
        {"mail": USER_2.mail, "name": USER_2.name},
        {"mail": USER_3.mail, "name": USER_3.name},
    ]
    response = await client.get(f"/user_friends?user_mail={USER_1.mail}")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_friends
