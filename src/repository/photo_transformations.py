from typing import Optional, Type, List

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

import src.conf.messages as message
from src.database.models import PhotoTransformation, Photo, Role
from src.repository.photo_filters import get_filter_preset_by_id, create_photo_filter
from src.schemas.photo_filters import PhotoFilterModel
from src.schemas.photo_transformations import (
    PhotoTransformationModel, NewDescTransformationModel, TransformationModel)
from src.services.photo_transformations import build_transformed_url

advanced_roles_create = []
advanced_roles_read = []
advanced_roles_update = [Role.admin]
advanced_roles_delete = [Role.admin]


async def get_transformation_by_id(trans_id, db: Session) -> Optional[PhotoTransformation]:
    return db.get(PhotoTransformation, trans_id)


async def get_photo_user_id(photo_id: int, db: Session) -> int:  # waiting_for_realization_from_Mykola
    return db.query(Photo.user_id).filter_by(id=photo_id).one()[0]


async def get_photo_public_id(photo_id: int, db: Session) -> str:  # waiting_for_realization_from_Mykola
    return db.query(Photo.cloud_public_id).filter_by(id=photo_id).one()[0]


async def advanced_rights_check(photo_id: int,
                                cur_user_id: int,
                                cur_user_role: Role,
                                advanced_roles: List[Role],
                                db: Session):
    owner_id = await get_photo_user_id(photo_id, db)
    allowed = cur_user_role in advanced_roles or owner_id == cur_user_id
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message.FORBIDDEN)


async def get_transformed_photos(photo_id: int, user_id: int, user_role: Role,
                                 db: Session) -> list[Type[PhotoTransformation]]:
    await advanced_rights_check(photo_id, user_id, user_role, advanced_roles_create, db)
    return db.query(PhotoTransformation).filter_by(photo_id=photo_id).order_by(PhotoTransformation.description).all()


async def create_transformation_from_preset(filter_id: int, photo_id: int, description: NewDescTransformationModel,
                                            user_id: int,
                                            user_role: Role, db: Session) -> Optional[PhotoTransformation]:
    await advanced_rights_check(photo_id, user_id, user_role, advanced_roles_create, db)

    transformation = TransformationModel(preset=await get_filter_preset_by_id(filter_id, db))

    public_id = await get_photo_public_id(photo_id, db)
    new_transformation = PhotoTransformation()
    new_transformation.photo_id = photo_id
    new_transformation.transformed_url = build_transformed_url(public_id, transformation)
    if description is not None:
        new_transformation.description = description.description

    db.add(new_transformation)
    db.commit()
    db.refresh(new_transformation)

    return new_transformation


async def create_transformation(data: PhotoTransformationModel,
                                save_filter: bool,
                                filter_name: Optional[str],
                                filter_description: Optional[str],
                                user_id: int,
                                user_role: Role, db: Session) -> Optional[PhotoTransformation]:
    await advanced_rights_check(data.photo_id, user_id, user_role, advanced_roles_create, db)

    if save_filter:
        if not filter_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message.BAD_REQUEST)
        ph_filter = PhotoFilterModel(name=filter_name, description=filter_description,
                                     preset=data.transformation.preset)
        await create_photo_filter(ph_filter, user_id, db)

    public_id = await get_photo_public_id(data.photo_id, db)
    new_transformation = PhotoTransformation()
    new_transformation.photo_id = data.photo_id
    new_transformation.transformed_url = build_transformed_url(public_id, data.transformation)
    new_transformation.description = data.description

    db.add(new_transformation)
    db.commit()
    db.refresh(new_transformation)

    return new_transformation


async def change_description(trans_id: int, data: NewDescTransformationModel,
                             user_id: int, user_role: Role, db: Session) -> Optional[PhotoTransformation]:
    transformation = await get_transformation_by_id(trans_id, db)
    if transformation:
        await advanced_rights_check(transformation.photo_id, user_id, user_role,
                                    advanced_roles_update, db)
        count = db.query(PhotoTransformation).filter_by(id=trans_id).update(
            {'description': data.description}, synchronize_session="fetch")
        db.commit()
        if count == 1:
            return transformation


async def remove_transformation(trans_id: int, user_id: int, user_role: Role, db: Session) -> Optional[int]:
    transformation = await get_transformation_by_id(trans_id, db)
    if transformation:
        await advanced_rights_check(transformation.photo_id, user_id, user_role,
                                    advanced_roles_delete, db)
        db.query(PhotoTransformation).filter_by(id=trans_id).delete(synchronize_session="fetch")
        db.commit()
        return transformation.id
