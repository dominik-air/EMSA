from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Media, Tag, media_tags_association
from src.database.schemas import MediaList, TagCreate, TagGet, TagUpdate


class TagCRUD:
    @staticmethod
    async def create_tag(
        tag: TagCreate, db: AsyncSession, media_id: int | None = None
    ) -> TagGet:
        query = insert(Tag).returning(Tag).values(tag.model_dump())
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            tag_name = row["name"]

            if media_id is not None:
                await db.execute(
                    media_tags_association.insert().values(
                        media_id=media_id, tag_name=tag_name
                    )
                )

            return TagGet(**row)
        else:
            raise ValueError("Failed to create tag. No row returned.")

    @staticmethod
    async def get_tag(tag_name: str, db: AsyncSession) -> TagGet:
        query = select(Tag).where(Tag.name == tag_name)
        result = await db.execute(query)
        tag_data = result.fetchone()

        if tag_data:
            return TagGet(**tag_data[0].to_dict())
        else:
            raise ValueError(f"No tag found with ID: {tag_name}")

    @staticmethod
    async def get_tags(db: AsyncSession) -> list[TagGet]:
        query = select(Tag)
        result = await db.execute(query)
        tags_data = result.fetchall()
        return [TagGet(**tag[0].to_dict()) for tag in tags_data]

    @staticmethod
    async def update_tag(tag_name: str, tag: TagUpdate, db: AsyncSession) -> TagGet:
        query = (
            update(Tag)
            .where(Tag.name == tag_name)
            .values(tag.model_dump())
            .returning(Tag)
        )
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return TagGet(**row)
        else:
            raise ValueError(f"No tag found with ID: {tag_name}")

    @staticmethod
    async def delete_tag(tag_name: str, db: AsyncSession) -> None:
        query = delete(Tag).where(Tag.name == tag_name)
        await db.execute(query)

    @staticmethod
    async def get_related_media(tag_name: str, db: AsyncSession) -> list[MediaList]:
        query = select(Media).join(Tag.media).where(Tag.name == tag_name)
        result = await db.execute(query)
        media = result.fetchall()

        if media:
            return [MediaList(**media[0].to_dict()) for media in media]
        return []
