from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.conf import messages
from src.repository import photos as repository_photos
from src.repository import rates as repository_rates
from src.schemas.rates import RateModel, RateResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/rating", tags=['rating'])

# CRUD
allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_web_admin_read = RoleAccess([Role.admin, Role.moderator])
# allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator])


@router.post("/", name="Set Rate To Photo", 
             response_model=RateResponse,
             status_code=status.HTTP_201_CREATED, 
             dependencies=[Depends(allowed_create)])
async def create_rate(body: RateModel, 
                      db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.get_photo_by_id_oper(body.photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)
    if photo.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
    existing_rate = await repository_rates.get_rate_photo_by_user(body.photo_id, db, current_user)
    if existing_rate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.DUPLICATE_RATING)
    rate = await repository_rates.add_rate(body, db, current_user)
    return rate


@router.get("/{photo_id}",  name="Return Rating By Photo Id",
            response_model=List[RateResponse],
            status_code=status.HTTP_200_OK, 
            dependencies=[Depends(allowed_web_admin_read)])
async def get_rating_by_photo_id(photo_id: int = Path(ge=1), 
                                 db: Session = Depends(get_db),
                                 _: User = Depends(auth_service.get_current_user)):
    rates = await repository_rates.get_detail_rating_by_photo(photo_id, db)
    if rates is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return rates


@router.delete("/{photo_id}", name="Delete User's Photo Rating",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_delete)])
async def remove_rate(photo_id: int = Path(ge=1), user_id: int = Path(ge=1),
                      db: Session = Depends(get_db),
                      _: User = Depends(auth_service.get_current_user)):
    deleted_count = await repository_rates.remove_rating(photo_id, user_id, db)
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return None
