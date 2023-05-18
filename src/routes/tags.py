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
allowed_get_tags = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_remove_tag = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=List[TagResponse],
            dependencies=[Depends(allowed_get_tags)],
            status_code=status.HTTP_200_OK)
async def get_tags(db: Session = Depends(get_db)):
    tags = await repository_tags.get_tags(db)
    if tags:
        return tags
    raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAGS_NOT_FOUND)


@router.delete("/{tag_id}", dependencies=[Depends(allowed_remove_tag)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    count = await repository_tags.delete_tag(tag_id, db)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND)
