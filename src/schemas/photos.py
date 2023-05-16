from pydantic import BaseModel, HttpUrl, Field
import src.conf.constants as constants


class PhotoModel(BaseModel):
    pass


class PhotoResponse(BaseModel):
    id: int
    url_photo: HttpUrl
    description: str | None = Field(
        default=None, title="The description of the Photo", max_length=constants.MAX_LENGTH_PHOTO_DESCRIPTION)

    class Config:
        orm_mode = True


class PhotoUpdate(BaseModel):
    pass
