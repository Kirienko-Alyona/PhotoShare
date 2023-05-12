from datetime import datetime, date

from pydantic import BaseModel, Field, EmailStr

from src.database.models import Role


class UserModel(BaseModel):
    first_name: str = Field(min_length=3, max_length=20) #'Jay'
    username: str = Field(min_length=5, max_length=30) #'@jay_b'
    email: EmailStr(min_length=5, max_length=50) #'jay_b@example.com'
    password: str = Field(min_length=6, max_length=10)
    birthday: date = Field #'2023-03-29'
    

class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str = None
    roles: Role

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
