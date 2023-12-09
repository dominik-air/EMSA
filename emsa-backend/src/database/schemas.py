from pydantic import BaseModel, EmailStr


class PublicUser(BaseModel):
    mail: EmailStr
    name: str = ""


class PrivateUser(PublicUser):
    password_hash: str


class UpdateUser(BaseModel):
    name: str | None = None
    password_hash: str | None = None


class FriendshipCreate(BaseModel):
    user_mail: EmailStr
    friend_mail: EmailStr


class GroupCreate(BaseModel):
    name: str
    owner_mail: EmailStr


class GroupGet(GroupCreate):
    id: int


class GroupUpdate(BaseModel):
    name: str | None = None
    owner_mail: EmailStr | None = None


class TagCreate(BaseModel):
    name: str


class TagGet(TagCreate):
    ...


class TagUpdate(BaseModel):
    name: str | None = None


class MediaCreate(BaseModel):
    group_id: int
    is_image: bool
    image_path: str = ""
    link: str = ""


class MediaList(MediaCreate):
    id: int


class MediaGet(MediaList):
    tags: list[TagGet]


class MediaUpdate(BaseModel):
    is_image: bool | None = None
    image_path: str | None = None
    link: str | None = None
