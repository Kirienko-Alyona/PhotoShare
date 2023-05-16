from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.conf import messages
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        user_id = request.query_params.get('user_id', None)
        if user_id:
            user_id = int(user_id)
            if current_user.id != user_id and current_user.roles not in self.allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
        else:
            if current_user.roles not in self.allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.FORBIDDEN)
