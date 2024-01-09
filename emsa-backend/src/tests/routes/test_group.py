from unittest.mock import ANY

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.routes.contracts import AddGroupMembersRequest
from src.tests.conftest import (
    GROUP_1,
    MEDIA_DATA_1,
    MEDIA_DATA_2,
    TAGS_1,
    USER_1,
    USER_2,
    USER_3,
    USER_4,
    headers_for_user1,
    headers_for_user2,
    headers_for_user4,
)


@pytest.mark.asyncio
async def test_create_group(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    payload = {"name": "GroupOfUser4", "owner_mail": advanced_use_case["user_ids"][3]}
    expected_group_creation = {
        "id": ANY,
        "name": "GroupOfUser4",
        "owner_mail": USER_4.mail,
    }

    response = await client.post(
        "/create_group",
        json=payload,
        headers=await headers_for_user4(db_session),
    )
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json() == expected_group_creation


@pytest.mark.asyncio
async def test_add_group_members(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    group_id = advanced_use_case["group_ids"][1]
    payload = AddGroupMembersRequest(
        members=[advanced_use_case["user_ids"][0], advanced_use_case["user_ids"][2]]
    )
    members_before = await GroupCRUD.get_users_in_group(group_id, db_session)

    response = await client.post(
        f"/add_group_members/{group_id}",
        json=payload.model_dump(),
        headers=await headers_for_user2(db_session),
    )
    members_after = await GroupCRUD.get_users_in_group(group_id, db_session)

    for user in payload.members:
        assert user not in [user.mail for user in members_before]
        assert user in [user.mail for user in members_after]
    assert len(members_after) == len(members_before) + 2
    assert response.status_code == status.HTTP_200_OK, response.json()


@pytest.mark.asyncio
async def test_remove_member(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    group_id = advanced_use_case["group_ids"][0]
    member_to_delete = advanced_use_case["user_ids"][1]
    members_before = await GroupCRUD.get_users_in_group(group_id, db_session)

    response = await client.delete(
        f"/remove_member/{group_id}/{member_to_delete}",
        headers=await headers_for_user1(db_session),
    )
    members_after = await GroupCRUD.get_users_in_group(group_id, db_session)

    assert member_to_delete in [user.mail for user in members_before]
    assert member_to_delete not in [user.mail for user in members_after]
    assert len(members_after) == len(members_before) - 1
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


@pytest.mark.asyncio
async def test_get_user_groups(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    expected_groups = [
        {"name": GROUP_1.name, "owner_mail": GROUP_1.owner_mail, "id": ANY}
    ]
    response = await client.get(
        "/user_groups",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_groups


@pytest.mark.asyncio
async def test_get_mutual_groups(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    expected_groups = [
        {"name": GROUP_1.name, "owner_mail": GROUP_1.owner_mail, "id": ANY},
    ]
    response = await client.get(
        f"/mutual_groups/{USER_2.mail}",
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_groups


@pytest.mark.asyncio
async def test_get_group_members(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    group_id = advanced_use_case["group_ids"][0]
    expected_group_members = [
        {"mail": USER_1.mail, "name": USER_1.name},
        {"mail": USER_2.mail, "name": USER_2.name},
        {"mail": USER_3.mail, "name": USER_3.name},
    ]

    response = await client.get(
        f"/group_members/{group_id}",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_group_members


@pytest.mark.asyncio
async def test_get_group_content(client: AsyncClient, advanced_use_case, db_session):
    group_id = advanced_use_case["group_ids"][0]
    expected_group_content = [
        {
            "group_id": group_id,
            "is_image": MEDIA_DATA_1["is_image"],
            "name": MEDIA_DATA_1["name"],
            "image_path": MEDIA_DATA_1["image_path"],
            "link": "",
            "preview_link": "",
            "uploaded_by": "",
            "id": ANY,
            "tags": ["Bike", "FUNNY", "fall"],
        },
        {
            "group_id": group_id,
            "is_image": MEDIA_DATA_2["is_image"],
            "name": MEDIA_DATA_2["name"],
            "image_path": "",
            "link": MEDIA_DATA_2["link"],
            "preview_link": "",
            "uploaded_by": "",
            "id": ANY,
            "tags": ["FUNNY", "fall"],
        },
    ]

    response = await client.get(
        f"/group_content/{group_id}",
        headers=await headers_for_user1(db_session),
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_group_content


@pytest.mark.asyncio
async def test_group_content_search_term(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    group_id = advanced_use_case["group_ids"][0]

    response = await client.get(
        f"/group_content/{group_id}?search_term={TAGS_1[0]}",
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()) == 1
    assert response.json()[0]["id"] in advanced_use_case["media_ids"]


@pytest.mark.asyncio
async def test_group_content_no_search_term(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    group_id = advanced_use_case["group_ids"][0]

    response = await client.get(
        f"/group_content/{group_id}",
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()) == 2
    assert all(
        media["id"] in advanced_use_case["media_ids"] for media in response.json()
    )


@pytest.mark.asyncio
async def test_group_content_nonexistent_search_term(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    group_id = advanced_use_case["group_ids"][0]

    response = await client.get(
        f"/group_content/{group_id}?search_term=nonexistent",
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_remove_group(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    group_id_to_delete = advanced_use_case["group_ids"][0]
    groups_before = await GroupCRUD.get_groups(db_session)

    response = await client.delete(
        f"/remove_group/{group_id_to_delete}",
        headers=await headers_for_user1(db_session),
    )
    groups_after = await GroupCRUD.get_groups(db_session)

    assert group_id_to_delete in [group.id for group in groups_before]
    assert group_id_to_delete not in [group.id for group in groups_after]
    assert len(groups_after) == len(groups_before) - 1
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
