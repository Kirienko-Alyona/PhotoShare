# from pydantic import BaseModel, validator

# from src.services.phone_number import format_phone_num, sanitize_phone_num


# class RequestPhoneNum(BaseModel):
#     phone_number: str

#     @validator("phone_number")
#     def validate_phone_number(cls, phone_num):
#         try:
#             return format_phone_num(sanitize_phone_num(phone_num))
#         except ValueError:
#             raise ValueError(f"\"{phone_num}\" - is not a valid phone number")

#     class Config:
#         schema_extra = {
#             "example": {
#                 "phone_number": "123456789"
#             }
#         }


# # if __name__ == '__main__':
# #     phone = RequestPhoneNum(phone_number="44 54 ")
# #     # phone = RequestPhoneNum(phone_number="44 54 2--12--45")
# #     print(phone.phone_number)
