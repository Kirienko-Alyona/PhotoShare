import json
import types
from fastapi import Depends, status, APIRouter, File, UploadFile, Query, HTTPException
from pydantic import Field, Json
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List, ClassVar, Type
from src.repository.photo_transformations import create_transformation

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import photos as repository_photos
from src.schemas.photos import PhotoResponse, PhotoUpdate, PhotoQRCodeResponse
from src.schemas.tags import TagModel
from src.services.auth import auth_service
from src.services.photos import upload_photo
import src.conf.messages as messages
from src.services.roles import RoleAccess
from src.repository import rates as repository_rates
from src.schemas.photo_transformations import (
    PhotoTransformationModelDb,
    PhotoTransformationModel,
    NewDescTransformationModel)

router = APIRouter(prefix='/photos', tags=['photos'])

# CRUD
allowed_create = RoleAccess([Role.admin, Role.user])
allowed_read = RoleAccess([Role.admin, Role.user])
allowed_update = RoleAccess([Role.admin, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])


default_transf = {
  "photo_id": 1,
  "description": "Photo with cool effect",
  "transformation": {
    "preset": [
      {
        "gravity": "face",
        "height": 400,
        "width": 400,
        "crop": "crop"
      },
      {
        "radius": "max"
      },
      {
        "width": 200,
        "crop": "scale"
      },
      {
        "fetch_format": "auto"
      }
    ]
  }
}

@router.post('/', name='Create Photo',
             response_model=PhotoResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
# accsess - admin, authenticated users
async def create_photo(photo: UploadFile = File(),
                       description: str | None = None,
                       tags: str = None,
                       data: str = PhotoTransformationModel.Config.schema_extra["example"],
                        #transformation: str = Field(default=default_transf),
                       #transformation: str = Json[PhotoTransformationModel.Config],
                       save_filter: bool = Query(default=False),
                       filter_name: Optional[str] = Query(default=None),
                       filter_description: Optional[str] = Query(default=None),
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    url, public_id = upload_photo(photo)
    try:
        if type(data) == str:
            data = json.loads(data)
        data = types.SimpleNamespace(**data)
        data.transformation = types.SimpleNamespace(**data.transformation)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.BAD_REQUEST)   
    photo = await repository_photos.add_photo(url, public_id, description, tags, db, current_user)
    data.photo_id = photo.id
    url_transf = await create_transformation(data,
                                save_filter,
                                filter_name,
                                filter_description,
                                current_user.id,
                                current_user.roles.value,
                                db) 
    return photo


@router.post('/qrcode/',
             name='Generate QRCode By Url',
             response_model=PhotoQRCodeResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
# accsess - admin, authenticated users
async def generate_qrcode(photo_url: str,
                          _: User = Depends(auth_service.get_current_user)):
    qrcode_encode = await repository_photos.generate_qrcode(photo_url)
    return qrcode_encode


@router.get('/', name="Get Photos By Request ",
            response_model=list[PhotoResponse],
            dependencies=[Depends(allowed_read)])
# accsess - admin, authenticated users
async def get_photos(tag_name: Optional[str] = Query(default=None),
                     limit: int = Query(default=10, ge=1, le=50),
                     offset: int = 0,
                     _: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    photos = await repository_photos.get_photos_by_tag_name(tag_name, limit, offset, db)
    photos_num = len(photos)
    if photos_num == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    result = []
    for photo in photos:
        photo_rating = await repository_rates.get_rating_by_photo_id(photo.id, db)
        photo_data = {
            'id': photo.id,
            'url_photo': photo.url_photo,
            'description': photo.description,
            'tags': photo.tags,
            'rating': photo_rating['average_rate']
        }
        result.append(photo_data)
    return result


@router.get('/{photo_id}', name="Get Photos By Id",
            response_model=PhotoResponse,
            dependencies=[Depends(allowed_read)])
# accsess - admin, authenticated users
async def get_photo_id(photo_id: int,
                       db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.get_photo_by_id(photo_id, db, user)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photo


@router.put("/{photo_id}",
            name="Update Photo",
            response_model=PhotoResponse,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(allowed_update)])
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


@router.patch("/untach_tag/{photo_id}",
              name="Untach Tag From Photo",
              response_model=PhotoResponse,
              status_code=status.HTTP_200_OK,
              dependencies=[Depends(allowed_update)])
# accsess - admin, user-owner
async def untach_tag_photo(photo_id: int,
                           tags: str,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.untach_tag(photo_id, tags, db, current_user)
    if photo:
        return photo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)


@router.delete('/{photo_id}',
               name="Remove Photo",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_delete)])
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
