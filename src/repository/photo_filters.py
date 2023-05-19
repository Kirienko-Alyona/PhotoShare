from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import PhotoFilter, Role
from src.repository.functions import advanced_rights_check
from src.schemas.photo_filters import PhotoFilterModel, PhotoFilterDbModel
from src.schemas.photo_transformations import TransformationModel

advanced_roles_update = [Role.admin]
advanced_roles_delete = [Role.admin]


async def get_filter_by_id(filter_id: int, db: Session) -> Optional[PhotoFilter]:
    return db.query(PhotoFilter).get(filter_id)


async def get_photo_filter_user_id(filter_id: int, db: Session) -> int:
    return db.query(PhotoFilter.user_id).filter_by(id=filter_id).one()[0]


async def get_filter_preset_by_id(filter_id: int, db: Session) -> Optional[TransformationModel]:
    return db.query(PhotoFilter.preset).filter_by(id=filter_id).one()[0]


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
        await advanced_rights_check("photo_filters", filter_id, user_id,
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
        await advanced_rights_check("photo_filters", filter_id, user_id,
                                    user_role, advanced_roles_delete, db)
        db.query(PhotoFilter).filter_by(id=filter_id).delete(synchronize_session="fetch")
        db.commit()
        return ph_filter.id
