import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.media import MediaCRUD
from src.crud.tag import TagCRUD
from src.database.models import Tag
from src.database.schemas import MediaCreate, TagCreate, TagUpdate
from src.tests.conftest import MEDIA_DATA_1, TAGS_1


@pytest.mark.asyncio
async def test_tag_create(db_session: AsyncSession, two_media_on_groups):
    media, _ = two_media_on_groups
    before_creation_select = await db_session.execute(select(Tag))
    before_creation_count = len(before_creation_select.fetchall())

    tag_create = TagCreate(name=TAGS_1[0].name)
    await TagCRUD.create_tag(tag_create, db_session, media.id)

    after_creation_select = await db_session.execute(select(Tag))
    after_creation_count = len(after_creation_select.fetchall())

    assert after_creation_count == before_creation_count + 1


@pytest.mark.asyncio
async def test_tag_get(db_session: AsyncSession, two_media_on_groups):
    media, _ = two_media_on_groups
    created_tag = await TagCRUD.create_tag(
        TagCreate(name=TAGS_1[0].name), db_session, media.id
    )
    tag = await TagCRUD.get_tag(created_tag.name, db_session)

    assert tag.model_dump(exclude={"id"}) == TAGS_1[0].model_dump()


@pytest.mark.asyncio
async def test_tag_list(db_session: AsyncSession, two_media_on_groups):
    media, _ = two_media_on_groups
    await TagCRUD.create_tag(TagCreate(name=TAGS_1[0].name), db_session, media.id)
    await TagCRUD.create_tag(TagCreate(name=TAGS_1[1].name), db_session, media.id)
    tags = await TagCRUD.get_tags(db_session)

    assert len(tags) == 2
    assert tags[0].model_dump(exclude={"id"}) == TAGS_1[0].model_dump()


@pytest.mark.asyncio
async def test_tag_update(db_session: AsyncSession):
    tag_1 = await TagCRUD.create_tag(TagCreate(name=TAGS_1[0].name), db_session)
    update_model = TagUpdate(name="Updated Tag Name")
    updated_tag = await TagCRUD.update_tag(tag_1.name, update_model, db_session)

    assert update_model.name == updated_tag.name
    assert tag_1.name != updated_tag.name


@pytest.mark.asyncio
async def test_tag_delete(db_session: AsyncSession):
    tag = await TagCRUD.create_tag(TagCreate(name=TAGS_1[0].name), db_session)
    before_deletion_select = await db_session.execute(select(Tag))
    before_deletion_count = len(before_deletion_select.fetchall())

    await TagCRUD.delete_tag(tag.name, db_session)

    after_deletion_select = await db_session.execute(select(Tag))
    after_deletion_count = len(after_deletion_select.fetchall())

    assert after_deletion_count == before_deletion_count - 1


@pytest.mark.asyncio
async def test_media_tag_creation(db_session: AsyncSession, two_groups):
    media_create = MediaCreate(**{"group_id": two_groups[0].id, **MEDIA_DATA_1})
    media = await MediaCRUD.create_media(media_create, db_session, TAGS_1)
    tags = await TagCRUD.get_tags(db_session)

    assert media.tags == tags
    assert media.model_dump(exclude={"id", "tags"}) == media_create.model_dump()


@pytest.mark.asyncio
async def test_get_media_related_to_tag(db_session: AsyncSession, two_groups):
    media_create = MediaCreate(**{"group_id": two_groups[0].id, **MEDIA_DATA_1})
    media = await MediaCRUD.create_media(media_create, db_session, TAGS_1)
    tags = await MediaCRUD.get_related_tags(media.id, db_session)

    assert {tag.name for tag in tags} == {tag.name for tag in TAGS_1}
