from typing import List

from fastapi import Depends, status, APIRouter, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import tags as repository_tags
from src.services.roles import RoleAccess
from src.conf import messages
from src.schemas.tags import TagResponse


router = APIRouter(prefix="/tags", tags=['tags'])

#CRUD
#allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user]) --> in photos
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])
#allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user]) --> in photos
allowed_delete = RoleAccess([Role.admin, Role.moderator])


@router.get("/", 
            name="Get Tags",
            response_model=List[TagResponse],
            dependencies=[Depends(allowed_read)],
            status_code=status.HTTP_200_OK)
async def get_tags(db: Session = Depends(get_db)):
    tags = await repository_tags.get_tags(db)
    if tags:
        return tags
    raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAGS_NOT_FOUND)

#-->delete the tag from DB
@router.delete("/{tag_id}", 
               name="Delete Tag From BD",
               dependencies=[Depends(allowed_delete)], 
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    count = await repository_tags.delete_tag(tag_id, db)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND)
