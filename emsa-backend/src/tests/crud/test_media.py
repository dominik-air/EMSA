import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.media import MediaCRUD, TagCRUD
from src.database.models import Media
from src.database.schemas import MediaCreate, MediaGet, MediaUpdate
from src.tests.conftest import MEDIA_DATA_1, TAGS_1


@pytest.mark.asyncio
async def test_media_create(db_session: AsyncSession, two_groups: list):
    before_creation_select = await db_session.execute(select(Media))
    before_creation_count = len(before_creation_select.fetchall())

    media_create = MediaCreate(**{"group_id": two_groups[0].id, **MEDIA_DATA_1})
    await MediaCRUD.create_media(media_create, db_session)

    after_creation_select = await db_session.execute(select(Media))
    after_creation_count = len(after_creation_select.fetchall())

    assert after_creation_count == before_creation_count + 1


@pytest.mark.asyncio
async def test_media_get(db_session: AsyncSession, two_media_on_groups: list[MediaGet]):
    media = await MediaCRUD.get_media(two_media_on_groups[0].id, db_session)

    assert media.model_dump() == two_media_on_groups[0].model_dump()


@pytest.mark.asyncio
async def test_media_list(
    db_session: AsyncSession, two_media_on_groups: list[MediaGet]
):
    media_list = await MediaCRUD.get_all_media(db_session)

    assert len(media_list) == 2
    for i, media in enumerate(media_list):
        assert media.model_dump() == two_media_on_groups[i].model_dump(exclude={"tags"})


@pytest.mark.asyncio
async def test_media_update(
    db_session: AsyncSession, two_media_on_groups: list[MediaGet]
):
    media = two_media_on_groups[0]
    update_model = MediaUpdate(
        **{"is_image": False, "image_path": "", "link": "https://example.com/new"}
    )
    updated_media = await MediaCRUD.update_media(media.id, update_model, db_session)
    get_updated_media = await MediaCRUD.get_media(media.id, db_session)

    assert updated_media.id == get_updated_media.id == media.id
    assert updated_media.is_image == get_updated_media.is_image == update_model.is_image
    assert (
        updated_media.image_path
        == get_updated_media.image_path
        == update_model.image_path
    )
    assert updated_media.link == get_updated_media.link == update_model.link


@pytest.mark.asyncio
async def test_media_delete(
    db_session: AsyncSession, two_media_on_groups: list[MediaGet]
):
    media = two_media_on_groups[0]
    before_deletion_select = await db_session.execute(select(Media))
    before_deletion_count = len(before_deletion_select.fetchall())

    await MediaCRUD.delete_media(media.id, db_session)

    after_deletion_select = await db_session.execute(select(Media))
    after_deletion_count = len(after_deletion_select.fetchall())

    assert after_deletion_count == before_deletion_count - 1


@pytest.mark.asyncio
async def test_get_related_tags(db_session: AsyncSession, two_groups):
    media_create = MediaCreate(**{"group_id": two_groups[0].id, **MEDIA_DATA_1})
    media = await MediaCRUD.create_media(media_create, db_session, TAGS_1)

    related_media = await TagCRUD.get_related_media(TAGS_1[0].name, db_session)

    assert media.model_dump(exclude={"tags"}) == related_media[0].model_dump()


@pytest.mark.asyncio
async def test_get_media_by_group(
    db_session: AsyncSession, two_media_on_groups: list[MediaGet]
):
    group_id = two_media_on_groups[0].group_id
    another_media = MediaCreate(**{"group_id": group_id, **MEDIA_DATA_1})
    expected_media = [
        two_media_on_groups[0],
        await MediaCRUD.create_media(another_media, db_session),
    ]

    media_list = await MediaCRUD.get_media_by_group(group_id, db_session)

    assert len(media_list) == 2
    for i, media in enumerate(media_list):
        assert media.model_dump() == expected_media[i].model_dump(exclude={"tags"})
