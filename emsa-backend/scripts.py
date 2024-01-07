"""
This module is for developers usage only!

For now, it contains script that load example data to database for local development.
To run script go into emsa-app Docker instance terminal and run:
`python scripts.py`
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.crud.user import FriendCRUD, UserCRUD
from src.database.schemas import GroupCreate, MediaCreate, PrivateUser
from src.database.session import async_session_global

USER_1 = PrivateUser(mail="abc@gmail.com", name="Dominik", password_hash="admin")
USER_2 = PrivateUser(mail="bzak@agh.pl", name="Bartosz", password_hash="admin")
USER_3 = PrivateUser(mail="ewa@example.com", name="EL_wariatka", password_hash="admin")
USER_4 = PrivateUser(mail="radek@example.com", name="Radik", password_hash="admin")

GROUP_1 = GroupCreate(name="Group 1", owner_mail="abc@gmail.com")
GROUP_2 = GroupCreate(name="Group 2", owner_mail="bzak@agh.pl")

TAGS_1 = ["Bike", "FUNNY", "fall"]
TAGS_2 = ["Travel", "Adventure"]

MEDIA_DATA_1 = {
    "is_image": True,
    "image_path": "https://i.chzbgr.com/full/9353383424/h13AAB7B7/funny-meme-from-madagascar-about-zoning-out-when-someone-else-is-talking",
    "tags": TAGS_1,
    "name": "Old but funny",
}
MEDIA_DATA_2 = {
    "is_image": False,
    "link": "tiktok.com/dominik-air",
    "tags": TAGS_1[1::],
    "name": "Old tiktok star",
}
MEDIA_DATA_3 = {"is_image": True, "image_path": "https://p16-sign.tiktokcdn-us.com/tos-useast5-p-0068-tx/oAfIEChK23MO9ZYQALA0I9LUwAibByACqUBpti~tplv-photomode-zoomcover:720:720.jpeg?x-expires=1704733200&x-signature=Qagm7THdLQr8F9Q7YEobUZnkR0o%3D", "tags": TAGS_2}
MEDIA_DATA_4 = {"is_image": False, "link": "example.com/video", "tags": TAGS_2[1::]}


async def add_data_for_local_dev(db: AsyncSession) -> dict:
    users = [
        USER_1,
        USER_2,
        USER_3,
        USER_4,
    ]
    for user in users:
        user.password_hash = (
            "scrypt:32768:8:1$O24V30qxDjRHhlwn$7cea465c1467953d3460ffa361627b2437f9"
            "7f5588def1276c0b84f5f5c15bbb468b31a86493ce455268628a8509f1b156e122c62c57c"
            "be950b1d95d8363053c"
        )
    # user_1, user_2, user_3, user_4 = await asyncio.gather(
    #     *[UserCRUD.create_user(user, db) for user in users]
    # )
    user_1 = await UserCRUD.create_user(users[0], db)
    user_2 = await UserCRUD.create_user(users[1], db)
    user_3 = await UserCRUD.create_user(users[2], db)
    user_4 = await UserCRUD.create_user(users[3], db)

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


async def run_script() -> None:
    db = async_session_global()
    try:
        data = await add_data_for_local_dev(db)
        await db.commit()
        print("Data loaded!")
        print("Dummy data:", data)
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_script())
