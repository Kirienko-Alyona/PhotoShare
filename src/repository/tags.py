from typing import Type, List

from sqlalchemy.orm import Session

from src.database.models import Tag, User, Photo
from src.schemas.tags import TagModel


def handler_tags(tags: List):
    tags_ = tags[0].split(",")
    return tags_ if tags_[0] else []


async def add_tags(tags: List, db: Session, user: User) -> List[Tag]:
    tags_ = []
    tags = handler_tags(tags)
    for i, tag_name in enumerate(tags):
        if i < 5:
            tag = db.query(Tag).filter_by(tag_name=tag_name).first()
            tags_.append(tag if tag else Tag(tag_name=tag_name, user_id=user.id))
        else:
            break
    return tags_


async def update_tags(body: TagModel, db: Session, user: User) -> Type[Photo] | None:
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


async def delete_tag(tag_id: int, db: Session):
    count = db.query(Tag).filter_by(id=tag_id).delete()
    db.commit()
    return count
