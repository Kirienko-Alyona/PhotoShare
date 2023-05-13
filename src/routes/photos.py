from typing import Annotated

from fastapi import Depends, status, APIRouter, File, UploadFile, Form, HTTPException, Path
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import photos as repository_photos
from src.schemas.photos import PhotoResponse
from src.services.auth import auth_service
from src.services.photos import upload_photo

router = APIRouter(prefix="/photos", tags=['photos'])


@router.post('/', response_model=PhotoResponse, name='Create photo', status_code=status.HTTP_201_CREATED)
async def create_photo(photo: Annotated[UploadFile, File()],
                       description: Annotated[str, Form()],
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_photo function creates a new photo in the database.

    :param description:
    :param photo: UploadFile: Upload a file to the server
    :param db: Session: Get a database session
    :param current_user: User: Get the user that is currently logged in
    :return: A photo object
    :doc-author: Trelent
    """
    url = upload_photo(photo)
    photo = await repository_photos.add_photo(url, description, db, current_user)
    return photo


@router.delete("/{photo_id}",
               response_model=PhotoResponse,
               name='Delete photo',
               status_code=status.HTTP_202_ACCEPTED)
async def remove_photo(photo_id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.delete_photo(photo_id, db, current_user)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo
