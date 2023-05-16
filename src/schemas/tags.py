from pydantic import BaseModel, Field

from src.conf.constants import TAG_MIN_LEN


class TagModel(BaseModel):
    tag_name: str = Field(min_length=TAG_MIN_LEN)
    photo_id: int


class TagResponse(BaseModel):
    id: int
    tag_name: str

    class Config:
        orm_mode = True
