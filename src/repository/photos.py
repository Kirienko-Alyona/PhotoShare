from typing import Optional, List

from sqlalchemy.orm import Session

from src.database.models import User, Photo, Tag


async def add_photo(url: str, description: str, db: Session, user: User):

    photo = Photo(url_photo=url, description=description, user_id=user.id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def get_photos(dict_values: dict,
                    skip: int,
                    limit: int,
                    db: Session) -> Optional[List[Photo]]:
    photos = db.query(Photo)
    for key, value in dict_values.items():
        if value is not None:
            attr = getattr(Photo, key)
            photos = photos.filter(attr.icontains(value))
    photos = photos.offset(skip).limit(limit).all()
    return photos


async def get_photo_by_id(photo_id: int, db: Session, user: User):
    return db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).first()


async def description_update(new_description: str,
                             photo_id: int,
                             db: Session,
                             user: User):
    #photo = await get_photo_by_id(photo_id, db, user)
    #if photo:
    count = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).update({
            'description': new_description
        })
    if count == 1:
        db.commit()
        #return photo
    return None


async def delete_photo(photo_id: int,
                       db: Session,
                       user: User):
    photo = await get_photo_by_id(photo_id, db, user)
    if photo:
        count = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user.id).delete()
        db.commit()
        if count == 1:
            return photo
    return None
