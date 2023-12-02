from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import check_password_hash, generate_password_hash

Base = declarative_base()


class Logins(Base):
    __tablename__ = "logins"
    user_mail = Column(String(100), primary_key=True, unique=True, index=True)
    password_hash = Column(String(255))
    user_name = Column(String(100))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Logins(user_mail={self.user_mail}, user_name={self.user_name})>"


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    is_image = Column(Boolean)
    image_path = Column(Text)
    link = Column(Text)


class Groups(Base):
    __tablename__ = "groups"
    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(100))


class GroupsMapping(Base):
    __tablename__ = "groups_mapping"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    user_mail = Column(String(100), ForeignKey("logins.user_mail"))


class FriendsMapping(Base):
    __tablename__ = "friends_mapping"
    id = Column(Integer, primary_key=True)
    user_mail_1 = Column(String(100), ForeignKey("logins.user_mail"))
    user_mail_2 = Column(String(100), ForeignKey("logins.user_mail"))


class MediaMapping(Base):
    __tablename__ = "media_mapping"
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    user_mail = Column(String(100), ForeignKey("logins.user_mail"))
    group_id = Column(Integer, ForeignKey("groups.group_id"))
