from sqlalchemy import delete, insert, select, update, func, cast, String, any_
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.crud.tag import TagCRUD
from src.database.models import Media, Tag, media_tags_association
from src.database.schemas import (
    MediaCreate,
    MediaGet,
    MediaList,
    MediaQuery,
    MediaUpdate,
    TagCreate,
    TagGet,
)


class MediaCRUD:
    @staticmethod
    async def create_media(
        media: MediaCreate, db: AsyncSession, tags: list[TagCreate] | None = None
    ) -> MediaGet:
        query = insert(Media).returning(Media).values(media.model_dump())
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            media_id = row["id"]
        else:
            raise ValueError("Failed to create media. No row returned.")

        related_tags = []

        if tags:
            for tag in tags:
                created_tag = await TagCRUD.create_tag(tag, db, media_id=media_id)
                related_tags.append(created_tag)

        return MediaGet(**row, tags=related_tags)

    @staticmethod
    async def get_media(media_id: int, db: AsyncSession) -> MediaGet:
        query = select(Media).where(Media.id == media_id)
        result = await db.execute(query)
        media_data = result.fetchone()
        related_tags = await MediaCRUD.get_related_tags(media_id, db)

        if media_data:
            return MediaGet(**media_data[0].to_dict(), tags=related_tags)
        else:
            raise ValueError(f"No media found with ID: {media_id}")

    @staticmethod
    async def get_all_media(db: AsyncSession) -> list[MediaList]:
        query = select(Media)
        result = await db.execute(query)
        media_data = result.fetchall()
        return [MediaList(**media[0].to_dict()) for media in media_data]

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
        related_tags = await MediaCRUD.get_related_tags(media_id, db)

        if row:
            return MediaGet(**row, tags=related_tags)
        else:
            raise ValueError(f"No media found with ID: {media_id}")

    @staticmethod
    async def delete_media(media_id: int, db: AsyncSession) -> None:
        query = delete(Media).where(Media.id == media_id)
        await db.execute(query)

    @staticmethod
    async def get_related_tags(media_id: int, db: AsyncSession) -> list[TagGet]:
        query = select(Tag).join(Media.tags).where(Media.id == media_id)
        result = await db.execute(query)
        tags = result.scalars().all()
        return [TagGet(**tag.to_dict()) for tag in tags]

    @staticmethod
    async def get_media_by_group(
        group_id: int, db: AsyncSession, query_params: MediaQuery | None = None
    ) -> list[MediaGet]:
        await GroupCRUD.get_group(group_id, db)
        query = select(Media).where(Media.group_id == group_id)

        if query_params and query_params.search_term:
            search_term_lower = query_params.search_term.lower()
            query = query.join(media_tags_association).join(Tag).filter(
                func.lower(Tag.name).like(search_term_lower)
            )

        result = await db.execute(query)
        media_data = result.fetchall()

        media_with_tags = []
        for media in media_data:
            tags = await MediaCRUD.get_related_tags(media[0].id, db)
            media_with_tags.append(MediaGet(**media[0].to_dict(), tags=tags))

        return media_with_tags
