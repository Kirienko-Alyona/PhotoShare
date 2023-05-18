from typing import Type, List

from sqlalchemy.orm import Session

from src.database.models import Tag, User


async def get_tags(dict_values: dict, limit: int, offset: int, db: Session) -> List[Type[Tag]]:
    # if not input params - returned all list tags
    # else - search by parametrs: id, tag_name, user.id - returned list tags
    tags = db.query(Tag)
    for key, value in dict_values.items():
        if value != None:
            attr = getattr(Tag, key)
            tags = tags.filter(attr.contains(value))
    tags = tags.limit(limit).offset(offset).all()
    return tags


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


async def update_tags(tags: List, db: Session, user: User) -> List[Tag]:
    tags_ = []
    for tag_name in tags:
        tag = db.query(Tag).filter_by(tag_name=tag_name).first()
        tags_.append(tag if tag else Tag(tag_name=tag_name, user_id=user.id))
    return tags_


async def delete_tag(tag_id: int, db: Session):
    count = db.query(Tag).filter_by(id=tag_id).delete()
    db.commit()
    return count
