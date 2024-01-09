from unittest.mock import AsyncMock, patch

import pytest

from src.services.preview_generator import (
    extract_video_id,
    fetch_tiktok_logo,
    link_preview_generator,
    preview_link_upload,
)


@pytest.mark.asyncio
async def test_fetch_tiktok_logo():
    expected_logo_url = (
        "https://storage.googleapis.com/emsa-content/thumbnails/tiktok_logo"
    )

    result = await fetch_tiktok_logo()

    assert result == expected_logo_url


@pytest.mark.asyncio
async def test_link_preview_generator_youtube():
    youtube_url = "https://www.youtube.com/watch?v=VIDEO_ID"
    expected_thumbnail = b"fake-thumbnail-content"

    with patch(
        "src.services.preview_generator.fetch_youtube_thumbnail"
    ) as mock_fetch_youtube_thumbnail:
        mock_fetch_youtube_thumbnail.return_value = expected_thumbnail

        result = await link_preview_generator(youtube_url)

    assert result == expected_thumbnail


@pytest.mark.asyncio
async def test_link_preview_generator_tiktok():
    tiktok_url = "https://www.tiktok.com/@user/video/1234567890"
    expected_logo_url = (
        "https://storage.googleapis.com/emsa-content/thumbnails/tiktok_logo"
    )

    with patch(
        "src.services.preview_generator.fetch_tiktok_logo"
    ) as mock_fetch_tiktok_logo:
        mock_fetch_tiktok_logo.return_value = expected_logo_url

        result = await link_preview_generator(tiktok_url)

    assert result == expected_logo_url


@pytest.mark.asyncio
async def test_link_preview_generator_default():
    default_url = "https://example.com"
    expected_screenshot = b"fake-screenshot-content"

    with patch(
        "src.services.preview_generator.fetch_website_screenshot"
    ) as mock_fetch_website_screenshot:
        mock_fetch_website_screenshot.return_value = expected_screenshot

        result = await link_preview_generator(default_url)

    assert result == expected_screenshot


@pytest.mark.asyncio
async def test_preview_link_upload():
    media_id = 1
    image_data = b"fake-image-content"
    expected_key = "cloud_key"

    with patch("src.services.preview_generator.CloudStorage") as mock_cloud_storage:
        mock_cloud_storage_instance = mock_cloud_storage.return_value
        mock_cloud_storage_instance.upload_image = AsyncMock()
        mock_cloud_storage_instance.upload_image.return_value = expected_key

        result = await preview_link_upload(image_data, media_id)

    assert result == expected_key


def test_extract_video_id():
    youtube_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    expected_video_id = "jNQXAC9IVRw"

    result = extract_video_id(youtube_url)

    assert result == expected_video_id
