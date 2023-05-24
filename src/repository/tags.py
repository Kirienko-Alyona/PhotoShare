from fastapi import status, HTTPException
from typing import Type, List

from sqlalchemy.orm import Session

from src.database.models import Tag, User
from src.conf import messages
from src.repository import photos as repository_photos


async def get_tags(db: Session) -> List[Type[Tag]]:
    return db.query(Tag).all()


def handler_tags(tags: str) -> List[Type[Tag]]:
    tags_list = tags.lower().replace(r", ", " ").replace(r",", " ").strip().split(" ")
    for i in range(len(tags_list)):
        if not tags_list[i].startswith("#"):
            tags_list[i] = '#' + tags_list[i]
    unique_tags_list = list(set(tags_list))        
    return unique_tags_list if unique_tags_list else []


async def get_tag_name(tag_name: str, db: Session):
    tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
    # attr = getattr(Tag, 'tag_name')
    # tag = db.query(Tag).filter(attr.contains(tag_name)).first()
    return tag
    
    
async def add_tag(tag_name: str, user_id, db: Session):
    tag = Tag(tag_name=tag_name, user_id=user_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def add_tags_for_photo(tags: str, db: Session, user: User) -> List[Tag]:
    tags_list = []
    if tags is None:
        tags_ = []
    else:    
        tags_ = handler_tags(tags)
    if len(tags_) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TOO_MANY_TAGS)
    
    for tag_name in tags_:
        tag = await get_tag_name(tag_name, db)
        if tag == None:
            tag = await add_tag(tag_name, user.id, db)
        tags_list.append(tag)  
        
    return tags_list


async def update_tags(new_tags: str, photo_id, db: Session, user: User) -> List[Tag]:
    new_tag_list = []
    photo = await repository_photos.get_photo_by_id(photo_id, db, user)
    old_tag_list = photo.tags
    if len(old_tag_list) < 5:
        new_tag_list = await add_tags_for_photo(new_tags, db, user)
        old_tag_list.extend(new_tag_list)
    if len(old_tag_list) >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.TOO_MANY_TAGS_UNDER_THE_PHOTO)
    return old_tag_list


async def delete_tag(tag_id: int, db: Session):
    count = db.query(Tag).filter_by(id=tag_id).delete()
    db.commit()
    return count
