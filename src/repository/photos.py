from sqlalchemy.orm import Session

from src.database.models import User, Photo, Tag


async def add_photo(url: str, description:str, db: Session):  # user: User
    '''
    The add_photo function takes a url and adds it to the database.
        Args:
            url (str): The URL of the photo to be added.
            db (Session): A connection to the database.

    :param url: str: Pass the url of the photo to be added
    :param db: Session: Pass in the database session to the function
    :param user: User: Get the user id from the database
    :return: A photo object
    :doc-author: Trelent
    '''
    photo = Photo(url_photo=url, description=description)  # user_id=user.id
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def get_photo(skip: int,
                    limit: int,
                    photo_id: int,
                    tags: list[str],
                    username: str,
                    db: Session):
    if photo_id:
        return db.query(Photo).filter(Photo.id == photo_id).first()
    if tags:
        for tag in tags:
            return db.query(Photo).filter(Photo.tags == tag).all()
    if username:
        get_user:User = db.query(User).filter(User.username == username).first()
        return db.query(Photo).filter(Photo.user_id == get_user.id).all()

    return db.query(Photo).offset(skip).limit(limit).all()
