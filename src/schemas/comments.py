from datetime import datetime

from pydantic import BaseModel, Field


class CommentModel(BaseModel):
    text_comment: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    text_comment: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
