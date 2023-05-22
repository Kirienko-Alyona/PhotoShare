from datetime import datetime

from pydantic import BaseModel, Field


class RateModel(BaseModel):
    photo_id: int
    rate: int = Field(..., ge=1, le=5)

    class Config:
        orm_mode = True


class RateResponse(BaseModel):
    photo_id: int
    user_id: int
    rate: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PhotoRatingResponse(BaseModel):
    average_rate: float
    rate_count: int
