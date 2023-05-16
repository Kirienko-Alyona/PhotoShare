from fastapi import FastAPI
from sqladmin import Admin, ModelView

from src.database.models import User
from src.database.db import get_db


app = FastAPI()
admin = Admin(app, get_db)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name]


admin.add_view(UserAdmin)