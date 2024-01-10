from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    mail: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    name: str = ""


class UpdateUserRequest(BaseModel):
    name: str | None = None
    password: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GetPendingRequests(BaseModel):
    name: str
    mail: str


class GetSentRequests(GetPendingRequests):
    ...


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
