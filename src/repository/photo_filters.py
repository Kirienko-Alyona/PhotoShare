from typing import Optional, List

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

import src.conf.messages as message
from src.database.models import PhotoFilter, Role
from src.schemas.photo_filters import PhotoFilterModel, PhotoFilterDbModel
from src.schemas.photo_transformations import TransformationModel

advanced_roles_create = []
advanced_roles_update = [Role.admin]
advanced_roles_delete = [Role.admin]


async def get_filter_by_id(filter_id: int, db: Session) -> Optional[PhotoFilter]:
    return db.get(PhotoFilter, filter_id)


async def get_photo_filter_user_id(filter_id: int, db: Session) -> int:
    return db.query(PhotoFilter.user_id).filter_by(id=filter_id).one()[0]


async def get_filter_preset_by_id(filter_id: int, db: Session) -> Optional[TransformationModel]:
    return db.query(PhotoFilter.preset).filter_by(id=filter_id).one()[0]


async def advanced_rights_check(filter_id: int,
                                cur_user_id: int,
                                cur_user_role: Role,
                                advanced_roles: List[Role],
                                db: Session):
    owner_id = await get_photo_filter_user_id(filter_id, db)
    allowed = cur_user_role in advanced_roles or owner_id == cur_user_id
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message.FORBIDDEN)


async def get_photos_filters(user_id: int, db: Session) -> Optional[List]:
    return db.query(PhotoFilter).filter_by(user_id=user_id).order_by(PhotoFilter.name).all()


async def create_photo_filter(data: PhotoFilterModel, user_id: int, db: Session) -> PhotoFilterDbModel:
    new_filter = PhotoFilter(**data.dict(), user_id=user_id)

    db.add(new_filter)
    db.commit()
    db.refresh(new_filter)

    return new_filter


async def update_photo_filter(filter_id: int, data: PhotoFilterModel,
                              user_id: int, user_role: Role, db: Session) -> Optional[PhotoFilterDbModel]:
    ph_filter = await get_filter_by_id(filter_id, db)
    if ph_filter:
        await advanced_rights_check(filter_id, user_id,
                                    user_role, advanced_roles_update, db)
        count = db.query(PhotoFilter).filter_by(id=filter_id).update(
            {'name': data.name, 'description': data.description, 'preset': data.preset},
            synchronize_session="fetch")
        db.commit()
        if count == 1:
            return ph_filter


async def remove_photo_filter(filter_id: int, user_id: int, user_role: Role, db: Session) -> Optional[int]:
    ph_filter = await get_filter_by_id(filter_id, db)
    if ph_filter:
        await advanced_rights_check(filter_id, user_id,
                                    user_role, advanced_roles_delete, db)
        db.query(PhotoFilter).filter_by(id=filter_id).delete(synchronize_session="fetch")
        db.commit()
        return ph_filter.id
