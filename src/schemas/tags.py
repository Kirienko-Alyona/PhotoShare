from typing import List

from pydantic import BaseModel, Field

from src.schemas.photos import PhotoResponse
from src.conf.constants import TAG_MIN_LEN


class TagModel(BaseModel):
    tag_name: str = Field(min_length=TAG_MIN_LEN)
    photo_id: int


class TagDBModel(BaseModel):
    id: int
    tag_name: str
    user_id: int
    # photos: List[PhotoResponse]

    class Config:
        orm_mode = True


class TagResponse(BaseModel):
    id: int
    tag_name: str
    user_id: int
    # photos: List[PhotoResponse]

    class Config:
        orm_mode = True
