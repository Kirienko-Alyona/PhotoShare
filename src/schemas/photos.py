from typing import List

from pydantic import BaseModel, HttpUrl, Field

# from src.schemas.tags import TagDBModel


class PhotoModel(BaseModel):
    pass


class PhotoResponse(BaseModel):
    id: int

    url_photo: HttpUrl
    description: str | None = Field(
        default=None, title="The description of the Photo", max_length=255)

    class Config:
        orm_mode = True


class PhotoUpdate(BaseModel):
    pass


class PhotoDBModel(BaseModel):
    id: int
    cloud_public_id: str
    url_photo: str
    description: str
    # tags: List[TagDBModel]

    class Config:
        orm_mode = True
