from pydantic import BaseModel, EmailStr


class RequestEmail(BaseModel):
    email: EmailStr

