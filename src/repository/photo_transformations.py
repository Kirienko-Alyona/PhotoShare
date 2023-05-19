from typing import Optional

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

import src.conf.messages as message
from src.database.models import PhotoTransformation, Photo, Role
from src.schemas.photo_transformations import PhotoTransformationModel, NewDescTransformationModel
from src.services.photo_transformations import build_transformed_url


async def get_photo_by_id_1(photo_id: int, db: Session):
    return db.query(Photo).get(photo_id)


async def get_transformation_by_id(trans_id, db: Session) -> PhotoTransformation:
    return db.query(PhotoTransformation).get(trans_id)


async def get_photo_user_id(photo_id: int, db: Session) -> int:  # waiting_for_realization_from_Mykola
    return db.query(Photo.user_id).filter_by(id=photo_id).one()[0]


# async def get_photo_user_id_by_trans_id(trans_id: int, db: Session) -> int:
#     return db.query(Photo.user_id).select_from(PhotoTransformation).join(Photo).filter_by(trans_id=trans_id).one()[0]


async def get_photo_public_id(photo_id: int, db: Session) -> str:  # waiting_for_realization_from_Mykola
    return db.query(Photo.cloud_public_id).filter_by(id=photo_id).one()[0]


async def additional_rights_check(photo_id: int, cur_user_id: int,
                                  cur_user_role: Role, db: Session, private=False):
    photo_user_id = await get_photo_user_id(photo_id, db)
    allowed = photo_user_id == cur_user_id if private else (cur_user_role == Role.admin or
                                                            photo_user_id == cur_user_id)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message.FORBIDDEN)


async def create_transformation(data: PhotoTransformationModel, user_id: int,
                                user_role: Role, db: Session) -> Optional[PhotoTransformation]:
    await additional_rights_check(data.photo_id, user_id, user_role, db, private=True)

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
        await additional_rights_check(transformation.photo_id, user_id, user_role, db)
        count = db.query(PhotoTransformation).filter_by(id=trans_id).update(
            {'description': data.description}, synchronize_session="fetch")
        db.commit()
        if count == 1:
            return transformation


async def remove_transformation(trans_id: int, user_id: int, user_role: Role, db: Session) -> Optional[int]:
    transformation = await get_transformation_by_id(trans_id, db)
    if transformation:
        await additional_rights_check(transformation.photo_id, user_id, user_role, db)
        db.query(PhotoTransformation).filter_by(id=trans_id).delete(synchronize_session="fetch")
        db.commit()
        return transformation.id
