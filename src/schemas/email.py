from pydantic import BaseModel, EmailError, EmailStr, Field, validator, ValidationError

from src.conf.logger import get_logger

logger = get_logger(__name__)

MAX_EMAIL_STR_LEN = 20  # 150


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


if __name__ == '__main__':
    try:
        email = RequestEmail(email='w@w.ua')
        print(email.email)

        email = RequestEmail(email='123456werewr@gfgdfglfgjhklghjlfgjhfghfglhjfglkhjfghjgfhjfgjhfljh.com')
        print(email.email)

        email = RequestEmail(email='123456')
        print(email.email)
    except ValidationError as err:
        logger.error(err)
