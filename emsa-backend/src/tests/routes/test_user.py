import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.authorization import verify_password
from src.crud.friend import FriendCRUD
from src.crud.user import UserCRUD
from src.routes.contracts import AddFriendRequest
from src.tests.conftest import (
    USER_1,
    USER_2,
    USER_3,
    USER_4,
    headers_for_user1,
    headers_for_user2,
    headers_for_user4,
)


@pytest.mark.asyncio
async def test_register(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    user_data = {
        "mail": "newuser@example.com",
        "name": "New User",
        "password": "newpassword",
    }

    response = await client.post("/register", json=user_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert response_data["mail"] == user_data["mail"]
    assert response_data["name"] == user_data["name"]


@pytest.mark.asyncio
async def test_login(client: AsyncClient, db_session: AsyncSession, advanced_use_case):
    user_data = {
        "mail": "newuser@example.com",
        "name": "New User",
        "password": "newpassword",
    }

    await client.post("/register", json=user_data)
    del user_data["name"]
    response = await client.post("/login", json=user_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_conflict(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    user_data = {
        "mail": USER_1.mail,
        "name": "New User",
        "password": "newpassword",
    }

    response = await client.post("/register", json=user_data)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_login_bad_request(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    user_data = {
        "mail": "nonexistentuser@example.com",
        "password": "invalidpassword",
    }

    response = await client.post("/login", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_user_details(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    response = await client.get(
        "/user_details",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "mail": USER_1.mail,
        "name": USER_1.name,
    }


@pytest.mark.asyncio
async def test_remove_account(client: AsyncClient, advanced_use_case, db_session):
    user_to_delete = advanced_use_case["user_ids"][1]
    users_before = await UserCRUD.get_users(db_session)

    response = await client.delete(
        "/remove_account",
        headers=await headers_for_user2(db_session),
    )
    users_after = await UserCRUD.get_users(db_session)

    assert user_to_delete in [user.mail for user in users_before]
    assert user_to_delete not in [user.mail for user in users_after]
    assert len(users_after) == len(users_before) - 1
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


@pytest.mark.asyncio
async def test_update_account(client: AsyncClient, advanced_use_case, db_session):
    user_to_update = advanced_use_case["user_ids"][0]
    update_data = {"name": "UpdatedName", "password": "UpdatedPassword"}

    response = await client.put(
        "/update_account",
        json=update_data,
        headers=await headers_for_user1(db_session),
    )
    response_data = response.json()
    updated_user = await UserCRUD.get_user(user_to_update, db_session)

    assert response.status_code == 200, response.json()
    assert updated_user.name == update_data["name"]
    assert verify_password(updated_user.password_hash, update_data["password"]) is True
    assert response_data["mail"] == updated_user.mail
    assert response_data["name"] == updated_user.name


@pytest.mark.asyncio
async def test_create_friend_request(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    user_to_send_request = advanced_use_case["user_ids"][3]
    response = await client.post(
        "/create_friend_request",
        json=AddFriendRequest(friend_mail=user_to_send_request).model_dump(),
        headers=await headers_for_user1(db_session),
    )
    user_pending_request = await FriendCRUD.get_pending_requests(
        user_to_send_request, db_session
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert response_data["sender_mail"] == USER_1.mail
    assert response_data["receiver_mail"] == user_to_send_request
    assert any(request.mail == USER_1.mail for request in user_pending_request)
    assert any(request.name == USER_1.name for request in user_pending_request)


@pytest.mark.asyncio
async def test_create_friend_request_self_error(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    user_to_send_request = advanced_use_case["user_ids"][0]
    response = await client.post(
        "/create_friend_request",
        json=AddFriendRequest(friend_mail=user_to_send_request).model_dump(),
        headers=await headers_for_user1(db_session),
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_data["detail"] == "Can't send friend request to yourself"


@pytest.mark.asyncio
async def test_create_friend_request_already_friends_error(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    user_to_send_request = advanced_use_case["user_ids"][1]
    response = await client.post(
        "/create_friend_request",
        json=AddFriendRequest(friend_mail=user_to_send_request).model_dump(),
        headers=await headers_for_user1(db_session),
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_data["detail"] == "Users are already friends"


@pytest.mark.asyncio
async def test_get_pending_requests(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    # user 4 sends friend request to user 1
    await FriendCRUD.create_friend_request(USER_4.mail, USER_1.mail, db_session)
    response = await client.get(
        "/pending_friend_requests",
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_200_OK

    pending_requests = response.json()
    assert len(pending_requests) == 1
    assert pending_requests[0]["name"] == USER_4.name
    assert pending_requests[0]["mail"] == USER_4.mail


@pytest.mark.asyncio
async def test_get_pending_requests_no_requests(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    response = await client.get(
        "/pending_friend_requests",
        headers=await headers_for_user2(db_session),
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_sent_requests(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    # user 4 sends friend request to user 1
    await FriendCRUD.create_friend_request(USER_4.mail, USER_1.mail, db_session)
    response = await client.get(
        "/sent_friend_requests",
        headers=await headers_for_user4(db_session),
    )
    assert response.status_code == status.HTTP_200_OK

    sent_requests = response.json()
    assert len(sent_requests) == 1
    assert sent_requests[0]["name"] == USER_1.name
    assert sent_requests[0]["mail"] == USER_1.mail


@pytest.mark.asyncio
async def test_get_sent_requests_no_requests(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    response = await client.get(
        "/sent_friend_requests",
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_add_friend_self(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    response = await client.post(
        "/add_friend",
        json=AddFriendRequest(friend_mail=USER_1.mail).model_dump(),
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_add_friend_already_friends(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    response = await client.post(
        "/add_friend",
        json=AddFriendRequest(friend_mail=USER_2.mail).model_dump(),
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_add_friend_no_pending_request(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    response = await client.post(
        "/add_friend",
        json=AddFriendRequest(friend_mail=USER_3.mail).model_dump(),
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_add_friend(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    friends_before = await FriendCRUD.get_user_friends(USER_1.mail, db_session)

    # user 4 sends friend request to user 1
    await FriendCRUD.create_friend_request(USER_4.mail, USER_1.mail, db_session)
    # user 1 accepts friend request from user 4
    response = await client.post(
        "/add_friend",
        json=AddFriendRequest(friend_mail=USER_4.mail).model_dump(),
        headers=await headers_for_user1(db_session),
    )
    friends_after = await FriendCRUD.get_user_friends(USER_1.mail, db_session)

    assert response.status_code == status.HTTP_201_CREATED
    assert len(friends_after) == len(friends_before) + 1
    assert not response.json()


@pytest.mark.asyncio
async def test_add_friend_deletes_friend_request(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    # user 4 sends friend request to user 1
    await FriendCRUD.create_friend_request(USER_4.mail, USER_1.mail, db_session)

    # Check that the friend request exists before adding the friend
    friend_request_before = await FriendCRUD.get_pending_requests(
        USER_1.mail, db_session
    )
    assert USER_4.mail in [request.mail for request in friend_request_before]

    response = await client.post(
        "/add_friend",
        json={"friend_mail": USER_4.mail},
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_201_CREATED
    # Check that the friend request is deleted after adding the friend
    friend_request_after = await FriendCRUD.get_pending_requests(
        USER_1.mail, db_session
    )
    friend_sent_request_after = await FriendCRUD.get_sent_requests(
        USER_1.mail, db_session
    )
    assert USER_4.mail not in [request.mail for request in friend_request_after]
    assert USER_1.mail not in [request.mail for request in friend_sent_request_after]


@pytest.mark.asyncio
async def test_decline_friend_request(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    # user 1 sends friend request to user 4
    await FriendCRUD.create_friend_request(USER_1.mail, USER_4.mail, db_session)
    # user 4 declines friend request from user 1
    response = await client.delete(
        f"/decline_friend_request/{USER_1.mail}",
        headers=await headers_for_user4(db_session),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Check that the friend request is deleted after declining
    friend_request_after = await FriendCRUD.get_pending_requests(
        USER_4.mail, db_session
    )
    friend_sent_request_after = await FriendCRUD.get_sent_requests(
        USER_1.mail, db_session
    )
    assert USER_1.mail not in [request.mail for request in friend_request_after]
    assert USER_4.mail not in [request.mail for request in friend_sent_request_after]


@pytest.mark.asyncio
async def test_decline_friend_request_self_error(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    response = await client.delete(
        f"/decline_friend_request/{USER_1.mail}",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Can't send friend request to yourself"


@pytest.mark.asyncio
async def test_decline_friend_request_not_found_error(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    await FriendCRUD.create_friend_request(USER_1.mail, USER_4.mail, db_session)
    response = await client.delete(
        "/decline_friend_request/nonexistentuser@example.com",
        headers=await headers_for_user4(db_session),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"].startswith("No user found with mail")


@pytest.mark.asyncio
async def test_decline_friend_request_no_sent_requests_error(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    # user 1 declines friend request from non-existing user
    response = await client.delete(
        f"/decline_friend_request/{USER_4.mail}",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Friend request doesn't exist"


@pytest.mark.asyncio
async def test_remove_friend_request(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    # user 1 sends friend request to user 4
    await FriendCRUD.create_friend_request(USER_1.mail, USER_4.mail, db_session)

    response = await client.delete(
        f"/remove_friend_request/{USER_4.mail}",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    friend_request_after = await FriendCRUD.get_pending_requests(
        USER_4.mail, db_session
    )
    friend_sent_request_after = await FriendCRUD.get_sent_requests(
        USER_1.mail, db_session
    )
    assert USER_1.mail not in [request.mail for request in friend_request_after]
    assert USER_4.mail not in [request.mail for request in friend_sent_request_after]


@pytest.mark.asyncio
async def test_remove_friend(
    client: AsyncClient, db_session: AsyncSession, advanced_use_case
):
    friends_before = await FriendCRUD.get_user_friends(USER_1.mail, db_session)
    response = await client.delete(
        f"/remove_friend/{USER_3.mail}",
        headers=await headers_for_user1(db_session),
    )
    friends_after = await FriendCRUD.get_user_friends(USER_1.mail, db_session)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(friends_after) == len(friends_before) - 1


@pytest.mark.asyncio
async def test_get_user_friends(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    expected_friends = [
        {"mail": USER_2.mail, "name": USER_2.name},
        {"mail": USER_3.mail, "name": USER_3.name},
    ]
    response = await client.get(
        "/user_friends",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_friends
