from typing import Optional

from pydantic import BaseModel


class PhotoResponse(BaseModel):
    id: int
    url_photo: str
    # description: Optional[str]

    class Config:
        orm_mode = True