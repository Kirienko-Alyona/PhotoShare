from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

import src.conf.messages as messages
from src.database.db import get_db
from src.database.models import User, Role
from src.repository import photo_transformations as repository_transformations
from src.schemas.photo_transformations import (
    PhotoTransformationModelDb,
    PhotoTransformationModel,
    NewDescTransformationModel)
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/transformations", tags=['photo transformations'])


allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get('/{photo_id}', 
            name='Get Transformations By Photo Id',
            response_model=List[PhotoTransformationModelDb],
            dependencies=[Depends(allowed_read)])
async def get_transformed_photos(photo_id: int,
                                 db: Session = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    photos = await repository_transformations.get_transformed_photos(photo_id, user.id, user.roles, db)
    if not photos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return photos


@router.post('/', 
             name='Create Photo Transformation', 
             response_model=PhotoTransformationModelDb,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
async def create_transformation(transformation: PhotoTransformationModel,
                                save_filter: bool = Query(default=False),
                                filter_name: Optional[str] = Query(default=None),
                                filter_description: Optional[str] = Query(default=None),
                                db: Session = Depends(get_db),
                                user: User = Depends(auth_service.get_current_user)):
    transformation = await repository_transformations.create_transformation(transformation,
                                                                            save_filter,
                                                                            filter_name,
                                                                            filter_description,
                                                                            user.id, user.roles, db)
    if transformation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COULD_NOT_FIND_FOTO)
    return transformation


@router.post('/filter_by/{photo_id}', 
             response_model=PhotoTransformationModelDb,
             name='Create Photo Transformation From Filter ', 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
async def create_transformation_from_preset(photo_id: int, 
                                            filter_id: int, 
                                            description: NewDescTransformationModel,
                                            db: Session = Depends(get_db),
                                            user: User = Depends(auth_service.get_current_user)):
    transformation = await \
        repository_transformations.create_transformation_from_preset(filter_id, photo_id, description,
                                                                     user.id, user.roles, db)
    if transformation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.COULD_NOT_FIND_FOTO)
    return transformation


@router.patch('/{trans_id}', response_model=PhotoTransformationModelDb,
              name='Changing Description Of Transformation', 
              status_code=status.HTTP_200_OK,
              dependencies=[Depends(allowed_update)])
async def change_description(trans_id: int, data: NewDescTransformationModel,
                             db: Session = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    transformation = await repository_transformations.change_description(trans_id, data, user.id, user.roles, db)
    if transformation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.COULD_NOT_FIND_FOTO_TRANSFORMATION)
    return transformation


@router.delete("/{trans_id}",
               name='Delete Photo Transformation',
               status_code=status.HTTP_204_NO_CONTENT, 
               dependencies=[Depends(allowed_delete)])
async def delete_transformation(trans_id: int,
                                db: Session = Depends(get_db),
                                user: User = Depends(auth_service.get_current_user)):
    id_ = await repository_transformations.remove_transformation(trans_id, user.id, user.roles, db)
    if id_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{messages.COULD_NOT_FIND_FOTO_TRANSFORMATION}')
