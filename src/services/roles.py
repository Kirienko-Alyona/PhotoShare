from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.conf import messages
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: dict, current_operation: str):
        self.allowed_roles = allowed_roles
        self.current_operation = current_operation

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        user_role = current_user.roles
        curent_role = self.allowed_roles[user_role.value]
        # record_user_id = request.query_params.get('record_user_id', None)
        # if record_user_id:
        #     record_user_id = int(record_user_id)
        #     if current_user.id != record_user_id and current_user.roles not in self.allowed_roles:
        #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
        # else:
        if self.current_operation not in curent_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
