from fastapi import status, HTTPException
from typing import Type, List

from sqlalchemy.orm import Session

from src.database.models import Tag, User
from src.conf import messages


async def get_tags(db: Session) -> List[Type[Tag]]:
    return db.query(Tag).all()


def handler_tags(tags: str) -> List[Type[Tag]]:
    tags_list = tags.lower().replace(r", ", " ").replace(r",", " ").strip().split(" ")
    for i in range(len(tags_list)):
        if not tags_list[i].startswith("#"):
            tags_list[i] = '#' + tags_list[i]

    return tags_list if tags_list else []


async def get_tag_name(tag_name: str, db: Session):
    attr = getattr(Tag, 'tag_name')
    tag = db.query(Tag).filter(attr.contains(tag_name)).first()
    return tag
    
    
async def add_tag(tag_name: str, user_id, db: Session):
    tag = Tag(tag_name=tag_name, user_id=user_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def add_tags_for_photo(tags: str, db: Session, user: User) -> List[Tag]:
    tags_list = []
    tags_ = handler_tags(tags)
    if len(tags_) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TOO_MANY_TAGS)
    
    for tag_name in tags_:
        tag = await get_tag_name(tag_name, db)
        if tag == None:
            tag = await add_tag(tag_name, user.id, db)
        tags_list.append(tag)  
        
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
