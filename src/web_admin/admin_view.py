from sqladmin import Admin, ModelView
from src.database.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, 
                   User.first_name, 
                   User.username, 
                   User.email, 
                   User.birthday, 
                   User.avatar,
                   User.roles,
                   User.confirmed,
                   User.active,
                   User.created_at,
                   User.updated_at
                   ]