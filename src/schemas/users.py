from datetime import datetime, date
import re

from pydantic import BaseModel, Field, EmailStr, EmailError, validator

from src.database.models import Role
from src.conf.constants import EMAIL_MAX__LEN, EMAIL_MIN_LEN, USERNAME_MIN_LEN, USERNAME_MAX_LEN, PASSWORD_MIN_LEN, PASSWORD_MAX_LEN, FIRST_NAME_MIN_LEN, FIRST_NAME_MAX_LEN

class UserModel(BaseModel):
    first_name: str = Field(min_length=FIRST_NAME_MIN_LEN, max_length=FIRST_NAME_MAX_LEN,) #'Jay'
    username: str = Field(..., min_length=USERNAME_MIN_LEN, max_length=USERNAME_MAX_LEN-1) #'@jay_b'
    email: str = Field(..., min_length=EMAIL_MIN_LEN, max_length=EMAIL_MAX__LEN) #'jay_b@example.com'
    password: str = Field(min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)
    birthday: date #'2023-03-29'
    
    @validator("username")
    def validate_username(cls, username: str):
        try:
            if re.search(r"^[a-zA-Z0-9 _]+$", username):
                return '@' + username.strip().lower().title().replace(' ', '_')
            else:
                raise ValueError()
        except ValueError:
            raise ValueError(f"\"{username}\" - is not a valid username")
    class Config:
        schema_extra = {
            "example": {
                "username": "ben_345"
            }
        }
        
    @validator("email")
    def check_email_value(cls, email_str):
        try:
            return EmailStr().validate(email_str)
        except EmailError:
            raise ValueError(f"\"{email_str}\" - is not a valid email address")

    class Config:
        schema_extra = {
            "example": {
                "email": "example@example.ua"
            }
        }    
        
        
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
