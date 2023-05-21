import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from src.database.models import User, Role
from src.conf import messages
from src.repository import users as repository_users


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_users(self):
        users = [User(), User(), User()]
        self.session.query().filter().limit().offset().all.return_value = users
        result = await repository_users.get_users(dict_values={"first_name": "a"}, limit=0, offset=0, db=self.session)
        self.assertIsInstance(result, list)
        self.assertEqual(result, users)

    async def test_get_users_by_id(self):
        user = User(id=1, username="test")
        self.session.query().filter().first.return_value = user
        result = await repository_users.get_user_by_id(id=user.id, db=self.session)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.username, user.username)

