from pydantic import BaseModel, EmailStr


class PublicUser(BaseModel):
    mail: EmailStr
    name: str = ""


class PrivateUser(PublicUser):
    password_hash: str


class UpdateUser(BaseModel):
    name: str | None = None
    password_hash: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_mail: EmailStr


class LoginRequest(BaseModel):
    mail: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    name: str = ""


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


class MediaCreate(BaseModel):
    group_id: int
    is_image: bool
    image_path: str = ""
    link: str = ""
    tags: list[str] = []


class MediaList(MediaCreate):
    id: int


class MediaGet(MediaList):
    ...


class MediaUpdate(BaseModel):
    is_image: bool | None = None
    image_path: str | None = None
    link: str | None = None


class MediaQuery(BaseModel):
    search_term: str | None = None
