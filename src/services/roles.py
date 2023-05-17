from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.conf import messages
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_operations: dict, current_operation: str):
        self.allowed_operations = allowed_operations
        self.current_operation = current_operation

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        user_role = current_user.roles
        curent_role = self.allowed_operations[user_role.value]
        if self.current_operation not in curent_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
