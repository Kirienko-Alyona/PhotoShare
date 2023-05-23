from datetime import datetime

from sqlalchemy.orm import Session
from typing import List, Optional

#from src.database.db import client_redis
from src.database.models import User, Photo
from src.schemas.users import UserModel, UserUpdateModel
import src.services.auth as auth

async def get_users(dict_values: dict, limit: int, offset: int, db: Session) -> Optional[List[User]]:

    # if not input params - returned all list users
    # else - search by parametrs: first_name, username, email, created_at, updated_at, avatar, roles, birthday - returned list contacts
    users = db.query(User)
    for key, value in dict_values.items():
        if value != None:
            attr = getattr(User, key)
            users = users.filter(attr.contains(value))
    users = users.limit(limit).offset(offset).all()
    return users



async def get_user_by_id(id: int, db: Session) -> User:
    return db.query(User).filter(User.id == id).first()


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
The get_user_by_email function takes in an email and a database session,
and returns the user associated with that email. If no such user exists, it returns None.

:param email: str: Specify the email of the user that we want to retrieve
:param db: Session: Pass the database session to the function
:return: The first user that matches the email address, or none if no such user exists
:doc-author: Trelent
"""
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
The create_user function creates a new user in the database.

:param body: UserModel: Specify the type of data that will be passed to the function
:param db: Session: Access the database
:return: A user object
:doc-author: Trelent
"""
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
The update_token function updates the refresh token for a user.

:param user: User: Get the user's id, which is used to find the user in the database
:param token: str | None: Update the refresh_token field in the database
:param db: Session: Pass the database session to the function
:return: None
:doc-author: Trelent
"""
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
The confirmed_email function takes in an email and a database session,
and sets the confirmed field of the user with that email to True.


:param email: str: Get the email of the user who's account is being confirmed
:param db: Session: Pass the database session to the function
:return: None
:doc-author: Trelent
"""
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
The update_avatar function updates the avatar of a user.

:param email: Find the user in the database
:param url: str: Specify the type of data that is being passed in
:param db: Session: Pass the database session to the function
:return: The updated user object
:doc-author: Trelent
"""
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def quantity_photo_by_users(user: User, db: Session):
    quantity_photos = db.query(Photo).filter(Photo.user_id == user.id).count()
    return quantity_photos


async def update_user(body: UserUpdateModel, user_id: int, user: User, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        count = db.query(User).filter(User.id == user_id).update({
            'first_name': body.first_name,
            'username': body.username,
            'birthday': body.birthday,
            'email' : body.email,
            'password': auth.auth_service.get_password_hash(body.password)
        })
        db.commit()
        db.refresh(user)
        if count == 1:
            return user
    return None


async def block_token(token: str, db: Session):
    email = auth.auth_service.verify_access_token(token)
    user = await get_user_by_email(email, db)
    await update_token(user, None, db)
    #expire = auth.auth_service.get_exp_by_access_token(token)
    #timedelta = expire - int(datetime.now().timestamp())
    #await client_redis.set(f'user_token:{email}', token, timedelta)


async def ban_user(user_id: int, db: Session) -> Optional[User]:
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        user.active = False
        user.refresh_token = None
        db.commit()
        db.refresh(user)
        #await client_redis.delete(f'user:{user.email}')
    return user
