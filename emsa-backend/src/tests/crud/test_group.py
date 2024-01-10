import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.database.models import Group, user_group_association
from src.database.schemas import GroupCreate, GroupGet, GroupUpdate, PrivateUser
from src.tests.conftest import GROUP_1, USER_1


@pytest.mark.asyncio
async def test_group_create(db_session: AsyncSession, two_users: list[PrivateUser]):
    before_creation_select = await db_session.execute(select(Group))
    before_creation_count = len(before_creation_select.fetchall())

    group_create = GroupCreate(name=GROUP_1.name, owner_mail=two_users[0].mail)
    await GroupCRUD.create_group(group_create, db_session)

    after_creation_select = await db_session.execute(select(Group))
    after_creation_count = len(after_creation_select.fetchall())

    assert after_creation_count == before_creation_count + 1


@pytest.mark.asyncio
async def test_group_get(db_session: AsyncSession, two_users: list[PrivateUser]):
    group_create = GroupCreate(name=GROUP_1.name, owner_mail=two_users[0].mail)
    created_group = await GroupCRUD.create_group(group_create, db_session)
    group = await GroupCRUD.get_group(created_group.id, db_session)

    assert group.model_dump(exclude={"id"}) == GROUP_1.model_dump()


@pytest.mark.asyncio
async def test_group_list(db_session: AsyncSession, two_groups: list[GroupGet]):
    groups = await GroupCRUD.get_groups(db_session)

    assert len(groups) == 2
    for i, group in enumerate(groups):
        assert group.model_dump() == two_groups[i].model_dump()


@pytest.mark.asyncio
async def test_group_update(db_session: AsyncSession, two_groups: list[GroupGet]):
    group_1 = two_groups[0]
    group_2 = two_groups[1]
    update_model = GroupUpdate(name=group_2.owner_mail, owner_mail=group_2.owner_mail)
    updated_group = await GroupCRUD.update_group(group_1.id, update_model, db_session)
    get_updated_group = await GroupCRUD.get_group(group_1.id, db_session)

    assert group_1.id == updated_group.id == get_updated_group.id
    assert (
        update_model.owner_mail
        == updated_group.owner_mail
        == get_updated_group.owner_mail
    )
    assert update_model.name == updated_group.name == get_updated_group.name


@pytest.mark.asyncio
async def test_group_delete(db_session: AsyncSession, two_groups: list[GroupGet]):
    group = two_groups[0]
    before_deletion_select = await db_session.execute(select(Group))
    before_deletion_count = len(before_deletion_select.fetchall())

    await GroupCRUD.delete_group(group.id, db_session)

    after_deletion_select = await db_session.execute(select(Group))
    after_deletion_count = len(after_deletion_select.fetchall())

    assert after_deletion_count == before_deletion_count - 1


@pytest.mark.asyncio
async def test_add_users_to_group_and_get_users(
    db_session: AsyncSession, two_users: list[PrivateUser]
):
    user_1, user_2 = two_users
    group_create = GroupCreate(name=GROUP_1.name, owner_mail=user_1.mail)
    created_group = await GroupCRUD.create_group(group_create, db_session)

    users_in_group_before = await GroupCRUD.get_users_in_group(
        created_group.id, db_session
    )
    await GroupCRUD.add_users_to_group(
        group_id=created_group.id,
        user_mails=[user_1.mail, user_2.mail],
        db=db_session,
    )
    users_in_group = await GroupCRUD.get_users_in_group(created_group.id, db_session)

    assert len(users_in_group_before) == 1
    assert len(users_in_group) == 2
    assert user_1.mail and user_2.mail in [user.mail for user in users_in_group]


@pytest.mark.asyncio
async def test_get_user_group(db_session: AsyncSession, two_users: list[PrivateUser]):
    user_1, user_2 = two_users
    group_create = GroupCreate(name=GROUP_1.name, owner_mail=user_1.mail)
    created_group = await GroupCRUD.create_group(group_create, db_session)
    await GroupCRUD.add_users_to_group(
        group_id=created_group.id,
        user_mails=[user_1.mail, user_2.mail],
        db=db_session,
    )
    user_groups = await GroupCRUD.get_user_groups(
        user_1.mail,
        db=db_session,
    )

    assert len(user_groups) == 1
    assert user_groups == [created_group]


@pytest.mark.asyncio
async def test_remove_user_from_group(
    db_session: AsyncSession, two_users: list[PrivateUser]
):
    user_1, user_2 = two_users
    group_create = GroupCreate(name=GROUP_1.name, owner_mail=user_1.mail)
    created_group = await GroupCRUD.create_group(group_create, db_session)
    await GroupCRUD.add_users_to_group(
        group_id=created_group.id,
        user_mails=[user_1.mail, user_2.mail],
        db=db_session,
    )

    users_in_group_before = await GroupCRUD.get_users_in_group(
        created_group.id, db_session
    )
    await GroupCRUD.remove_user_from_group(
        group_id=created_group.id, member_mail=user_2.mail, db=db_session
    )
    users_in_group_after = await GroupCRUD.get_users_in_group(
        created_group.id, db_session
    )

    assert len(users_in_group_before) == 2
    assert len(users_in_group_after) == 1
    assert user_1.mail in [user.mail for user in users_in_group_after]
    assert user_2.mail not in [user.mail for user in users_in_group_after]

    association_query = (
        select(user_group_association)
        .where(user_group_association.c.group_id == created_group.id)
        .where(user_group_association.c.user_mail == user_2.mail)
    )
    association_result = await db_session.execute(association_query)
    assert association_result.fetchone() is None

    @pytest.mark.asyncio
    async def test_remove_user_from_group_owner_change(
        db_session: AsyncSession, two_users: list[PrivateUser]
    ):
        user_1, user_2 = two_users
        group_create = GroupCreate(name=GROUP_1.name, owner_mail=user_1.mail)
        created_group = await GroupCRUD.create_group(group_create, db_session)
        await GroupCRUD.add_users_to_group(
            group_id=created_group.id,
            user_mails=[user_1.mail, user_2.mail],
            db=db_session,
        )

        users_in_group_before = await GroupCRUD.get_users_in_group(
            created_group.id, db_session
        )
        await GroupCRUD.remove_user_from_group(
            group_id=created_group.id, member_mail=user_1.mail, db=db_session
        )
        users_in_group_after = await GroupCRUD.get_users_in_group(
            created_group.id, db_session
        )

        assert len(users_in_group_before) == 2
        assert len(users_in_group_after) == 1
        assert user_2.mail in [user.mail for user in users_in_group_after]
        assert user_1.mail not in [user.mail for user in users_in_group_after]

        association_query = (
            select(user_group_association)
            .where(user_group_association.c.group_id == created_group.id)
            .where(user_group_association.c.user_mail == user_1.mail)
        )
        association_result = await db_session.execute(association_query)
        assert association_result.fetchone() is None

        updated_group = await GroupCRUD.get_group(created_group.id, db_session)
        assert updated_group.owner_mail == user_2.mail


@pytest.mark.asyncio
async def test_remove_last_user_from_group(
    db_session: AsyncSession, two_groups: list[GroupGet]
):
    group_1, _ = two_groups
    await GroupCRUD.remove_user_from_group(
        group_id=group_1.id, member_mail=USER_1.mail, db=db_session
    )

    with pytest.raises(ValueError):
        await GroupCRUD.get_group(group_1.id, db_session)
