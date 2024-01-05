import aiohttp
from google.auth.transport.requests import Request  # type: ignore
from google.oauth2 import service_account  # type: ignore

from src.settings import settings


class FailedToUploadImageException(Exception):
    pass


class FailedToDeleteImageException(Exception):
    pass


class CloudStorage:
    def __init__(self) -> None:
        self.bucket_name = "emsa-content"
        self.credentials = service_account.Credentials.from_service_account_file(
            settings.GCP_SERVICE_ACCOUNT_FILEPATH,
            scopes=("https://www.googleapis.com/auth/devstorage.read_write",),
        )
        self.credentials.refresh(Request())

    async def upload_image(self, image_id: str, image: bytes, group_name: str) -> str:
        """Uploads an image to Cloud Storage asynchronously and returns its public URL."""
        headers = {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "image",
        }
        upload_url = (
            f"https://storage.googleapis.com/upload/storage/v1/b/{self.bucket_name}/o"
            f"?uploadType=media&name={group_name}/{image_id}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                upload_url, headers=headers, data=image
            ) as response:
                if response.status == 200:
                    return f"https://storage.googleapis.com/{self.bucket_name}/{group_name}/{image_id}"
                else:
                    raise FailedToUploadImageException(
                        f"Failed to upload image: {await response.text()}"
                    )

    async def delete_image(self, image_id: str, group_name: str) -> None:
        """Deletes an image from Cloud Storage asynchronously."""
        headers = {"Authorization": f"Bearer {self.credentials.token}"}
        delete_url = f"https://storage.googleapis.com/storage/v1/b/{self.bucket_name}/o/{group_name}%2F{image_id}"

        async with aiohttp.ClientSession() as session:
            async with session.delete(delete_url, headers=headers) as response:
                if response.status != 204:
                    raise FailedToDeleteImageException(
                        f"Failed to delete image: {await response.text()}"
                    )
