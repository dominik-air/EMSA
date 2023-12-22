from sqlalchemy import delete, func, insert, literal_column, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.database.models import Media
from src.database.schemas import (
    MediaCreate,
    MediaGet,
    MediaList,
    MediaQuery,
    MediaUpdate,
)


class MediaCRUD:
    @staticmethod
    async def create_media(media: MediaCreate, db: AsyncSession) -> MediaGet:
        query = insert(Media).returning(Media).values(media.model_dump())
        result = await db.execute(query)
        fetched_media = result.fetchone()

        if fetched_media:
            return MediaGet(**fetched_media._asdict())
        else:
            raise ValueError("Failed to create media. No row returned.")

    @staticmethod
    async def get_media(media_id: int, db: AsyncSession) -> MediaGet:
        query = select(Media).where(Media.id == media_id)
        result = await db.execute(query)
        fetched_media = result.fetchone()

        if fetched_media:
            return MediaGet(**fetched_media[0].to_dict())
        else:
            raise ValueError(f"No media found with ID: {media_id}")

    @staticmethod
    async def get_all_media(db: AsyncSession) -> list[MediaList]:
        query = select(Media)
        result = await db.execute(query)
        fetched_all_media = result.fetchall()
        return [MediaList(**media[0].to_dict()) for media in fetched_all_media]

    @staticmethod
    async def update_media(
        media_id: int, media_update: MediaUpdate, db: AsyncSession
    ) -> MediaGet:
        query = (
            update(Media)
            .returning(Media)
            .values(media_update.model_dump(exclude_defaults=True))
            .where(Media.id == media_id)
        )
        result = await db.execute(query)
        fetched_media = result.fetchone()

        if fetched_media:
            return MediaGet(**fetched_media._asdict())
        else:
            raise ValueError(f"No media found with ID: {media_id}")

    @staticmethod
    async def delete_media(media_id: int, db: AsyncSession) -> None:
        query = delete(Media).where(Media.id == media_id)
        await db.execute(query)

    @staticmethod
    async def get_media_by_group(
        group_id: int, db: AsyncSession, query_params: MediaQuery | None = None
    ) -> list[MediaGet]:
        await GroupCRUD.get_group(group_id, db)
        query = select(Media).where(Media.group_id == group_id)

        if query_params and query_params.search_term:
            search_term_lower = query_params.search_term.lower()
            subquery = select(
                literal_column("media.id").label("media_id"),
                func.unnest(Media.tags).label("tag"),
            ).alias("tags_subquery")

            query = query.join(subquery, subquery.c.media_id == Media.id).filter(
                func.lower(subquery.c.tag).like(search_term_lower)
            )

        result = await db.execute(query)
        media_data = result.fetchall()

        return [MediaGet(**media[0].to_dict()) for media in media_data]
