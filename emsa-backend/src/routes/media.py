import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.authorization import get_current_active_user
from src.crud.group import GroupCRUD
from src.crud.media import MediaCRUD
from src.database.schemas import MediaCreate, MediaGet, MediaUpdate, PublicUser
from src.database.session import get_db
from src.routes.contracts import AddLinkRequest, ProposeTagsRequest, ProposeTagsResponse
from src.services.cloud_storage import (
    CloudStorage,
    FailedToDeleteImageException,
    FailedToUploadImageException,
)
from src.services.preview_generator import link_preview_generator, preview_link_upload
from src.services.tag_proposer import propose_tag_from_link, propose_tags_from_name

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/propose_tags",
    summary="Propose tags for media",
    description="Retrieve a list of proposed tags for a given media link or image."
    " Tags are created by media name and possibly by link domain",
    response_model=ProposeTagsResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Proposed tags retrieved successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Media not found",
            "content": {"application/json": {}},
        },
    },
)
async def proposed_tags(
    request: ProposeTagsRequest,
    _: PublicUser = Depends(get_current_active_user),
) -> ProposeTagsResponse:
    tags = propose_tags_from_name(request.name)
    if not request.is_image:
        tag = propose_tag_from_link(request.link)
        tags.append(tag) if tag else None
    return ProposeTagsResponse(proposed_tags=tags)


@router.post(
    "/add_link",
    status_code=status.HTTP_201_CREATED,
    summary="Add link to group",
    description="Add a link to an existing group by group_id.",
    response_model=MediaGet,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Link added successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Group not found",
            "content": {"application/json": {}},
        },
    },
)
async def add_link(
    link_media: AddLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> MediaGet:
    media_db_data = MediaCreate(
        group_id=link_media.group_id,
        is_image=False,
        image_path="",
        link=link_media.link,
        name=link_media.name,
        uploaded_by=current_user.mail,
        tags=link_media.tags,
    )
    try:
        media = await MediaCRUD.create_media(media_db_data, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    thumbnail = await link_preview_generator(link_media.link)
    if isinstance(thumbnail, bytes):
        preview_link = await preview_link_upload(thumbnail, media.id)
    else:
        preview_link = thumbnail

    try:
        return await MediaCRUD.update_media(
            media.id,
            MediaUpdate(preview_link=preview_link),
            db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/add_image",
    status_code=status.HTTP_201_CREATED,
    summary="Add image to group",
    description="Add an image to an existing group by group_id.",
    response_model=MediaGet,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Image added successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Group not found",
            "content": {"application/json": {}},
        },
    },
)
async def add_image(
    group_id: int = Form(...),
    name: str = Form(...),
    tags: list[str] = Form([]),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> MediaCreate:
    image_bytes = await image.read()
    if len(image_bytes) >= 2 * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail="File size exceeds the allowed limit of 2MB"
        )
    try:
        group = await GroupCRUD.get_group(group_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    media_db_data = MediaCreate(
        group_id=group_id,
        is_image=True,
        image_path="placeholder",
        link="",
        name=name,
        uploaded_by=current_user.mail,
        tags=tags,
    )
    try:
        media = await MediaCRUD.create_media(media_db_data, db)
    except ValueError as e:
        logger.error(
            f"Failed to upload image={media_db_data.model_dump()}. For user={current_user.mail}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    cloud_storage = CloudStorage()
    try:
        media_cloud_key = await cloud_storage.upload_image(
            str(media.id), image_bytes, group.name
        )
    except FailedToUploadImageException:
        logger.error(
            f"Failed to upload image={media_db_data.model_dump()}. For user={current_user.mail}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image",
        )

    try:
        return await MediaCRUD.update_media(
            media.id,
            MediaUpdate(image_path=media_cloud_key, preview_link=media_cloud_key),
            db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete(
    "/delete_media",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete media",
    description="Delete an existing media by media_id.",
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Media deleted successfully",
            "content": {"application/json": {}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Media not found",
            "content": {"application/json": {}},
        },
    },
)
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: PublicUser = Depends(get_current_active_user),
) -> None:
    try:
        media = await MediaCRUD.get_media(media_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    try:
        group = await GroupCRUD.get_group(media.group_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if media.is_image:
        cloud_storage = CloudStorage()
        try:
            await cloud_storage.delete_image(str(media.id), group.name)
        except FailedToDeleteImageException:
            logger.error(
                f"Failed to delete image={media.model_dump()}. For user={current_user.mail}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete image",
            )

    try:
        await MediaCRUD.delete_media_from_db(media_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
