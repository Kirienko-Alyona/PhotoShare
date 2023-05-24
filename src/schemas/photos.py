from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Field

from src.schemas.tags import TagResponse
import src.conf.constants as constants


class PhotoModel(BaseModel):
    pass


class PhotoResponse(BaseModel):
    id: int
    url_photo: HttpUrl
    description: str | None = Field(
        default=None, title="The description of the Photo", max_length=constants.MAX_LENGTH_PHOTO_DESCRIPTION)
    tags: Optional[List[TagResponse]]
    rating: float = None

    class Config:
        orm_mode = True


class PhotoResponseRating(BaseModel):
    photos: list[PhotoResponse] | PhotoResponse
    rating: str = None

    class Config:
        orm_mode = True


class PhotoUpdate(BaseModel):
    pass


# class PhotoQRCodeResponse(BaseModel):
#     qrcode_encode: str
