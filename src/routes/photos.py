from fastapi import Depends, status, APIRouter, File, UploadFile, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from src.services.roles import RoleAccess
from src.database.db import get_db
from src.database.models import User
from src.repository import photos as repository_photos
from src.schemas.photos import PhotoResponse, PhotoQRCodeResponse
from src.services.auth import auth_service
from src.services.photos import upload_photo
import src.conf.messages as messages

router = APIRouter(prefix='/photos', tags=['photos'])

allowed_operations = {
    'admin': ['C', 'R', 'U', 'D'],
    'moderator': [],
    'user': ['C', 'R', 'U', 'D'],
}


@router.post('/', response_model=PhotoResponse, name='Create photo', status_code=status.HTTP_201_CREATED, 
             dependencies=[Depends(RoleAccess(allowed_operations, "C"))])
async def create_photo(photo: UploadFile = File(),
                       description: str | None = None,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    url, public_id = upload_photo(photo)
    photo = await repository_photos.add_photo(url, public_id, description, db, current_user)
    return photo


@router.get('/', response_model=list[PhotoResponse], name="Get photos by request ",
            dependencies=[Depends(RoleAccess(allowed_operations, "R"))])
async def get_photos(skip: int = 0, limit: int = Query(default=10, ge=1, le=50),
                     tag_name: Optional[str] = Query(default=None),
                     user: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    photos = await repository_photos.get_photos({'tag_name': tag_name},
                                                skip,
                                                limit,
                                                db)
    if len(photos) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photos


@router.get('/{photo_id}', response_model=PhotoResponse, name="Get photos by id ", 
            dependencies=[Depends(RoleAccess(allowed_operations, "R"))])
async def get_photo_id(photo_id: int,
                       db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.get_photo_by_id(photo_id, db, user)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photo


@router.patch('/{photo_id}', response_model=PhotoResponse, name="Update photo's description", 
              dependencies=[Depends(RoleAccess(allowed_operations, "U"))])
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


@router.delete('/{photo_id}', status_code=status.HTTP_204_NO_CONTENT, 
               dependencies=[Depends(RoleAccess(allowed_operations, "D"))])
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


@router.post('/qrcode/', response_model=PhotoQRCodeResponse, name='Generate QRCode by url',
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RoleAccess(allowed_operations, "C"))])
async def generate_qrcode(photo_url: str, _: User = Depends(auth_service.get_current_user)):
    qrcode_encode = await repository_photos.generate_qrcode(photo_url)
    return qrcode_encode
