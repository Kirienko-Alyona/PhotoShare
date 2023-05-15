from fastapi import Depends, status, APIRouter, File, UploadFile, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from src.database.db import get_db
from src.database.models import User
from src.repository import photos as repository_photos
from src.schemas.photos import PhotoResponse
from src.services.auth import auth_service
from src.services.photos import upload_photo
import src.conf.messages as messages

router = APIRouter(prefix='/photos', tags=['photos'])


@router.post('/', response_model=PhotoResponse, name='Create photo', status_code=status.HTTP_201_CREATED)
async def create_photo(photo: UploadFile = File(),
                       description: str | None = None,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):

    url = upload_photo(photo)
    photo = await repository_photos.add_photo(url, description, db, current_user)
    return photo


@router.get('/', response_model=list[PhotoResponse], name="Get photos by request ")
async def get_photos(skip: int = 0, limit: int = Query(default=10, ge=1, le=50),
                    tags: Optional[list] = Query(default=None),
                    user: User = Depends(auth_service.get_current_user),
                    db: Session = Depends(get_db)):
    photos = await repository_photos.get_photos({'tags': tags},
                                                skip,
                                                limit,
                                                user,
                                                db)
    if len(photos) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photos


@router.patch('/{photo_id}', response_model=PhotoResponse, name="Update photo's description")
async def photo_description_update(
        new_description: str,
        photo_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    updated_photo = await repository_photos.description_update(new_description,
                                                               photo_id,
                                                               db,
                                                               current_user)
    if updated_photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return updated_photo


@router.delete('/{photo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def photo_remove(
        photo_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    photo = await repository_photos.delete_photo(photo_id,
                                                 db, current_user)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photo
