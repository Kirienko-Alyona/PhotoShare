from datetime import datetime, date
from typing import List
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Query, Path

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas.users import UserDb, UserResponse
from src.services.photos import upload_photo
from src.conf import messages


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserDb])
async def read_users(first_name: str = None, 
                     username: str = None, 
                     email: str = None, 
                     created_at: datetime = None, 
                     updated_at: datetime = None, 
                     avatar: str = None, 
                     roles: Role = None, 
                     birthday: date = None,
                     confirmed: bool = None,
                     active: bool = None, 
                     limit: int = Query(default=10, ge=1, le=50), 
                     offset: int = 0, 
                     db: Session = Depends(get_db), 
                     _: User = Depends(auth_service.get_current_user)):
    
    users = await repository_users.get_users({'first_name': first_name, 
                                              'username': username, 
                                              'email': email, 
                                              'created_at': created_at, 
                                              'updated_at': updated_at, 
                                              'avatar': avatar, 
                                              'roles': roles, 
                                              'birthday': birthday,
                                              'confirmed': confirmed,
                                              'active': active
                                              }, 
                                             limit, 
                                             offset, 
                                             db)
    if len(users) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return users


@router.get("/{user_id}", response_model=UserDb)
async def read_user_by_id(user_id: int = Path(ge=1), 
                     db: Session = Depends(get_db), 
                     _: User = Depends(auth_service.get_current_user)):
    
    user = await repository_users.get_user_by_id(user_id, db)
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return user


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
