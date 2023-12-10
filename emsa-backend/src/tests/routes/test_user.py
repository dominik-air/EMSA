import json

import pytest

from src.crud.group import GroupCRUD
from src.crud.user import UserCRUD
from src.tests.conftest import USER_1, create_advanced_use_case
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_groups(test_client: AsyncClient, ):
    # await create_advanced_use_case(db_session)
    response = await test_client.get(f"/user_groups")
    assert response.status_code == 200, response.json()
    assert "groups" in response.json()


@pytest.mark.asyncio
async def test_user_friends(two_users, client):
    user = two_users[0]
    response = await client.get(f"/user_friends?user_mail={user.mail}")
    assert response.status_code == 200
    assert "friends" in response.json()


@pytest.mark.asyncio
async def test_mutual_groups(db_session, two_users, two_groups, client):
    user_1, user_2 = two_users
    group_1, group_2 = two_groups

    # Add both users to each other's friends
    await UserCRUD.add_friend(user_1.mail, user_2.mail, db_session)

    response = await client.get(
        f"/mutual_groups?user_mail={user_1.mail}&friend_mail={user_2.mail}"
    )
    assert response.status_code == 200
    assert "mutual_groups" in response.json()


@pytest.mark.asyncio
async def test_add_friend(db_session, two_users, client):
    user_1, user_2 = two_users
    response = await client.post(
        "/add_friend", json={"user_mail": user_1.mail, "friend_mail": user_2.mail}
    )
    assert response.status_code == 201
    assert "message" in response.json()

    # Check if the friend has been added
    response = await client.get(f"/user_friends?user_mail={user_1.mail}")
    assert response.status_code == 200
    friends = response.json()["friends"]
    assert any(friend["mail"] == user_2.mail for friend in friends)


@pytest.mark.asyncio
async def test_remove_friend(db_session, two_users, client):
    user_1, user_2 = two_users

    # Add users as friends first
    await UserCRUD.add_friend(user_1.mail, user_2.mail, db_session)

    response = await client.delete(
        "/remove_friend", json={"user_mail": user_1.mail, "friend_mail": user_2.mail}
    )
    assert response.status_code == 200
    assert "message" in response.json()

    # Check if the friend has been removed
    response = await client.get(f"/user_friends?user_mail={user_1.mail}")
    assert response.status_code == 200
    friends = response.json()["friends"]
    assert not any(friend["mail"] == user_2.mail for friend in friends)
