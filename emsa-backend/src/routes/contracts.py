from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    mail: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    name: str = ""


class AddFriendRequest(BaseModel):
    friend_mail: str


class AddGroupMembersRequest(BaseModel):
    members: list[EmailStr]


class ProposeTagsRequest(BaseModel):
    name: str
    is_image: bool
    image_path: str = ""
    link: str = ""


class ProposeTagsResponse(BaseModel):
    proposed_tags: list[str]


class AddLinkRequest(BaseModel):
    group_id: int
    link: str
    name: str
    tags: list[str] = []
