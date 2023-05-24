from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

import src.conf.messages as messages
from src.database.db import get_db
from src.database.models import User, Role
from src.repository import photo_filters as photo_filters
from src.schemas.photo_filters import PhotoFilterDbModel, PhotoFilterModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/filters", tags=['photo filters'])

allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get('/my/', response_model=Optional[List[PhotoFilterDbModel]],
            name='Get photo filters by user',
            dependencies=[Depends(allowed_read)])
async def get_photos_filters(db: Session = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    ph_filters = await photo_filters.get_photos_filters(user.id, db)
    if not ph_filters:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{messages.COULD_NOT_FIND_FOTO_FILTER}')
    return ph_filters


@router.post('/', response_model=PhotoFilterDbModel,
             name='Create photo filter', status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
async def create_photo_filter(photo_filter: PhotoFilterModel,
                              db: Session = Depends(get_db),
                              user: User = Depends(auth_service.get_current_user)):
    ph_filter = await photo_filters.create_photo_filter(photo_filter, user.id, db)
    return ph_filter


@router.put('/{filter_id}', response_model=PhotoFilterDbModel,
            name='Update photo filter', status_code=status.HTTP_200_OK,
            dependencies=[Depends(allowed_update)])
async def update_photo_filter(filter_id: int, data: PhotoFilterModel,
                              db: Session = Depends(get_db),
                              user: User = Depends(auth_service.get_current_user)):

    ph_filter = await photo_filters.update_photo_filter(filter_id, data, user.id, user.roles, db)
    if ph_filter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=messages.COULD_NOT_FIND_FOTO_FILTER)
    return ph_filter


@router.delete("/{filter_id}",
               name='Delete photo filter',
               status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allowed_delete)])
async def delete_photo_filter(filter_id: int,
                              db: Session = Depends(get_db),
                              user: User = Depends(auth_service.get_current_user)):
    id_ = await photo_filters.remove_photo_filter(filter_id, user.id, user.roles, db)
    if id_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{messages.COULD_NOT_FIND_FOTO_FILTER}')
