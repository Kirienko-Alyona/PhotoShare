from fastapi import Depends, status, APIRouter, File, UploadFile, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import photos as repository_photos
from src.schemas.photos import PhotoResponse, PhotoUpdate, PhotoQRCodeResponse
from src.schemas.tags import TagModel
from src.services.auth import auth_service
from src.services.photos import upload_photo
import src.conf.messages as messages
from src.services.roles import RoleAccess

router = APIRouter(prefix='/photos', tags=['photos'])

#CRUD
allowed_create = RoleAccess([Role.admin, Role.user])
allowed_read = RoleAccess([Role.admin, Role.user])
allowed_update = RoleAccess([Role.admin, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post('/', response_model=PhotoResponse, name='Create photo', status_code=status.HTTP_201_CREATED, dependencies=[Depends(allowed_create)])
# accsess - admin, authenticated users
async def create_photo(photo: UploadFile = File(),
                       description: str | None = None,
                       tags: str = None,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    url, public_id = upload_photo(photo)
    photo = await repository_photos.add_photo(url, public_id, description, tags, db, current_user)
    return photo


@router.post('/qrcode/', response_model=PhotoQRCodeResponse, name='Generate QRCode by url',
             status_code=status.HTTP_201_CREATED, dependencies=[Depends(allowed_create)])
# accsess - admin, authenticated users
async def generate_qrcode(photo_url: str, _: User = Depends(auth_service.get_current_user)):
    qrcode_encode = await repository_photos.generate_qrcode(photo_url)
    return qrcode_encode


@router.get('/', response_model=list[PhotoResponse], name="Get photos by request ", dependencies=[Depends(allowed_read)])
# accsess - admin, authenticated users
async def get_photos(tag_name: Optional[str] = Query(default=None),
                     limit: int = Query(default=10, ge=1, le=50), 
                     offset: int = 0, 
                     _: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    photos = await repository_photos.get_photos_by_tag_name(tag_name, limit, offset, db)
    if len(photos) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photos


@router.get('/{photo_id}', response_model=PhotoResponse, name="Get photos by id ", dependencies=[Depends(allowed_read)])
# accsess - admin, authenticated users
async def get_photo_id(photo_id: int,
                       db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.get_photo_by_id(photo_id, db, user)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photo


@router.put("/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(allowed_update)])
# accsess - admin, user-owner
async def update_tags_by_photo(photo_id: int,
                               new_description: str | None = None,
                               tags: str = None,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.update_tags_descriptions_for_photo(
                                photo_id, 
                                new_description, 
                                tags, 
                                db, 
                                current_user)
    if photo:
        return photo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)


@router.patch("/untach_tag/{photo_id}", response_model=PhotoResponse, status_code=status.HTTP_200_OK, dependencies=[Depends(allowed_update)])
# accsess - admin, user-owner
async def untach_tag_photo(photo_id: int,
                           tags: str,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.untach_tag(photo_id, tags, db, current_user)
    if photo:
        return photo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)


@router.delete('/{photo_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allowed_delete)])
# accsess - admin, moderator, user-owner
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
