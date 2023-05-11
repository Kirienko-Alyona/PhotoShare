from pydantic import BaseModel, EmailError, EmailStr, Field, validator

from src.conf.constants import MAX_EMAIL_STR_LEN


class RequestEmail(BaseModel):
    email: str = Field(..., max_length=MAX_EMAIL_STR_LEN)

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
