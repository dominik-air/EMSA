# group.py
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Group
from src.database.schemas import GroupCreate, GroupGet, GroupUpdate


class GroupCRUD:
    @staticmethod
    async def create_group(group: GroupCreate, db: AsyncSession) -> GroupGet:
        query = (
            insert(Group)
            .returning(Group)
            .values(
                **group.model_dump(exclude={"owner_mail"}), owner_mail=group.owner_mail
            )
        )
        result = await db.execute(query)
        row = result.fetchone()

        if row:
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
        query = delete(Group).where(Group.id == group_id)
        await db.execute(query)
