from fastapi import HTTPException, status
from typing import Optional

from sqlalchemy.orm import Session

import src.conf.messages as message
from src.database.models import PhotoFilter
from src.schemas.photo_filters import PhotoFilterModel, PhotoFilterDbModel


async def get_filter_by_id(filter_id: int, db: Session) -> Optional[PhotoFilter]:
    return db.query(PhotoFilter).get(filter_id)


async def create_foto_filter(data: PhotoFilterModel, user_id: int, db: Session) -> PhotoFilterDbModel:
    new_filter = PhotoFilter(**data.dict(), user_id=user_id)

    db.add(new_filter)
    db.commit()
    db.refresh(new_filter)

    return new_filter
