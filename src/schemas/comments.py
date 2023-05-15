from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.users import UserDb
from src.conf.constants import COMMENT_MIN_LEN


class CommentModel(BaseModel):
    photo_id: int
    text_comment: str = Field(min_length=COMMENT_MIN_LEN)


class CommentUpdateModel(BaseModel):
    text_comment: str = Field(min_length=COMMENT_MIN_LEN)


class CommentResponse(BaseModel):
    id: int
    text_comment: str
    user: UserDb
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
