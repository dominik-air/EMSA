from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Media
from src.database.schemas import MediaCreate, MediaGet, MediaUpdate


class MediaCRUD:
    @staticmethod
    async def create_media(media: MediaCreate, db: AsyncSession) -> MediaGet:
        query = insert(Media).returning(Media).values(media.model_dump())
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return MediaGet(**row)
        else:
            raise ValueError("Failed to create media. No row returned.")

    @staticmethod
    async def get_media(media_id: int, db: AsyncSession) -> MediaGet:
        query = select(Media).where(Media.id == media_id)
        result = await db.execute(query)
        media_data = result.fetchone()

        if media_data:
            return MediaGet(**media_data[0].to_dict())
        else:
            raise ValueError(f"No media found with ID: {media_id}")

    @staticmethod
    async def get_all_media(db: AsyncSession) -> list[MediaGet]:
        query = select(Media)
        result = await db.execute(query)
        media_data = result.fetchall()
        return [MediaGet(**media[0].to_dict()) for media in media_data]

    @staticmethod
    async def update_media(
        media_id: int, media_update: MediaUpdate, db: AsyncSession
    ) -> MediaGet:
        query = (
            update(Media)
            .values(
                is_image=media_update.is_image,
                image_path=media_update.image_path,
                link=media_update.link,
            )
            .returning(Media)
            .where(Media.id == media_id)
        )
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return MediaGet(**row)
        else:
            raise ValueError(f"No media found with ID: {media_id}")

    @staticmethod
    async def delete_media(media_id: int, db: AsyncSession) -> None:
        query = delete(Media).where(Media.id == media_id)
        await db.execute(query)
