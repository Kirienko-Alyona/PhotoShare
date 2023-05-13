from pydantic import BaseModel, HttpUrl, Field


class PhotoModel(BaseModel):
    pass


class PhotoResponse(BaseModel):
    id: int
    url_photo: HttpUrl
    description: str | None = Field(
        default=None, title="The description of the Photo", max_length=300
    )

    class Config:
        orm_mode = True


class PhotoUpdate(BaseModel):
    pass
