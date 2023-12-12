import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.media import MediaCRUD
from src.crud.user import FriendCRUD
from src.tests.conftest import MEDIA_DATA_2, TAGS_1, USER_1, USER_2, USER_3, USER_4


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


# @pytest.mark.asyncio
# async def test_group_content_search_term(
#     client: AsyncClient, advanced_use_case
# ):
#     group_id = advanced_use_case["group_ids"][0]
#
#     response = await client.get(
#         f"/group_content?group_id={group_id}&search_query={TAGS_1[0]}"
#     )
#     assert response.status_code == status.HTTP_200_OK, response.json()
#     assert len(response.json()) == 1
#     assert response.json()[0]["id"] in advanced_use_case["media_ids"]
#
#     response = await client.get(
#         f"/group_content?group_id={group_id}&search_query={MEDIA_DATA_2['link'][8:]}"
#     )
#     assert response.status_code == status.HTTP_200_OK, response.json()
#     assert len(response.json()) == 1
#     assert response.json()[0]["id"] in advanced_use_case["media_ids"]
#
#     response = await client.get(f"/group_content?group_id={group_id}")
#     assert response.status_code == status.HTTP_200_OK, response.json()
#     assert len(response.json()) == 2
#     assert all(
#         media["id"] in advanced_use_case["media_ids"] for media in response.json()
#     )
#
#     response = await client.get(
#         f"/group_content?group_id={group_id}&search_query=nonexistent"
#     )
#     assert response.status_code == status.HTTP_200_OK, response.json()
#     assert len(response.json()) == 0
