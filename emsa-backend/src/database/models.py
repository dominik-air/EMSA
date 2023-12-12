from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src.database.session import Base


class TimestampMixin:
    created_at: DateTime = Column(DateTime(timezone=True), server_default=func.now())


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

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User(user_mail={self.mail}, username={self.name})>"

    def to_dict(self) -> dict:
        return {
            "mail": self.mail,
            "password_hash": self.password_hash,
            "name": self.name,
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


media_tags_association = Table(
    "media_tags_association",
    Base.metadata,
    Column("media_id", Integer, ForeignKey("media.id"), primary_key=True),
    Column("tag_name", String, ForeignKey("tags.name"), primary_key=True),
)


class Media(Base, TimestampMixin):
    __tablename__ = "media"

    id: int = Column(Integer, primary_key=True)
    group_id: int = Column(Integer, ForeignKey("groups.id"), nullable=False)
    is_image: bool = Column(Boolean, nullable=False)
    image_path: str = Column(String)
    link: str = Column(String)

    # many-to-one relationship with the Group
    group: Group = relationship("Group", back_populates="media")

    # many-to-many relationship with Tags
    tags: list["Tag"] = relationship(
        "Tag", secondary=media_tags_association, back_populates="media"
    )

    def __repr__(self) -> str:
        return (
            f"<Media("
            f"id={self.id}, "
            f"group_id={self.group_id}, "
            f"is_image={self.is_image}, "
            f"image_path={self.image_path}, "
            f"link={self.link})>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "group_id": self.group_id,
            "is_image": self.is_image,
            "image_path": self.image_path,
            "link": self.link,
        }


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"
    name: str = Column(String(64), primary_key=True)

    # many-to-many relationship with Media
    media: list["Media"] = relationship(
        "Media", secondary=media_tags_association, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag(name={self.name})>"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
        }
