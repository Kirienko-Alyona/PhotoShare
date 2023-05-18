import re
from typing import Type, List

from sqlalchemy.orm import Session

from src.database.models import Tag, User


async def get_tags(db: Session) -> List[Type[Tag]]:
    return db.query(Tag).all()


def handler_tags(tags: str):
    tags_list = re.search(r'\w+', tags)
    return tags_list if tags_list else []


# async def add_tags(tags: List, db: Session, user: User) -> List[Tag]:
#     tags_ = []
#     tags = handler_tags(tags)
#     for i, tag_name in enumerate(tags):
#         if i < 5:
#             tag = db.query(Tag).filter_by(tag_name=tag_name).first()
#             tags_.append(tag if tag else Tag(tag_name=tag_name, user_id=user.id))
#         else:
#             break
#     return tags_

async def add_tags(tags: str, db: Session, user: User) -> List[Tag]:
    tags_list = []
    tags = handler_tags(tags)
    for i, tag_name in enumerate(tags):
        if i < 5:
            tag = db.query(Tag).filter_by(tag_name=tag_name).first()
            tags_list.append(tag if tag else Tag(tag_name=tag_name, user_id=user.id))
        else:
            break
    return tags_list


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
