from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.cloud_storage import (
    CloudStorage,
    FailedToDeleteImageException,
    FailedToUploadImageException,
)


@pytest.fixture
def mock_gcp_credentials():
    with patch(
        "google.oauth2.service_account.Credentials.from_service_account_file"
    ) as mock:
        mock_credentials = MagicMock(token="fake_token")
        mock_credentials.refresh = MagicMock()
        mock.return_value = mock_credentials
        yield


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_gcp_credentials")
async def test_upload_image_success():
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock(status=200, text=AsyncMock(return_value="Success"))
        mock_post.return_value.__aenter__.return_value = mock_response

        cloud_storage = CloudStorage()

        result = await cloud_storage.upload_image(
            "test_id", b"image_data", "test_group"
        )

        assert (
            result == "https://storage.googleapis.com/emsa-content/test_group/test_id"
        )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_gcp_credentials")
async def test_upload_image_failure():
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock(
            status=500, text=AsyncMock(return_value="Server Error")
        )
        mock_post.return_value.__aenter__.return_value = mock_response

        cloud_storage = CloudStorage()

        with pytest.raises(FailedToUploadImageException):
            await cloud_storage.upload_image("test_id", b"image_data", "test_group")


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_gcp_credentials")
async def test_delete_image_success():
    with patch("aiohttp.ClientSession.delete") as mock_delete:
        mock_response = AsyncMock(status=204)
        mock_delete.return_value.__aenter__.return_value = mock_response

        cloud_storage = CloudStorage()

        await cloud_storage.delete_image("test_id", "test_group")


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_gcp_credentials")
async def test_delete_image_failure():
    with patch("aiohttp.ClientSession.delete") as mock_delete:
        mock_response = AsyncMock(
            status=500, text=AsyncMock(return_value="Server Error")
        )
        mock_delete.return_value.__aenter__.return_value = mock_response

        cloud_storage = CloudStorage()

        with pytest.raises(FailedToDeleteImageException):
            await cloud_storage.delete_image("test_id", "test_group")


def live_creds_in_env() -> bool:
    try:
        CloudStorage()
    except Exception:
        return False
    return True


@pytest.mark.asyncio
@pytest.mark.skipif(not live_creds_in_env(), reason="GCP credentials are not present")
async def test_live_image_upload():
    cloud_storage = CloudStorage()
    await cloud_storage.upload_image("test_id", b"image_data", "test_group")
    await cloud_storage.delete_image("test_id", "test_group")
