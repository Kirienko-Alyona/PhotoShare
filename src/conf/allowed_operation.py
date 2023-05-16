from src.database.models import Role
from src.services.roles import RoleAccess

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_delete = RoleAccess([Role.admin, Role.moderator, Role.user])
