from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import tags as repository_tags
from src.schemas.tags import TagResponse, TagModel
from src.services.auth import auth_service


router = APIRouter(prefix="/tags", tags=['tags'])


@router.post("/", response_model=TagResponse, name="Create tag to photo", status_code=status.HTTP_201_CREATED)
async def create_comment(body: TagModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    tag = await repository_tags.add_tag(body, db, current_user)
    return tag
