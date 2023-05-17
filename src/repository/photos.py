import base64
import io
from typing import Optional, List

import qrcode as qrcode
from sqlalchemy.orm import Session

from src.database.models import User, Photo, Tag
from src.repository.tags import add_tags_


async def add_photo(url: str,
                    public_id: str,
                    description: str,
                    tags: List,
                    db: Session,
                    user: User):
    tags_ = []
    tags = tags[0].split(",")
    if tags[0]:
        tags_ = await add_tags_(tags, db, user)
    photo = Photo(
        url_photo=url,
        cloud_public_id=public_id,
        description=description,
        tags=tags_,
        user_id=user.id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def get_photos(dict_values: dict,
                    skip: int,
                    limit: int,
                    db: Session) -> Optional[List[Photo]]:
    photos = db.query(Photo)
    for key, value in dict_values.items():
        if value is not None:
            attr = getattr(Tag, key)
            photos = photos.filter(attr.contains(value))
    photos = photos.offset(skip).limit(limit).all()
    return photos


async def get_photo_by_id(photo_id: int, db: Session, user: User):
    return db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).first()


async def description_update(new_description: str,
                             photo_id: int,
                             db: Session,
                             user: User):
    photo = await get_photo_by_id(photo_id, db, user)
    if photo:
        count = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).update({
            'description': new_description
        })
        db.commit()
        if count == 1:
            return photo
    return None


async def delete_photo(photo_id: int,
                       db: Session,
                       user: User):
    photo = await get_photo_by_id(photo_id, db, user)
    if photo:
        count = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).delete()
        db.commit()
        if count == 1:
            return photo
    return None


async def generate_qrcode(photo_url: str):
    img = qrcode.make(photo_url)
    buffer = io.BytesIO()
    img.save(buffer)
    return {'qrcode_encode': base64.b64encode(buffer.getvalue()).decode('utf-8')}
