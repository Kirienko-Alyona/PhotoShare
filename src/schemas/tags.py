from typing import List

from pydantic import BaseModel, Field


class TagModel(BaseModel):
    tags: str


class TagResponse(BaseModel):
    id: int
    tag_name: str

    class Config:
        orm_mode = True
