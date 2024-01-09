"""
This module is for developers usage only!

For now, it contains script that load example data to database for local development.
To run script go into emsa-app Docker instance terminal and run:
`python scripts.py`

Group 1 has 3 users and most content
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.crud.user import UserCRUD
from src.crud.friend import FriendCRUD
from src.database.schemas import GroupCreate, MediaCreate, PrivateUser
from src.database.session import async_session_global

USER_1 = PrivateUser(mail="dominik@example.com", name="Dominik", password_hash="admin")
USER_2 = PrivateUser(mail="bzak@example.com", name="Bartosz", password_hash="admin")
USER_3 = PrivateUser(mail="ewa@example.com", name="Ewa", password_hash="admin")
USER_4 = PrivateUser(mail="radek@example.com", name="Radek", password_hash="admin")
USER_5 = PrivateUser(mail="igor@example.com", name="Igor", password_hash="admin")

GROUP_1 = GroupCreate(name="Group DBE", owner_mail="dominik@example.com")
GROUP_2 = GroupCreate(name="Group BR", owner_mail="bzak@example.com")
GROUP_3 = GroupCreate(name="Group DB", owner_mail="dominik@example.com")

TAGS_1 = ["Bike", "FUNNY", "fall"]
TAGS_2 = ["Travel", "Adventure"]

MEDIA_DATA_1 = {
    "is_image": True,
    "image_path": "https://i1.kwejk.pl/k/obrazki/2012/12/e5ef9d0089e9a9beec32575841b0686a_original.jpg",
    "tags": ["bartek", "to", "nie", "imie", "error"],
    "name": "Bartek to nie imie",
}
MEDIA_DATA_2 = {
    "is_image": True,
    "image_path": "https://i1.kwejk.pl/k/obrazki/2013/01/7a11d23a6f899c49c96e8d7150ef0a40_original.jpg",
    "tags": ["dominik", "to", "nie", "imie", "nos"],
    "name": "Dominik to nie imie",
}
MEDIA_DATA_3 = {
    "is_image": True,
    "image_path": "https://www.blasty.pl/upload/images/large/2017/01/przynajmniej-nie-mam-na-imie-radek_2017-01-25_12-36-17.jpg",
    "tags": ["przynajmniej", "nie", "imie", "radek"],
    "name": "Radek to nie imie",
}
MEDIA_DATA_4 = {
    "is_image": True,
    "image_path": "https://naukawpolsce.pl/sites/default/files/202005/dejsomsiad.jpg",
    "tags": ["somsiad", "sąsiad", "nosacz"],
    "name": "Somsiad nosacz",
}
MEDIA_DATA_5 = {
    "is_image": True,
    "image_path": "https://static.polityka.pl/_resource/res/path/fb/b1/fbb14f40-8d27-411b-830a-1df4d13b98b6_f1400x900",
    "tags": ["fal", "podsiadlo", "milionerzy"],
    "name": "",
}
MEDIA_DATA_6 = {
    "is_image": True,
    "image_path": "https://d-art.ppstatic.pl/kadry/k/r/1/87/31/65574960d99be_o_medium.jpg",
    "tags": ["fryzura", "oczekiwania", "rzeczywistosc"],
    "name": "",
}
MEDIA_DATA_7 = {
    "is_image": True,
    "image_path": "https://pobierak.jeja.pl/images/8/1/7/273340_oczekiwania-vs-rzeczywistosc.jpg",
    "tags": ["oczekiwania", "rzeczywistosc", "jeansy", "obelix"],
    "name": "",
}
MEDIA_DATA_8 = {
    "is_image": True,
    "image_path": "https://img1.dmty.pl//uploads/202007/1593622779_bi9ynq_600.jpg",
    "tags": ["oczekiwania", "rzeczywistosc", "ciastko"],
    "name": "",
}
MEDIA_DATA_9 = {
    "is_image": True,
    "image_path": "https://i1.kwejk.pl/k/obrazki/2022/10/JrYjT5ZSU0qo2FBV.jpg",
    "tags": ["nerd", "podobaja", "geek", "ona"],
    "name": "",
}
MEDIA_DATA_10 = {
    "is_image": True,
    "image_path": "https://as1.ftcdn.net/v2/jpg/03/16/01/06/1000_F_316010690_Wm9W2fSc2KTVvuyuJDZSb7xDNZ77q0qC.jpg",
    "tags": ["nerd", "okulary"],
    "name": "",
}
MEDIA_DATA_11 = {
    "is_image": True,
    "image_path": "https://i.pinimg.com/736x/65/78/33/657833ddecc987d1f9f267c02636986d.jpg",
    "tags": ["nerd", "okulary", "actually"],
    "name": "",
}


async def add_data_for_local_dev(db: AsyncSession) -> dict:
    users = [
        USER_1,
        USER_2,
        USER_3,
        USER_4,
        USER_5,
    ]
    for user in users:
        user.password_hash = (
            "scrypt:32768:8:1$O24V30qxDjRHhlwn$7cea465c1467953d3460ffa361627b2437f9"
            "7f5588def1276c0b84f5f5c15bbb468b31a86493ce455268628a8509f1b156e122c62c57c"
            "be950b1d95d8363053c"
        )
    user_1 = await UserCRUD.create_user(users[0], db)
    user_2 = await UserCRUD.create_user(users[1], db)
    user_3 = await UserCRUD.create_user(users[2], db)
    user_4 = await UserCRUD.create_user(users[3], db)
    user_5 = await UserCRUD.create_user(users[4], db)

    # 2 groups owned by user 1 and 2
    group_1 = await GroupCRUD.create_group(GROUP_1, db)
    group_2 = await GroupCRUD.create_group(GROUP_2, db)
    group_3 = await GroupCRUD.create_group(GROUP_3, db)

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

    # Add user_1 and user_2 to group_3
    await GroupCRUD.add_users_to_group(group_3.id, [user_1.mail, user_2.mail], db)

    # Add content into group 1
    media_1 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_1})
    media_2 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_2})
    media_3 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_3})
    media_4 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_4})
    media_5 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_5})
    media_6 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_6})
    media_7 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_7})
    media_8 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_8})
    media_9 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_9})
    media_10 = MediaCreate(**{"group_id": group_1.id, **MEDIA_DATA_10})
    media_1 = await MediaCRUD.create_media(media_1, db)
    media_2 = await MediaCRUD.create_media(media_2, db)
    media_3 = await MediaCRUD.create_media(media_3, db)
    media_4 = await MediaCRUD.create_media(media_4, db)
    media_5 = await MediaCRUD.create_media(media_5, db)
    media_6 = await MediaCRUD.create_media(media_6, db)
    media_7 = await MediaCRUD.create_media(media_7, db)
    media_8 = await MediaCRUD.create_media(media_8, db)
    media_9 = await MediaCRUD.create_media(media_9, db)
    media_10 = await MediaCRUD.create_media(media_10, db)
    # Add content into group 2 and 3
    media_21 = MediaCreate(**{"group_id": group_2.id, **MEDIA_DATA_8})
    media_22 = MediaCreate(**{"group_id": group_2.id, **MEDIA_DATA_9})
    media_23 = MediaCreate(**{"group_id": group_2.id, **MEDIA_DATA_10})
    media_31 = MediaCreate(**{"group_id": group_3.id, **MEDIA_DATA_8})
    media_32 = MediaCreate(**{"group_id": group_3.id, **MEDIA_DATA_9})
    media_33 = MediaCreate(**{"group_id": group_3.id, **MEDIA_DATA_10})
    media_21 = await MediaCRUD.create_media(media_21, db)
    media_22 = await MediaCRUD.create_media(media_22, db)
    media_23 = await MediaCRUD.create_media(media_23, db)
    media_31 = await MediaCRUD.create_media(media_31, db)
    media_32 = await MediaCRUD.create_media(media_32, db)
    media_33 = await MediaCRUD.create_media(media_33, db)


    return {
        "user_ids": [user.mail for user in users],
        "passwords": "admin",
        "group_ids": [group_1.id, group_2.id, group_3.id],
        "media_ids": [
            media_1.id,
            media_2.id,
            media_3.id,
            media_4.id,
            media_5.id,
            media_6.id,
            media_7.id,
            media_8.id,
            media_9.id,
            media_10.id,
            media_21.id,
            media_22.id,
            media_23.id,
            media_31.id,
            media_32.id,
            media_33.id,
        ],
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
