from sqlalchemy.orm import Session

from src.database.models import User, Photo


async def add_photo(url: str, db: Session, user: User):
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
    photo = Photo(url_photo=url, user_id=user.id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo