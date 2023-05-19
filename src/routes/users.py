from datetime import datetime, date
from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Query, Path

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import UserDb, UserUpdateModel, UserBanModel
from src.services.photos import upload_photo
from src.conf import messages
from src.services.roles import RoleAccess

router = APIRouter(prefix="/users", tags=["users"])

#CRUD
#allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user]) --> in auth
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_ban = RoleAccess([Role.admin])


allowed_read_webadmin = RoleAccess([Role.admin, Role.moderator]) #--> for admin-panel

#only for admin-panel
#---------------------------------------------------------------------------------------------
@router.get("/", name="Read Users", 
            response_model=List[UserDb], 
            dependencies=[Depends(allowed_read_webadmin)])
# accsess - admin, мoderator
async def read_users(first_name: str = None, 
                     username: str = None, 
                     email: str = None, 
                     created_at: datetime = None, 
                     updated_at: datetime = None, 
                     avatar: str = None, 
                     roles: Role = None, 
                     birthday: date = None, 
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
                                              'birthday': birthday}, 
                                             limit, 
                                             offset, 
                                             db)

    if len(users) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return users


@router.get("/{user_id}",  
            name="Read User By Id", 
            response_model=UserDb, 
            dependencies=[Depends(allowed_read_webadmin)])
# accsess - admin, мoderator
async def read_user_by_id(user_id: int = Path(ge=1), 
                     db: Session = Depends(get_db), 
                     _: User = Depends(auth_service.get_current_user)):
    
    user = await repository_users.get_user_by_id(user_id, db)
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return user
#---------------------------------------------------------------------------------------------


@router.get("/me/", 
            name="Read User Me",
            response_model=UserDb, 
            dependencies=[Depends(allowed_read)])
# accsess -  admin, мoderator, user
async def read_user_me(current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    quantity_photos = await repository_users.quantity_photo_by_users(current_user, db)
    if quantity_photos:
        return {'id': current_user.id,
                'first_name': current_user.first_name,
                'username': current_user.username,
                'email': current_user.email,
                'created_at': current_user.created_at,
                'updated_at': current_user.updated_at,
                'avatar': current_user.avatar,
                'roles': current_user.roles,
                'birthday': current_user.birthday,
                'quantity_photos': quantity_photos}
    return current_user


@router.put('/{user_id}', 
            name="Edit User",
            response_model=UserDb, 
            dependencies=[Depends(allowed_update)])
# accsess - only for admin, moderators and  user-owner
async def user_edit(body: UserUpdateModel,
                    user_id: int,
                    current_user: User = Depends(auth_service.get_current_user),
                    db: Session = Depends(get_db)):
    user = await repository_users.update_user(body, user_id, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return user


@router.patch('/avatar', 
              name="Update Avatar User",
              response_model=UserDb, 
              dependencies=[Depends(allowed_update)])
# accsess - only for admin, moderators and  user-owner
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
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return user


@router.patch("/ban/{user_id}", 
              name="Ban User",
              response_model=UserBanModel, 
              dependencies=[Depends(allowed_ban)], 
              status_code=status.HTTP_202_ACCEPTED)
async def ban_user(user_id: int, db: Session = Depends(get_db)):
    user = await repository_users.ban_user(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
    return user
