import logging

from pydantic import EmailStr
from sqlalchemy import delete, exists, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import UserCRUD
from src.database.models import Group, Media, User, user_group_association
from src.database.schemas import GroupCreate, GroupGet, GroupUpdate, PublicUser

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class GroupCRUD:
    @staticmethod
    async def create_group(group: GroupCreate, db: AsyncSession) -> GroupGet:
        query = insert(Group).returning(Group).values(**group.model_dump())
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            association_query = user_group_association.insert().values(
                user_mail=group.owner_mail, group_id=row.id
            )
            await db.execute(association_query)
            return GroupGet(**row)
        else:
            raise ValueError("Failed to create group. No row returned.")

    @staticmethod
    async def get_group(group_id: int, db: AsyncSession) -> GroupGet:
        query = select(Group).where(Group.id == group_id)
        result = await db.execute(query)
        group_data = result.fetchone()

        if group_data:
            return GroupGet(**group_data[0].to_dict())
        else:
            raise ValueError(f"No group found with ID: {group_id}")

    @staticmethod
    async def get_groups(db: AsyncSession) -> list[GroupGet]:
        query = select(Group)
        result = await db.execute(query)
        groups_data = result.fetchall()
        return [GroupGet(**group[0].to_dict()) for group in groups_data]

    @staticmethod
    async def update_group(
        group_id: int, group: GroupUpdate, db: AsyncSession
    ) -> GroupGet:
        query = (
            update(Group)
            .values(**group.model_dump())
            .returning(Group)
            .where(Group.id == group_id)
        )
        result = await db.execute(query)
        row = result.fetchone()

        if row:
            return GroupGet(**row)
        else:
            raise ValueError(f"No group found with ID: {group_id}")

    @staticmethod
    async def delete_group(group_id: int, db: AsyncSession) -> None:
        await db.execute(delete(Media).where(Media.group_id == group_id))
        await db.execute(
            delete(user_group_association).where(
                user_group_association.c.group_id == group_id
            )
        )
        await db.execute(delete(Group).where(Group.id == group_id))

    @staticmethod
    async def add_users_to_group(
        group_id: int,
        user_mails: list[EmailStr],
        db: AsyncSession,
    ) -> None:
        for user_mail in user_mails:
            membership_query = select(
                exists().where(
                    (user_group_association.c.user_mail == user_mail)
                    & (user_group_association.c.group_id == group_id)
                )
            )
            result = await db.execute(membership_query)
            is_member = result.scalar()

            if not is_member:
                association_query = insert(user_group_association).values(
                    user_mail=user_mail, group_id=group_id
                )
                await db.execute(association_query)

    @staticmethod
    async def get_users_in_group(group_id: int, db: AsyncSession) -> list[PublicUser]:
        query = (
            select(User)
            .join(user_group_association)
            .where(user_group_association.c.group_id == group_id)
        )
        result = await db.execute(query)
        users_data = result.fetchall()
        return [PublicUser(**user[0].to_dict()) for user in users_data]

    @staticmethod
    async def get_user_groups(user_mail: EmailStr, db: AsyncSession) -> list[GroupGet]:
        await UserCRUD.get_user(user_mail, db)
        query = (
            select(Group)
            .join(user_group_association)
            .join(User)
            .where(User.mail == user_mail)
        )
        result = await db.execute(query)
        groups = result.fetchall()
        return [GroupGet(**group[0].to_dict()) for group in groups]

    @staticmethod
    async def get_user_owned_groups(
        user_mail: EmailStr, db: AsyncSession
    ) -> list[GroupGet]:
        query = select(Group).where(Group.owner_mail == user_mail)
        result = await db.execute(query)
        groups = result.fetchall()
        return [GroupGet(**group[0].to_dict()) for group in groups]

    @staticmethod
    async def remove_user_from_group(
        group_id: int,
        member_mail: str,
        db: AsyncSession,
    ) -> None:
        await GroupCRUD.get_group(group_id, db)
        await UserCRUD.get_user(member_mail, db)

        query = (
            delete(user_group_association)
            .where(user_group_association.c.group_id == group_id)
            .where(user_group_association.c.user_mail == member_mail)
        )
        await db.execute(query)
