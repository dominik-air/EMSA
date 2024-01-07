import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.crud.user import FriendCRUD, UserCRUD
from src.database.schemas import MediaCreate
from src.tests.conftest import (
    GROUP_1,
    GROUP_2,
    MEDIA_DATA_1,
    MEDIA_DATA_2,
    MEDIA_DATA_3,
    MEDIA_DATA_4,
    USER_1,
    USER_2,
    USER_3,
    USER_4,
)


async def add_data_for_local_dev(db: AsyncSession) -> dict:
    users = [
        USER_1,
        USER_2,
        USER_3,
        USER_4,
    ]
    for user in users:
        user.password_hash = "scrypt:32768:8:1$O24V30qxDjRHhlwn$7cea465c1467953d3460ffa361627b2437f9" \
                             "7f5588def1276c0b84f5f5c15bbb468b31a86493ce455268628a8509f1b156e122c62c57c" \
                             "be950b1d95d8363053c"
    user_1, user_2, user_3, user_4 = await asyncio.gather(
        *[UserCRUD.create_user(user, db) for user in users]
    )

    # 2 groups owned by user 1 and 2
    group_1 = await GroupCRUD.create_group(GROUP_1, db)
    group_2 = await GroupCRUD.create_group(GROUP_2, db)

    # Make user_1, user_2, and user_3 friends and add them to group_1
    await FriendCRUD.add_friend(user_1.mail, user_2.mail, db)
    await FriendCRUD.add_friend(user_1.mail, user_3.mail, db)
    await FriendCRUD.add_friend(user_2.mail, user_3.mail, db)
    # user_1 is added while group creation, but it won't be added 2nd time if passed here
    await GroupCRUD.add_users_to_group(
        group_1.id, [user_1.mail, user_2.mail, user_3.mail], db
    )

    # Make user_2 and user_4 friends and add them to group_2
    await FriendCRUD.add_friend(user_2.mail, user_4.mail, db)
    await GroupCRUD.add_users_to_group(group_2.id, [user_2.mail, user_4.mail], db)

    # Add content into group 1 and 2
    media_1 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_1})
    media_2 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_2})
    media_3 = MediaCreate(**{"group_id": group_2.id, **MEDIA_DATA_3})
    media_4 = MediaCreate(**{"group_id": group_2.id, **MEDIA_DATA_4})
    media_1 = await MediaCRUD.create_media(media_1, db)
    media_2 = await MediaCRUD.create_media(media_2, db)
    media_3 = await MediaCRUD.create_media(media_3, db)
    media_4 = await MediaCRUD.create_media(media_4, db)

    return {
        "user_ids": [user.mail for user in users],
        "passwords": "admin",
        "group_ids": [group_1.id, group_2.id],
        "media_ids": [media_1.id, media_2.id, media_3.id, media_4.id],
    }
