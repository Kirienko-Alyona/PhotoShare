from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.users import UserDb


class RateModel(BaseModel):
    photo_id: int
    rate: int = Field(..., ge=1, le=5)

    class Config:
        orm_mode = True


class RateResponse(BaseModel):
    average_rate: float
    rate_count: int


class RateDetailResponse(BaseModel):
    photo_id: int
    user: UserDb
    rate: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RateDeleteModel(BaseModel):
    photo_id: int
    user_id: int

