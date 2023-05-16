from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas.users import UserDb
from src.services.photos import upload_photo

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):

    quantity_photos = await repository_users.quantity_photo_by_users(current_user, db)
    if quantity_photos:
        return {'id': current_user.id,
                'first_name': current_user.first_name,
                'username': current_user.username,
                'email': current_user.email,
                'created_at': current_user.created_at,
                'avatar': current_user.avatar,
                'roles': current_user.roles,
                'birthday': current_user.birthday,
                'quantity_photos': quantity_photos}
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(),
                             current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
The update_avatar_user function updates the avatar of a user.
    The function takes in an UploadFile object, which is a file that has been uploaded to the server.
    It also takes in a User object and Session object as dependencies.

:param file: UploadFile: Upload the file to cloudinary
:param current_user: User: Get the current user
:param db: Session: Access the database
:return: The updated user object
:doc-author: Trelent
"""
    url, public_id = upload_photo(file)
    user = await repository_users.update_avatar(current_user.email, url, db)
    return user
