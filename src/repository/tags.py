from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import Tag, User, Photo
from src.schemas.tags import TagModel


async def add_tag(body: TagModel, db: Session, user: User) -> Optional[Tag]:
    photo = db.query(Photo).filter_by(id=body.photo_id, user_id=user.id).first()

    if not photo:
        return

    tag = db.query(Tag).filter_by(tag_name=body.tag_name).first()

    if tag:
        tag.photos.append(photo)
    else:
        tag = Tag(tag_name=body.tag_name, photos=[photo], user_id=user.id)

    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
