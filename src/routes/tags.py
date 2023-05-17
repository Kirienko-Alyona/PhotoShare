from fastapi import Depends, status, APIRouter, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import tags as repository_tags
from src.services.roles import RoleAccess
from src.conf import messages


router = APIRouter(prefix="/tags", tags=['tags'])
allowed_remove_tag = RoleAccess([Role.admin, Role.moderator])


@router.delete("/{tag_id}", dependencies=[Depends(allowed_remove_tag)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    count = await repository_tags.delete_tag(tag_id, db)
    if not count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND)
