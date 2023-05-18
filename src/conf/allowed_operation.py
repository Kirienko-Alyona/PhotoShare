from src.database.models import Role
from src.services.roles import RoleAccess

allowed_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_delete = RoleAccess([Role.admin, Role.moderator, Role.user])
