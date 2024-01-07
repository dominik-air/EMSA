from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    cast,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.orm import relationship

from src.database.session import Base


class TimestampMixin:
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())


user_group_association = Table(
    "user_group_association",
    Base.metadata,
    Column("user_mail", String, ForeignKey("users.mail")),
    Column("group_id", Integer, ForeignKey("groups.id")),
)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    mail: str = Column(String(64), primary_key=True, index=True)
    password_hash: str = Column(String(255), nullable=False)
    name: str = Column(String(64), nullable=False, default=mail)

    # many-to-many relationship with the User
    friendships: list["Friendship"] = relationship(
        "Friendship", back_populates="users", foreign_keys="Friendship.friend_mail"
    )
    # many-to-many relationship with the Group
    groups: list["Group"] = relationship(
        "Group", secondary=user_group_association, back_populates="users"
    )
    # one-to-many relationship with the Group
    owned_groups: list["Group"] = relationship(
        "Group", back_populates="owner", uselist=True
    )
    token: "Token" = relationship("Token", back_populates="user")
    # one-to-many relationship with FriendRequest (sent requests)
    sent_friend_requests: list["FriendRequest"] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.sender_mail",
        back_populates="sender",
    )
    # one-to-many relationship with FriendRequest (received requests)
    received_friend_requests: list["FriendRequest"] = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_mail",
        back_populates="receiver",
    )

    def __repr__(self) -> str:
        return f"<User(user_mail={self.mail}, username={self.name})>"

    def to_dict(self) -> dict:
        return {
            "mail": self.mail,
            "password_hash": self.password_hash,
            "name": self.name,
        }


class Token(Base):
    __tablename__ = "tokens"

    access_token = Column(String(450), primary_key=True)
    is_active = Column(Boolean, nullable=False, default=False)
    user_mail = Column(String(64), ForeignKey("users.mail"))
    user: "User" = relationship("User", back_populates="token")

    def __repr__(self) -> str:
        return (
            f"<Token("
            f"access_token={self.access_token}, "
            f"is_active={self.is_active}, "
            f"user_mail={self.user_mail})>"
        )

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "is_active": self.is_active,
            "user_mail": self.user_mail,
        }


class FriendRequest(Base, TimestampMixin):
    __tablename__ = "friend_requests"

    id: int = Column(Integer, primary_key=True)
    sender_mail: str = Column(String, ForeignKey("users.mail"), nullable=False)
    receiver_mail: str = Column(String, ForeignKey("users.mail"), nullable=False)

    sender: User = relationship("User", foreign_keys=[sender_mail])
    receiver: User = relationship("User", foreign_keys=[receiver_mail])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender_mail": self.sender_mail,
            "receiver_mail": self.receiver_mail,
        }


class Friendship(Base, TimestampMixin):
    __tablename__ = "friendships"

    id: int = Column(Integer, primary_key=True)
    friend_mail: str = Column(String, ForeignKey("users.mail"))
    user_mail: str = Column(String, ForeignKey("users.mail"))

    # many-to-one relationship with the User
    users: User = relationship(
        "User", back_populates="friendships", foreign_keys=[user_mail]
    )
    friend: User = relationship(
        "User", back_populates="friendships", foreign_keys=[friend_mail]
    )


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(64), nullable=False)
    owner_mail: str = Column(String, ForeignKey("users.mail"), nullable=False)
    owner: User = relationship("User", back_populates="owned_groups")

    # many-to-many relationship with the User
    users: list["User"] = relationship(
        "User", secondary=user_group_association, back_populates="groups"
    )
    # one-to-many relationship with the Media
    media: list["Media"] = relationship("Media", back_populates="group")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "owner_mail": self.owner_mail,
        }


class Media(Base, TimestampMixin):
    __tablename__ = "media"

    id: int = Column(Integer, primary_key=True)
    group_id: int = Column(Integer, ForeignKey("groups.id"), nullable=False)
    name: str = Column(String, nullable=False, default="")
    is_image: bool = Column(Boolean, nullable=False)
    image_path: str = Column(String)
    link: str = Column(String)
    tags: list[str] = Column(
        ARRAY(Text), nullable=False, default=cast(array([], type_=Text), ARRAY(Text))
    )

    # many-to-one relationship with the Group
    group: Group = relationship("Group", back_populates="media")

    def __repr__(self) -> str:
        return (
            f"<Media("
            f"id={self.id}, "
            f"group_id={self.group_id}, "
            f"name={self.name}, "
            f"is_image={self.is_image}, "
            f"image_path={self.image_path}, "
            f"link={self.link}, "
            f"tags={self.tags})>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "group_id": self.group_id,
            "name": self.name,
            "is_image": self.is_image,
            "image_path": self.image_path,
            "link": self.link,
            "tags": self.tags,
        }
