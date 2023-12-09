import pytest
from pydantic import ValidationError

from src.database.schemas import (
    FriendshipCreate,
    GroupCreate,
    GroupGet,
    GroupUpdate,
    MediaCreate,
    MediaGet,
    MediaList,
    MediaUpdate,
    PrivateUser,
    PublicUser,
    TagCreate,
    TagGet,
    TagUpdate,
    UpdateUser,
)


def test_public_user():
    data = {"mail": "test@example.com", "name": "John"}
    user = PublicUser(**data)
    assert user.model_dump() == data


def test_private_user():
    data = {
        "mail": "test@example.com",
        "name": "John",
        "password_hash": "hashed_password",
    }
    user = PrivateUser(**data)
    assert user.model_dump() == data


def test_update_user():
    data = {"name": "John", "password_hash": "hashed_password"}
    user_update = UpdateUser(**data)
    assert user_update.model_dump() == data


def test_friendship_create():
    data = {"user_mail": "user1@example.com", "friend_mail": "user2@example.com"}
    friendship = FriendshipCreate(**data)
    assert friendship.model_dump() == data


def test_group_create():
    data = {"name": "Group 1", "owner_mail": "owner@example.com"}
    group = GroupCreate(**data)
    assert group.model_dump() == data


def test_group_get():
    data = {"id": 1, "name": "Group 1", "owner_mail": "owner@example.com"}
    group_get = GroupGet(**data)
    assert group_get.model_dump() == data


def test_group_update():
    data = {"name": "Updated Group", "owner_mail": "updated_owner@example.com"}
    group_update = GroupUpdate(**data)
    assert group_update.model_dump() == data


def test_tag_create():
    data = {"name": "Tag1"}
    tag = TagCreate(**data)
    assert tag.model_dump() == data


def test_tag_get():
    data = {"name": "Tag1"}
    tag_get = TagGet(**data)
    assert tag_get.model_dump() == data


def test_tag_update():
    data = {"name": "UpdatedTag"}
    tag_update = TagUpdate(**data)
    assert tag_update.model_dump() == data


def test_media_create():
    data = {
        "group_id": 1,
        "is_image": True,
        "image_path": "image.jpg",
        "link": "example.com",
    }
    media = MediaCreate(**data)
    assert media.model_dump() == data


def test_media_list():
    data = {
        "id": 1,
        "group_id": 1,
        "is_image": True,
        "image_path": "image.jpg",
        "link": "example.com",
    }
    media_list = MediaList(**data)
    assert media_list.model_dump() == data


def test_media_get():
    data = {
        "id": 1,
        "group_id": 1,
        "is_image": True,
        "image_path": "image.jpg",
        "link": "example.com",
        "tags": [{"name": "Tag1"}],
    }
    media_get = MediaGet(**data)
    assert media_get.model_dump() == data


def test_media_update():
    data = {
        "is_image": False,
        "image_path": "updated_image.jpg",
        "link": "updated_example.com",
    }
    media_update = MediaUpdate(**data)
    assert media_update.model_dump() == data


def test_invalid_public_user():
    with pytest.raises(ValidationError):
        PublicUser(mail="invalid_email")
