from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.conf import messages
from src.repository import photos as repository_photos
from src.repository import rates as repository_rates
from src.schemas.rates import RateModel, RateResponse, RateDetailResponse, RateDeleteModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/rating", tags=['rating'])

allowed_operations = {
    'admin': ['R', 'D'],
    'moderator': ['R', 'D'],
    'user': ['C', 'R'],
}


@router.post("/", response_model=RateResponse, name="Set rate to photo",
             status_code=status.HTTP_201_CREATED, 
             dependencies=[Depends(RoleAccess(allowed_operations, "C"))])
async def create_rate(body: RateModel, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_photos.get_photo_by_id(body.photo_id, db, current_user)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    if photo.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
    existing_rate = await repository_rates.get_rate_photo_by_user(body.photo_id, db, current_user)
    if existing_rate is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.DUPLICATE_RATING)
    rate = await repository_rates.add_rate(body, db, current_user)
    return rate


@router.get("/{photo_id}", response_model=RateResponse, name="Return photo rating by photo id",
            status_code=status.HTTP_200_OK, dependencies=[Depends(RoleAccess(allowed_operations, "R"))])
async def get_rating_by_photo_id(photo_id: int = Path(ge=1), db: Session = Depends(get_db),
                                 _: User = Depends(auth_service.get_current_user)):
    print(_.roles)
    rating = await repository_rates.get_rating_by_photo_id(photo_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return rating


@router.get("/detail/{photo_id}", response_model=List[RateDetailResponse],
            name="Return detail rating by photo id",
            status_code=status.HTTP_200_OK, dependencies=[Depends(RoleAccess(allowed_operations, "R"))])
async def get_rating_by_photo_id(photo_id: int = Path(ge=1), db: Session = Depends(get_db),
                                 _: User = Depends(auth_service.get_current_user)):
    rating = await repository_rates.get_detail_rating_by_photo(photo_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return rating


@router.delete("/detail", name="Delete user's photo rating", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RoleAccess(allowed_operations, "D"))])
async def remove_rate(body: RateDeleteModel, db: Session = Depends(get_db),
                      _: User = Depends(auth_service.get_current_user)):
    deleted_count = await repository_rates.remove_rating(body, db)
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return None
