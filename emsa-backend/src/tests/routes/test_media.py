import io
import logging
from unittest.mock import ANY, AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.tests.conftest import GROUP_1, USER_1, headers_for_user1

logging.basicConfig(level=logging.ERROR)


@pytest.mark.asyncio
async def test_proposed_tags(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    payload = {"name": "Test Media", "is_image": False, "link": "https://example.com"}
    expected_response = {"proposed_tags": ["test", "media", "example"]}

    response = await client.post(
        "/propose_tags",
        json=payload,
        headers=await headers_for_user1(db_session),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_add_link(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    payload = {
        "group_id": advanced_use_case["group_ids"][0],
        "link": "https://www.tiktok.com/@hubsztal_/video/7313356906494430496?_r=1&_t=8iG637nsGEy",
        "tags": ["tag1", "tag2"],
        "name": "abc",
    }
    expected_response = {
        "group_id": ANY,
        "is_image": False,
        "image_path": "",
        "link": "https://www.tiktok.com/@hubsztal_/video/7313356906494430496?_r=1&_t=8iG637nsGEy",
        "name": "abc",
        "preview_link": "https://storage.googleapis.com/emsa-content/thumbnails/tiktok_logo",
        "uploaded_by": USER_1.mail,
        "tags": ["tag1", "tag2"],
        "id": ANY,
    }

    with patch("src.routes.media.CloudStorage"):
        response = await client.post(
            "/add_link",
            json=payload,
            headers=await headers_for_user1(db_session),
        )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_add_image(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    file_content = b"fake-image-content"
    fake_file = io.BytesIO(file_content)
    payload = {
        "group_id": advanced_use_case["group_ids"][0],
        "name": "abc",
        "tags": ["tag1", "tag2"],
    }
    files = {"image": ("image.jpg", fake_file, "image/jpeg")}
    expected_response = {
        "group_id": ANY,
        "is_image": True,
        "image_path": "cloud_key",
        "link": "",
        "name": "abc",
        "preview_link": "cloud_key",
        "uploaded_by": USER_1.mail,
        "tags": ["tag1", "tag2"],
        "id": ANY,
    }

    with patch("src.routes.media.CloudStorage") as mock_cloud:
        mock_cloud_instance = mock_cloud.return_value
        mock_cloud_instance.upload_image = AsyncMock()
        mock_cloud_instance.upload_image.return_value = "cloud_key"

        response = await client.post(
            "/add_image",
            data=payload,
            files=files,
            headers=await headers_for_user1(db_session),
        )

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_delete_media_link(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    media_id = advanced_use_case["media_ids"][1]

    with patch("src.routes.media.CloudStorage") as mock_cloud:
        mock_cloud_instance = mock_cloud.return_value
        mock_cloud_instance.delete_image = AsyncMock()
        mock_cloud_instance.delete_image.return_value = None

        response = await client.delete(
            f"/delete_media?media_id={media_id}",
            headers=await headers_for_user1(db_session),
        )

    mock_cloud_instance.delete_image.assert_not_awaited()
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_media_image(
    client: AsyncClient,
    db_session: AsyncSession,
    advanced_use_case,
):
    media_id = advanced_use_case["media_ids"][0]

    with patch("src.routes.media.CloudStorage") as mock_cloud:
        mock_cloud_instance = mock_cloud.return_value
        mock_cloud_instance.delete_image = AsyncMock()
        mock_cloud_instance.delete_image.return_value = None

        response = await client.delete(
            f"/delete_media?media_id={media_id}",
            headers=await headers_for_user1(db_session),
        )

    mock_cloud_instance.delete_image.assert_called_once_with(
        str(media_id), GROUP_1.name
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
