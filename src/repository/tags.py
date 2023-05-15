from sqlalchemy.orm import Session

from src.database.models import Tag, User, Photo

from src.schemas.tags import TagModel


async def add_tag(body: TagModel, db: Session, user: User):
    photos = db.query(Photo).filter_by(id=body.photo_id, user_id=user.id).all()
    tag = Tag(tag_name=body.tag_name, photos=photos, user_id=user.id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
