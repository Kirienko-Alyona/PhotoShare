import base64
import io
from typing import Optional, List
from fastapi import HTTPException, status
from src.conf import messages

import qrcode as qrcode
from sqlalchemy.orm import Session

from src.database.models import User, Photo, Role
from src.repository import tags as repository_tags


async def add_photo(url: str,
                    public_id: str,
                    description: str,
                    tags: List,
                    db: Session,
                    user: User):
    tags_list = await repository_tags.add_tags_for_photo(tags, db, user)
    photo = Photo(url_photo=url, cloud_public_id=public_id, description=description, tags=tags_list, user_id=user.id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def get_photos_by_tag_name(tag_name: str, limit: int, offset: int, db: Session) -> Optional[List[Photo]]:
    if tag_name is not None:
        tag = await repository_tags.get_tag_name(tag_name, db)
        photo_list = tag.photos
        return photo_list
    photos = db.query(Photo).limit(limit).offset(offset).all()
    return photos


async def get_photo_by_id(photo_id: int, db: Session, user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin)):
        return photo
    return None


# operational function for backend
async def get_photo_by_id_oper(photo_id: int, db: Session):
    return db.query(Photo).filter(Photo.id == photo_id).first()


async def delete_photo(photo_id: int,
                                db: Session,
                                user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin) or (user.roles == Role.moderator)):
        db.query(Photo).filter(Photo.id == photo_id).delete()
        db.commit()
        return photo
    return None


async def generate_qrcode(photo_url: str):
    img = qrcode.make(photo_url)
    buffer = io.BytesIO()
    img.save(buffer)
    return {'qrcode_encode': base64.b64encode(buffer.getvalue()).decode('utf-8')}


async def update_tags_descriptions_for_photo(photo_id: int,
                                             new_description: str,
                                             tags: str,
                                             db: Session,
                                             user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin)):
        if tags is not None:
            new_tags_list = await repository_tags.update_tags(tags, photo_id, db, user=user)
            photo.tags = new_tags_list
        if new_description is not None:
            db.query(Photo).filter(Photo.id == photo_id).update({
                'description': new_description})
        db.commit()
        db.refresh(photo)
        return photo
    return None


async def untach_tag(photo_id: int,
                     tags: str,
                     db: Session,
                     user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin)):
        tag_list_to_del = repository_tags.handler_tags(tags)
        old_list_tags = photo.tags
        for tag_name in tag_list_to_del:
            tag = await repository_tags.get_tag_name(tag_name, db)
            if tag:
                [photo.tags.remove(tag_) for tag_ in old_list_tags if tag_name in tag_.tag_name]
                db.commit()
                db.refresh(photo)
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND)
        return photo
    return None
