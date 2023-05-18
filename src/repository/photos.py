import base64
import io
from typing import Optional, List

import qrcode as qrcode
from sqlalchemy.orm import Session

from src.database.models import User, Photo, Tag
from src.repository import tags as repository_tags
from src.schemas.tags import TagModel


async def add_photo(url: str,
                    public_id: str,
                    description: str,
                    tags: List,
                    db: Session,
                    user: User):
    tags_ = await repository_tags.add_tags(tags, db, user)
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


async def get_photos(tag_name: str,
                    offset: int,
                    limit: int,
                    db: Session) -> Optional[List[Photo]]:
    tags_list = await repository_tags.get_tags(tag_name, limit, offset, db) 
    for i in range(len(tags_list)):
        
     
        # if value is not None:
        #     attr = getattr(Tag, key)
        #     photos = photos.filter(attr.contains(value))
        
    # photos = photos.offset(offset).limit(limit).all()
    return photos


async def get_photo_by_id(photo_id: int, db: Session, user: User):
    return db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).first()


# operational function for Vadym and Yuriy
async def get_photo_by_id_oper(photo_id: int, db: Session):
    return db.query(Photo).filter(Photo.id == photo_id).first()


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


async def update_tags(photo_id: int,
                      tags: TagModel,
                      db: Session,
                      user: User):
    photo = db.query(Photo).filter_by(id=photo_id, user_id=user.id).first()
    if not photo:
        return None
    tags_ = await repository_tags.update_tags(tags.tags, db, user)
    photo.tags = tags_
    db.commit()
    db.refresh(photo)
    return photo


async def untach_tag(photo_id: int,
                     tag_name: str,
                     db: Session,
                     user: User):
    photo = db. query(Photo).filter_by(id=photo_id, user_id=user.id).first()
    if not photo:
        return None
    tags = photo.tags
    [photo.tags.remove(tag_) for tag_ in tags if tag_name in tag_.tag_name]
    db.commit()
    db.refresh(photo)
    return photo
