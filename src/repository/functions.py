from typing import List

from fastapi import HTTPException, status

from sqlalchemy import text
from sqlalchemy.orm import Session

import src.conf.messages as message
from src.database.models import Role


async def get_owner_id(db_table_name: str,
                       record_id: int,
                       db: Session) -> int:
    query_str = f"SELECT user_id FROM {db_table_name} WHERE id={record_id}"
    return db.execute(text(query_str)).one()[0]


async def advanced_rights_check(db_table_name: str,
                                record_id: int,
                                cur_user_id: int,
                                cur_user_role: Role,
                                advanced_roles: List[Role],
                                db: Session):
    owner_id = await get_owner_id(db_table_name, record_id, db)
    allowed = cur_user_role in advanced_roles or owner_id == cur_user_id
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message.FORBIDDEN)
