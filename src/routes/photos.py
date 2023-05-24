import json
import types
from datetime import date
from fastapi import Depends, status, APIRouter, File, UploadFile, Query, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import Response#, HTMLResponse

from typing import Optional
from src.repository.photo_transformations import create_transformation, create_transformation_from_preset

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import photos as repository_photos
from src.repository import photo_transformations as repository_photo_transformations
from src.schemas.photos import PhotoResponse#, PhotoQRCodeResponse
from src.services.auth import auth_service
from src.services.photos import upload_photo
import src.conf.messages as messages
from src.services.roles import RoleAccess
#from src.repository import rates as repository_rates
from src.schemas.photo_transformations import PhotoTransformationModel
    

router = APIRouter(prefix='/photos', tags=['photos'])

# CRUD
allowed_create = RoleAccess([Role.admin, Role.user])
allowed_read = RoleAccess([Role.admin, Role.user])
allowed_update = RoleAccess([Role.admin, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post('/', name='Create Photo',
             response_model=PhotoResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
# accsess - admin, authenticated users
async def create_photo(photo: UploadFile = File(),
                       description: str | None = None,
                       tags: str = None,
                       has_trans: bool = False,
                       transformation: str = PhotoTransformationModel.Config.schema_extra['example'],
                       save_filter: bool = Query(default=False),
                       filter_name: Optional[str] = Query(default=None),
                       filter_description: Optional[str] = Query(default=None),
                       filter_id: int = None,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    url, public_id = upload_photo(photo)
    photo = await repository_photos.add_photo(url, public_id, description, tags, db, current_user)
    if has_trans:
        try:
            if type(transformation) == str:
                transformation = transformation.replace('\'', '\"')
                transformation = json.loads(transformation)
            if transformation.get("transformation"):
                transformation_obj = types.SimpleNamespace(**transformation)
                transformation_obj.transformation = types.SimpleNamespace(**transformation_obj.transformation)
            
                transformation_obj.photo_id = photo.id
                url_transf = await create_transformation(transformation_obj,
                                    save_filter,
                                    filter_name,
                                    filter_description,
                                    current_user.id,
                                    current_user.roles.value,
                                    db) 
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.BAD_REQUEST)  
    if filter_id:
        photo_id = photo.id
        transformation = await \
        create_transformation_from_preset(filter_id, 
                                          photo_id, 
                                          filter_description,
                                          current_user.id,
                                          current_user.roles.value, 
                                          db)     
        
    return photo


@router.get('/qrcode/',
             name='Generate QRCode By Url',
             response_class=Response,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
# access - admin, authenticated users
async def generate_qrcode(photo_url: Optional[str]= Query(default=None),
                          photo_id: Optional[int]= Query(default=None),
                          trans_id: Optional[int]= Query(default=None),
                          _: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    qr_code_url = None
    if photo_id:
        photo = await repository_photos.get_photo_by_id_oper(photo_id, db)
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
        qr_code_url = photo.url_photo
    elif trans_id:
        transformation = await repository_photo_transformations.get_transformation_by_id(trans_id, db)
        if not transformation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
        qr_code_url = transformation.transformed_url
    qr_code_url = qr_code_url or photo_url
    if not qr_code_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    qrcode_encode = await repository_photos.generate_qrcode(qr_code_url)
    return qrcode_encode


@router.get('/', name="Get Photos By Request ",
            response_model=list[PhotoResponse],
            dependencies=[Depends(allowed_read)])
# accsess - admin, authenticated users
async def get_photos(user_id: Optional[int] = Query(default=None),
                     tag_name: Optional[str] = Query(default=None),
                     rate_min: Optional[float] = Query(default=None),
                     rate_max: Optional[float] = Query(default=None),
                     created_at_min: Optional[date] = Query(default=None),
                     created_at_max: Optional[date] = Query(default=None),
                     limit: int = Query(default=10, ge=1, le=50),
                     offset: int = 0,
                     cur_user: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    photos = await repository_photos.get_photos(user_id, cur_user.id, cur_user.roles, tag_name, rate_min,
                                                rate_max, created_at_min, created_at_max,
                                                limit, offset, db)
    if not photos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photos


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
