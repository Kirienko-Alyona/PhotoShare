from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Field

from src.schemas.tags import TagResponse


class PhotoModel(BaseModel):
    pass


class PhotoResponse(BaseModel):
    id: int

    url_photo: HttpUrl
    description: str | None = Field(
        default=None, title="The description of the Photo", max_length=255)
    tags: Optional[List[TagResponse]]

    class Config:
        orm_mode = True


class PhotoUpdate(BaseModel):
    pass
