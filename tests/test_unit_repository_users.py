import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import UserModel, UserUpdateModel


class TestUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_users(self):
        users = [User(), User(), User()]
        self.session.query().filter().limit().offset().all.return_value = users
        result = await repository_users.get_users(dict_values={"first_name": "a"}, limit=0, offset=0, db=self.session)
        self.assertIsInstance(result, list)
        self.assertEqual(result, users)

    async def test_get_user_by_id(self):
        user = User(id=1, username="test")
        self.session.query().filter().first.return_value = user
        result = await repository_users.get_user_by_id(id=user.id, db=self.session)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.username, user.username)

    async def test_get_user_by_email(self):
        user = User(id=1, email="test")
        self.session.query().filter().first.return_value = user
        result = await repository_users.get_user_by_email(email=user.email, db=self.session)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.email, user.email)

    async def test_create_user(self):
        body = UserModel(username="username", email="test@mail.com", password="123456")
        result = await repository_users.create_user(body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User(id=1)
        token = "token"
        result = await repository_users.update_token(user=user, token=token, db=self.session)
        self.assertIsNone(result)

    async def test_confirmed_email(self):
        email = "test@mail.com"
        user = User(id=1, confirmed=False)
        self.session.query().filter().first.return_value = user
        result = await repository_users.confirmed_email(email=email, db=self.session)
        self.assertIsNone(result)
        self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        email = "test@mail.com"
        url = "url"
        user = User(id=1)
        self.session.query().filter().first.return_value = user
        result = await repository_users.update_avatar(email=email, url=url, db=self.session)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.avatar, url)

    async def test_quantity_photo_by_users(self):
        user = User()
        count = 5
        self.session.query().filter().count.return_value = count
        result = await repository_users.quantity_photo_by_users(user=user, db=self.session)
        self.assertEqual(result, count)

    async def test_update_user(self):
        body = UserUpdateModel(
            first_name="first_name",
            username="username",
            birthday="2023-05-21",
            email="email",
            password="password"
        )
        user = User(id=1)
        count = 1
        self.session.query().filter().first.return_value = user
        self.session.query().filter().update.return_value = count
        result = await repository_users.update_user(body=body, user_id=user.id, user=user, db=self.session)
        self.assertEqual(result, user)

    async def test_update_user_None(self):
        body = UserUpdateModel(
            first_name="first_name",
            username="username",
            birthday="2023-05-21",
            email="email",
            password="password"
        )
        user = User(id=1)
        self.session.query().filter().first.return_value = None
        result = await repository_users.update_user(body=body, user_id=user.id, user=user, db=self.session)
        self.assertIsNone(result)

    async def test_block_token(self):
        token = "token"
        user = User(id=1, refresh_token=token)
        repository_users.auth.auth_service.verify_access_token = MagicMock()
        # repository_users.auth.auth_service.get_exp_by_access_token = MagicMock(return_value=1)
        repository_users.client_redis = AsyncMock()
        auth_service.redis_cache = AsyncMock()
        self.session.query().filter().first.return_value = user
        result = await repository_users.block_token(token=token, db=self.session)
        self.assertIsNone(user.refresh_token)
        self.assertIsNone(result)

    async def test_ban_user(self):
        user = User(id=1, refresh_token="token", active=True)
        # repository_users.client_redis = MagicMock()
        auth_service.redis_cache = AsyncMock()
        self.session.query().filter_by().first.return_value = user
        result = await repository_users.ban_user(user_id=user.id, db=self.session)
        self.assertEqual(result.id, user.id)
        self.assertFalse(user.active)
        self.assertEqual(result, user)
        self.assertIsNone(user.refresh_token)
