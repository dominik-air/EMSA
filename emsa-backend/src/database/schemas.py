from pydantic import BaseModel


class PublicUser(BaseModel):
    mail: str
    name: str = ""


class PrivateUser(PublicUser):
    password_hash: str


class UpdateUser(BaseModel):
    name: str | None = None
    password_hash: str | None = None
