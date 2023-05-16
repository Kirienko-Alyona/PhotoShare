from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import PhotoTransformation, Photo
from src.schemas.photo_transformations import PhotoTransformationModel, NewDescTransformationModel
from src.services.photo_transformations import build_transformed_url


class RecordNotFound(Exception):
    pass


async def get_photo_by_id_1(photo_id: int, db: Session):
    return db.query(Photo).get(photo_id)


async def get_transformation_by_id(trans_id, db: Session) -> PhotoTransformation:
    return db.query(PhotoTransformation).get(trans_id)


async def create_transformation(data: PhotoTransformationModel, db: Session) -> PhotoTransformation:
    photo = await get_photo_by_id_1(data.photo_id, db)
    if photo is None:
        raise RecordNotFound(f'{data.photo_id}')

    new_transformation = PhotoTransformation()
    new_transformation.photo_id = data.photo_id
    new_transformation.transformed_url = build_transformed_url(photo.cloud_public_id, data.transformation)
    new_transformation.description = data.description

    db.add(new_transformation)
    db.commit()
    db.refresh(new_transformation)

    return new_transformation


async def change_description(trans_id: int, data: NewDescTransformationModel,
                             db: Session) -> Optional[PhotoTransformation]:
    transformation = await get_transformation_by_id(trans_id, db)
    if transformation is None:
        raise RecordNotFound(f'{trans_id}')

    transformation.description = data.description
    db.commit()
    db.refresh(transformation)

    return transformation


async def remove_transformation(trans_id: int, db: Session) -> PhotoTransformation:
    transformation = await get_transformation_by_id(trans_id, db)
    if transformation is None:
        raise RecordNotFound(f'{trans_id}')

    db.delete(transformation)
    db.commit()
    return transformation
