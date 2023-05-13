from fastapi import Depends, status, APIRouter, File, UploadFile, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from src.database.db import get_db
from src.database.models import User
from src.repository import photos as repository_photos
from src.schemas.photos import PhotoResponse, PhotoModel
from src.services.auth import auth_service
from src.services.photos import upload_photo
import src.conf.messages as messages

router = APIRouter(prefix='/photos', tags=['photos'])


@router.post('/', response_model=PhotoResponse, name='Create photo', status_code=status.HTTP_201_CREATED)
async def create_photo(photo: UploadFile = File(),
                       description: str | None = None,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """The create_photo function creates a new photo in the database.
    :param photo: UploadFile: Upload a file to the server
    :param db: Session: Get a database session
    :param current_user: User: Get the user that is currently logged in
    :return: A photo object
    :doc-author: Trelent """
    # public_id = update_filename(photo.filename)
    url = upload_photo(photo)
    photo = await repository_photos.add_photo(url, description, db, current_user)
    return photo


@router.get('/', response_model=PhotoResponse, name="Get photo by request ")
async def get_photo(
        skip: int = 0, limit: int = Query(default=10, ge=1, le=50),
        photo_id: Optional[int] = Query(default=None),
        tags: Optional[list] = Query(default=None),
        username: Optional[str] = Query(default=None),
        db: Session = Depends(get_db),
):
    photo = await repository_photos.get_photo(skip, limit,
                                              photo_id, tags,
                                              username, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photo


@router.patch('/photo_description', response_model=PhotoResponse, name="Update photo's description")
async def photo_description_update(
        new_description: str,
        skip: int = 0, limit: int = Query(default=10, ge=1, le=50),
        photo_id: Optional[int] = Query(default=None),
        tags: Optional[list] = Query(default=None),
        username: Optional[str] = Query(default=None),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    updated_photo = await repository_photos.description_update(new_description,
                                                               skip, limit,
                                                               photo_id,
                                                               tags,
                                                               username,
                                                               db, current_user)
    if updated_photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return updated_photo


@router.delete('/photo_delete', status_code=status.HTTP_204_NO_CONTENT)
async def photo_delete(
        skip: int = 0, limit: int = Query(default=10, ge=1, le=50),
        photo_id: Optional[int] = Query(default=None),
        tags: Optional[list] = Query(default=None),
        username: Optional[str] = Query(default=None),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    photo = await repository_photos.delete_photo(
                                                skip, limit,
                                                photo_id,
                                                tags,
                                                username,
                                                db, current_user)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photo
