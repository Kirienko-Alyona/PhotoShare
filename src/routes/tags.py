from fastapi import Depends, status, APIRouter, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import tags as repository_tags
from src.schemas.tags import TagModel
from src.schemas.photos import PhotoResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf import messages


router = APIRouter(prefix="/tags", tags=['tags'])

allowed_operations = {
    'admin': ['R', 'D'],
    'moderator': ['R', 'D'],
    'user': ['C', 'R', 'U'],
}


@router.post("/", response_model=PhotoResponse, name="Create tags to photo (max 5 tags to one photo)", status_code=status.HTTP_201_CREATED, 
             dependencies=[Depends(RoleAccess(allowed_operations, "C"))])
async def create_tags(body: TagModel, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    photo = await repository_tags.add_tags(body, db, current_user)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND)
    return photo


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, 
               dependencies=[Depends(RoleAccess(allowed_operations, "D"))])
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    count = await repository_tags.delete_tag(tag_id, db)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND)
