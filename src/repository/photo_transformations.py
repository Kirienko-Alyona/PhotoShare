from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import PhotoTransformation, Photo, Role
from src.repository.functions import advanced_rights_check
from src.repository.photo_filters import get_filter_preset_by_id
from src.schemas.photo_transformations import PhotoTransformationModel, NewDescTransformationModel, TransformationModel
from src.services.photo_transformations import build_transformed_url

advanced_roles_create = []
advanced_roles_update = [Role.admin]
advanced_roles_delete = [Role.admin]


async def get_transformation_by_id(trans_id, db: Session) -> PhotoTransformation:
    return db.query(PhotoTransformation).get(trans_id)


async def get_photo_user_id(photo_id: int, db: Session) -> int:  # waiting_for_realization_from_Mykola
    return db.query(Photo.user_id).filter_by(id=photo_id).one()[0]


async def get_photo_public_id(photo_id: int, db: Session) -> str:  # waiting_for_realization_from_Mykola
    return db.query(Photo.cloud_public_id).filter_by(id=photo_id).one()[0]


async def create_transformation_from_preset(filter_id: int, photo_id: int, description: NewDescTransformationModel,
                                            user_id: int,
                                            user_role: Role, db: Session) -> Optional[PhotoTransformation]:
    await advanced_rights_check("photos", photo_id, user_id, user_role, advanced_roles_create, db)

    transformation = TransformationModel(preset=await get_filter_preset_by_id(filter_id, db))

    public_id = await get_photo_public_id(photo_id, db)
    new_transformation = PhotoTransformation()
    new_transformation.photo_id = photo_id
    new_transformation.transformed_url = build_transformed_url(public_id, transformation)
    new_transformation.description = description.description

    db.add(new_transformation)
    db.commit()
    db.refresh(new_transformation)

    return new_transformation


async def create_transformation(data: PhotoTransformationModel, user_id: int,
                                user_role: Role, db: Session) -> Optional[PhotoTransformation]:
    await advanced_rights_check("photos", data.photo_id, user_id, user_role, advanced_roles_create, db)

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
        await advanced_rights_check("photos", transformation.photo_id, user_id, user_role,
                                    advanced_roles_update, db)
        count = db.query(PhotoTransformation).filter_by(id=trans_id).update(
            {'description': data.description}, synchronize_session="fetch")
        db.commit()
        if count == 1:
            return transformation


async def remove_transformation(trans_id: int, user_id: int, user_role: Role, db: Session) -> Optional[int]:
    transformation = await get_transformation_by_id(trans_id, db)
    if transformation:
        await advanced_rights_check("photos", transformation.photo_id, user_id, user_role,
                                    advanced_roles_delete, db)
        db.query(PhotoTransformation).filter_by(id=trans_id).delete(synchronize_session="fetch")
        db.commit()
        return transformation.id
