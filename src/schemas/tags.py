from typing import List

from pydantic import BaseModel, Field


class TagModel(BaseModel):
    tags: List = Field(max_items=5)


class TagResponse(BaseModel):
    id: int
    tag_name: str

    class Config:
        orm_mode = True
