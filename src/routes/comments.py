from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.conf import messages
from src.repository import comments as repository_comments
from src.schemas.comments import CommentResponse, CommentModel, CommentUpdateModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/comments", tags=['comments'])

allowed_operation_remove = RoleAccess([Role.admin, Role.moderator])


@router.post("/", response_model=CommentResponse, name="Create comment to photo", status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.add_comment(body, db, current_user)
    return comment


@router.get("/{comment_id}", response_model=CommentResponse, name="Return comment by id")
async def get_comment(comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                      _: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return comment


@router.put("/{comment_id}", name="Update comment by id", response_model=CommentResponse)
async def update_comment(body: CommentUpdateModel, comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    if comment.user != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
    comment = await repository_comments.update_comment(body, comment_id, db)
    return comment


@router.delete("/{comment_id}", name="Delete comment by id", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_remove)])
async def remove_comment(comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                         _: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.remove_comment(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return comment


@router.get("/comments_by_photo/{photo_id}", response_model=List[CommentResponse], name="Return all comments for photo")
async def get_comments_by_photo(photo_id: int, db: Session = Depends(get_db),
                                  _: User = Depends(auth_service.get_current_user)):
    comments = await repository_comments.get_comments_by_photo(photo_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return comments
