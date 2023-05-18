from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import photo_filters as photo_filters
from src.schemas.photo_filters import PhotoFilterDbModel, PhotoFilterModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/photos/filters", tags=['photo filters'])

allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post('/', response_model=PhotoFilterDbModel,
             name='Create photo filter', status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
async def create_foto_filter(photo_filter: PhotoFilterModel,
                             db: Session = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    p_filter = await photo_filters.create_foto_filter(photo_filter, user.id, db)
    return p_filter
