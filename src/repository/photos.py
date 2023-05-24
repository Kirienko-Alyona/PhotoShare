from datetime import date
#import base64
import io
from typing import Optional, List, Tuple

from fastapi import HTTPException, Query, status
from src.conf import messages
from fastapi.responses import Response
import qrcode as qrcode
from sqlalchemy import func#, or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from src.database.models import User, Photo, Tag, Role, Rate
from src.repository import tags as repository_tags
from src.repository.tags import handler_tags
from src.schemas.photos import PhotoResponse
#from src.schemas.tags import TagModel


class PhotoFilteringOptions:
    def __init__(self, user_id: int, rate_min: float = None,
                 rate_max: float = None, created_at_min: date = None, created_at_max: date = None):
        self.user_id = user_id
        self.rate_min = rate_min
        self.rate_max = rate_max
        self.created_at_min = created_at_min
        self.created_at_max = created_at_max


async def filter_for_photo_query(photo_query: Query, filter_options: PhotoFilteringOptions) -> Query:
    if filter_options.user_id:
        photo_query = photo_query.filter(Photo.user_id == filter_options.user_id)
    if filter_options.created_at_min and filter_options.created_at_max:
        photo_query = photo_query.filter(func.DATE(Photo.created_at) >= filter_options.created_at_min).\
            filter(func.DATE(Photo.created_at) <= filter_options.created_at_max)
    if filter_options.rate_min and filter_options.rate_max:
        photo_query = photo_query.having(func.avg(Rate.rate).between(filter_options.rate_min, filter_options.rate_max))
    return photo_query


async def foto_response_create(photos: List[Tuple], db: Session) -> Optional[List[PhotoResponse]]:
    result = []
    if photos:
        for row in photos:
            ph = PhotoResponse(id=row[0], url_photo=row[1], description=row[2], rating=row[3])
            ph.tags = db.query(Tag.id, Tag.tag_name).select_from(Photo).join(Tag.photos)\
                .filter(Photo.id == row[0]).all()
            result.append(ph)
    return result


async def add_photo(url: str,
                    public_id: str,
                    description: str,
                    tags: List,
                    db: Session,
                    user: User):
    tags_list = await repository_tags.add_tags_for_photo(tags, db, user)
    photo = Photo(url_photo=url, cloud_public_id=public_id, description=description, tags=tags_list, user_id=user.id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def get_photos(user_id: int,
                     cur_user_id,
                     cur_user_role: Role,
                     tag_name: str,
                     rate_min: float,
                     rate_max: float,
                     created_at_min: date,
                     created_at_max: date,
                     limit: int, offset: int, db: Session) -> Optional[List[PhotoResponse]]:
    if user_id:
        allowed = cur_user_role in [Role.admin, Role.moderator] or user_id == cur_user_id

        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)

    filter_options = PhotoFilteringOptions(user_id, rate_min, rate_max, created_at_min, created_at_max)

    if tag_name is None:
        photos = db.query(Photo.id,
                          Photo.url_photo,
                          Photo.description,
                          func.avg(Rate.rate)) \
            .outerjoin(Rate) \
            .group_by(Photo.id, Photo.url_photo, Photo.description)
    else:
        tag_name = handler_tags(tag_name)[0]

        photos = db.query(Photo.id,
                          Photo.url_photo,
                          Photo.description,
                          func.avg(Rate.rate)) \
            .join(Tag.photos).outerjoin(Rate) \
            .filter(func.lower(Tag.tag_name) == tag_name) \
            .group_by(Photo.id, Photo.url_photo, Photo.description)

    photos = await(filter_for_photo_query(photos, filter_options))

    return await foto_response_create(photos.limit(limit).offset(offset).all(), db)


async def get_photo_by_id(photo_id: int, db: Session, user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin)):
        return photo
    return None


# operational function for backend
async def get_photo_by_id_oper(photo_id: int, db: Session):
    return db.query(Photo).filter(Photo.id == photo_id).first()


async def delete_photo(photo_id: int,
                                db: Session,
                                user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin) or (user.roles == Role.moderator)):
        db.query(Photo).filter(Photo.id == photo_id).delete()
        db.commit()
        return photo
    return None


async def generate_qrcode(photo_url: str):
    img = qrcode.make(photo_url)
    buffer = io.BytesIO()
    img.save(buffer)    
    return Response(content=buffer.getvalue(), media_type="image/png")


async def update_tags_descriptions_for_photo(photo_id: int,
                                             new_description: str,
                                             tags: str,
                                             db: Session,
                                             user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin)):
        if tags is not None:
            new_tags_list = await repository_tags.update_tags(tags, photo_id, db, user=user)
            photo.tags = new_tags_list
        if new_description is not None:
            db.query(Photo).filter(Photo.id == photo_id).update({
                'description': new_description})
        db.commit()
        db.refresh(photo)
        return photo
    return None


async def untach_tag(photo_id: int,
                     tags: str,
                     db: Session,
                     user: User):
    photo = await get_photo_by_id_oper(photo_id, db)
    if photo and ((photo.user_id == user.id) or (user.roles == Role.admin)):
        tag_list_to_del = repository_tags.handler_tags(tags)
        old_list_tags = photo.tags
        for tag_name in tag_list_to_del:
            tag = await repository_tags.get_tag_name(tag_name, db)
            if tag:
                [photo.tags.remove(tag_) for tag_ in old_list_tags if tag_name in tag_.tag_name]
                db.commit()
                db.refresh(photo)
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND)
        return photo
    return None
