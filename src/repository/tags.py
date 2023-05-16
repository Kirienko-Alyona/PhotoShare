from typing import Type

from sqlalchemy.orm import Session

from src.database.models import Tag, User, Photo
from src.schemas.tags import TagModel


async def add_tags(body: TagModel, db: Session, user: User) -> Type[Photo] | None:
    photo = db.query(Photo).filter_by(id=body.photo_id, user_id=user.id).first()
    if not photo:
        return
    elif len(photo.tags) > 4:
        return photo
    for tag_name in body.tags:
        tag = db.query(Tag).filter_by(tag_name=tag_name).first()
        if tag:
            tag.photos.append(photo)
        else:
            tag = Tag(tag_name=tag_name, photos=[photo], user_id=user.id)
        db.add(tag)
    db.commit()
    db.refresh(photo)
    return photo
