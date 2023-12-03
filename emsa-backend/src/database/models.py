from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from werkzeug.security import check_password_hash, generate_password_hash

from src.database.session import Base


class User(Base):
    __tablename__ = "user"
    mail = Column(String(100), primary_key=True, unique=True, index=True)
    password_hash = Column(String(255))
    name = Column(String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(user_mail={self.mail}, username={self.name})>"

    def to_dict(self):
        return {
            "mail": self.mail,
            "password_hash": self.password_hash,
            "name": self.name,
        }


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    is_image = Column(Boolean)
    image_path = Column(Text)
    link = Column(Text)


class Group(Base):
    __tablename__ = "group"
    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(100))


class GroupsMapping(Base):
    __tablename__ = "groups_mapping"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("group.group_id"))
    mail = Column(String(100), ForeignKey("user.mail"))


class FriendsMapping(Base):
    __tablename__ = "friends_mapping"
    id = Column(Integer, primary_key=True)
    user_mail_1 = Column(String(100), ForeignKey("user.mail"))
    user_mail_2 = Column(String(100), ForeignKey("user.mail"))


class MediaMapping(Base):
    __tablename__ = "media_mapping"
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    user_mail = Column(String(100), ForeignKey("user.mail"))
    group_id = Column(Integer, ForeignKey("group.group_id"))
