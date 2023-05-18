from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

import src.conf.constants as c


class PhotoFilterModel(BaseModel):
    name: str = Field(min_lenght=c.MIN_LEN_PHOTO_FILTER_NAME, max_length=c.MAX_LEN_PHOTO_FILTER_NAME)
    description: Optional[str] = Field(max_length=c.MAX_LEN_PHOTO_FILTER_DESC)
    preset: List[Dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "name": "Avatar",
                "description": "Photo transformation preset for avatars",
                "preset": [
                    {"gravity": "face", "height": 400, "width": 400, "crop": "crop"},
                    {"radius": "max"},
                    {"width": 200, "crop": "scale"},
                    {"fetch_format": "auto"}
                ]
            }
        }


class PhotoFilterDbModel(BaseModel):
    id: int
    name: str
    description: Optional[str] = Field(max_length=c.MAX_LENGTH_PHOTO_DESCRIPTION)
    preset: List[Dict[str, Any]]

    class Config:
        orm_mode = True
