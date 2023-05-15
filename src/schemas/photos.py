from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class PhotoModel(BaseModel):
    url_photo: HttpUrl


class PhotoResponse(BaseModel):
    #count: int
    #url_photo: HttpUrl
    #description: str | None = Field(default=None, title="The description of the Photo", max_length=255)
    pass
    # class Config:
    #     orm_mode = True


class PhotoUpdate(BaseModel):
    pass
