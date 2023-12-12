from unittest.mock import ANY

import pytest
from fastapi import status
from httpx import AsyncClient

from src.tests.conftest import (
    GROUP_1,
    MEDIA_DATA_1,
    MEDIA_DATA_2,
    USER_1,
    USER_2,
    USER_3,
)


@pytest.mark.asyncio
async def test_get_user_groups(client: AsyncClient, advanced_use_case):
    expected_groups = [
        {"name": GROUP_1.name, "owner_mail": GROUP_1.owner_mail, "id": ANY}
    ]
    response = await client.get(f"/user_groups?user_mail={USER_1.mail}")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_groups


@pytest.mark.asyncio
async def test_get_mutual_groups(client: AsyncClient, advanced_use_case):
    expected_groups = [
        {"name": GROUP_1.name, "owner_mail": GROUP_1.owner_mail, "id": ANY},
    ]
    response = await client.get(
        f"/mutual_groups?user_mail={USER_1.mail}&friend_mail={USER_2.mail}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_groups


@pytest.mark.asyncio
async def test_get_group_members(client: AsyncClient, advanced_use_case):
    group_id = advanced_use_case["group_ids"][0]
    expected_group_members = [
        {"mail": USER_1.mail, "name": USER_1.name},
        {"mail": USER_2.mail, "name": USER_2.name},
        {"mail": USER_3.mail, "name": USER_3.name},
    ]

    response = await client.get(f"/group_members?group_id={group_id}")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_group_members


@pytest.mark.asyncio
async def test_get_group_content(client: AsyncClient, advanced_use_case, db_session):
    group_id = advanced_use_case["group_ids"][0]
    expected_group_content = [
        {
            "group_id": group_id,
            "is_image": MEDIA_DATA_1["is_image"],
            "image_path": MEDIA_DATA_1["image_path"],
            "link": "",
            "id": ANY,
            "tags": [{"name": "Bike"}, {"name": "FUNNY"}, {"name": "fall"}],
        },
        {
            "group_id": group_id,
            "is_image": MEDIA_DATA_2["is_image"],
            "image_path": "",
            "link": MEDIA_DATA_2["link"],
            "id": ANY,
            "tags": [{"name": "FUNNY"}, {"name": "fall"}],
        },
    ]

    response = await client.get(f"/group_content?group_id={group_id}")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == expected_group_content
