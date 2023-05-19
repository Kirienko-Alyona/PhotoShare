from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, HttpUrl

from src.conf.constants import MAX_LENGTH_PHOTO_DESCRIPTION


class NewDescTransformationModel(BaseModel):
    description: str  # Field(max_length=BASE_DESCRIPTION_LEN)


class TransformationModel(BaseModel):
    preset: List[Dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "preset": [
                    {"gravity": "face", "height": 400, "width": 400, "crop": "crop"},
                    {"radius": "max"},
                    {"width": 200, "crop": "scale"},
                    {"fetch_format": "auto"}
                ]
            }
        }


class PhotoTransformationModel(BaseModel):
    photo_id: int
    description: Optional[str] = Field(max_length=MAX_LENGTH_PHOTO_DESCRIPTION)
    transformation: TransformationModel

    class Config:
        schema_extra = {
            "example": {
                "photo_id": 1,
                "description": "Photo with cool effect",
                "transformation": {
                    "preset": [
                        {"gravity": "face", "height": 400, "width": 400, "crop": "crop"},
                        {"radius": "max"},
                        {"width": 200, "crop": "scale"},
                        {"fetch_format": "auto"}
                    ]
                }
            }
        }


class PhotoTransformationModelDb(BaseModel):
    id: int
    photo_id: int
    transformed_url: HttpUrl
    description: Optional[str] = None

    class Config:
        orm_mode = True
