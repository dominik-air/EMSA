from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import UserCRUD


def validate_not_self(
    first_mail: str,
    second_mail: str,
) -> None:
    if first_mail == second_mail:
        raise ValueError("Can't send friend request to yourself")


async def validate_user_exist(
    mail: str,
    db: AsyncSession,
) -> None:
    await UserCRUD.get_user(mail, db)
