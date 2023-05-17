from typing import Type, List

from sqlalchemy.orm import Session

from src.database.models import Tag, User, Photo
from src.schemas.tags import TagModel


async def add_tags(body: TagModel, db: Session, user: User) -> Type[Photo] | None:
    photo = db.query(Photo).filter_by(id=body.photo_id).first()
    if not photo:
        return None
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


async def add_tags_(tags: List, db: Session, user: User) -> List[Tag]:
    tags_ = []
    for i, tag_name in enumerate(tags):
        if i < 5:
            tag = db.query(Tag).filter_by(tag_name=tag_name).first()
            if tag:
                tags_.append(tag)
            else:
                tags_.append(Tag(tag_name=tag_name, user_id=user.id))
        else:
            break
    return tags_




async def delete_tag(tag_id: int, db: Session):
    count = db.query(Tag).filter_by(id=tag_id).delete()
    db.commit()
    return count
