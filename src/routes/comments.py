from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.conf import messages
from src.repository import comments as repository_comments
from src.schemas.comments import CommentResponse, CommentModel, CommentUpdateModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/comments", tags=['comments'])

# CRUD
allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator])


@router.post("/", name="Create Comment To Photo", 
             response_model=CommentResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_create)])
async def create_comment(body: CommentModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.add_comment(body, db, current_user)
    return comment


@router.get("/{comment_id}", name="Return Comment By Id", 
            response_model=CommentResponse, 
            dependencies=[Depends(allowed_read)])
async def get_comment(comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                      _: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return comment


@router.get("/", name="Return All Comments For Photo",
            response_model=List[CommentResponse],
            dependencies=[Depends(allowed_read)])
async def get_comments_by_photo(photo_id: int, db: Session = Depends(get_db),
                                _: User = Depends(auth_service.get_current_user)):
    comments = await repository_comments.get_comments_by_photo(photo_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return comments


@router.put("/{comment_id}", name="Update Comment By Id", 
            response_model=CommentResponse,
            dependencies=[Depends(allowed_update)])
async def update_comment(body: CommentUpdateModel, comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
    comment = await repository_comments.update_comment(body, comment_id, db)
    return comment


@router.delete("/{comment_id}", name="Delete Comment By Id", 
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_delete)])
async def remove_comment(comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                         _: User = Depends(auth_service.get_current_user)):
    delete_count = await repository_comments.remove_comment(comment_id, db)
    if delete_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return None
