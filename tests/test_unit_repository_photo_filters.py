import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import PhotoFilter, Role
from src.schemas.photo_filters import PhotoFilterModel
from src.repository.photo_filters import (
    get_filter_by_id,
    get_photo_filter_user_id,
    get_filter_preset_by_id,
    advanced_rights_check,
    get_photos_filters,
    create_photo_filter,
    update_photo_filter,
    remove_photo_filter
)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    photo_filter = None
    photo_filters = None
    advanced_roles_create = None
    advanced_roles_update = None
    advanced_roles_delete = None
    photo_preset = None
    body = None

    @classmethod
    def setUpClass(cls):
        cls.photo_filter = PhotoFilter(id=1, name="Avatar1", user_id=1)
        cls.photo_filters = [PhotoFilter(id=1, name="Avatar1", user_id=1),
                             PhotoFilter(id=2, name="Avatar2", user_id=2),
                             PhotoFilter(id=3, name="Avatar3", user_id=3)]

        cls.advanced_roles_create = []
        cls.advanced_roles_update = [Role.admin]
        cls.advanced_roles_delete = [Role.admin]

        cls.photo_preset = [{"radius": "max"}]
        cls.body = PhotoFilterModel(
            name="Avatar",
            description="No description",
            preset=[{"radius": "max"}]
        )

    @classmethod
    def tearDownClass(cls):
        cls.photo_filter = None
        del cls.photo_filters
        del cls.advanced_roles_update
        del cls.advanced_roles_delete
        del cls.photo_preset
        cls.body = None

    def setUp(self):
        self.session = MagicMock(spec=Session)

    def tearDown(self):
        self.session = None

    async def test_get_filter_by_id_found(self):
        self.session.get.return_value = self.photo_filter
        result = await get_filter_by_id(filter_id=1, db=self.session)
        self.assertEqual(result, self.photo_filter)

    async def test_get_filter_by_id_not_found(self):
        self.session.get.return_value = None
        result = await get_filter_by_id(filter_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_get_photo_filter_user_id_found(self):
        self.session.query().filter_by().one.return_value = (100,)
        result = await get_photo_filter_user_id(filter_id=1, db=self.session)
        self.assertEqual(result, 100)

    async def test_get_photo_filter_user_id_not_found(self):
        self.session.query().filter_by().one = MagicMock(side_effect=NoResultFound)
        with self.assertRaises(NoResultFound) as context:
            await get_photo_filter_user_id(filter_id=1, db=self.session)
        self.assertTrue(context.exception)

    async def test_get_filter_preset_by_id_found(self):
        self.session.query().filter_by().one = MagicMock(return_value=self.photo_preset)
        result = await get_filter_preset_by_id(filter_id=1, db=self.session)
        self.assertEqual(result, self.photo_preset[0])

    async def test_get_filter_preset_by_id_not_found(self):
        self.session.query().filter_by().one = MagicMock(side_effect=NoResultFound)
        with self.assertRaises(NoResultFound) as context:
            await get_filter_preset_by_id(filter_id=1, db=self.session)
        self.assertTrue(context.exception)

    @patch('src.repository.photo_filters.get_photo_filter_user_id', return_value=1)
    async def test_advanced_rights_check_awaited(self, _):
        result = await advanced_rights_check(filter_id=1,
                                             cur_user_id=1,
                                             cur_user_role=Role.admin,
                                             advanced_roles=self.advanced_roles_update,
                                             db=self.session)
        self.assertIsNone(result)

    @patch('src.repository.photo_filters.get_photo_filter_user_id', return_value=2)
    async def test_advanced_rights_check_not_awaited(self, _):
        with self.assertRaises(HTTPException) as context:
            await advanced_rights_check(filter_id=1,
                                        cur_user_id=1,
                                        cur_user_role=Role.user,
                                        advanced_roles=self.advanced_roles_update,
                                        db=self.session)
        self.assertTrue(context.exception)

    async def test_get_photos_filters_found(self):
        self.session.query().filter_by().order_by().all.return_value = self.photo_filters
        result = await get_photos_filters(user_id=1, db=self.session)
        self.assertEqual(result, self.photo_filters)

    async def test_get_photos_filters_not_found(self):
        self.session.query().filter_by().order_by().all.return_value = []
        result = await get_photos_filters(user_id=1, db=self.session)
        self.assertEqual(result, [])

    async def test_create_photo_filter(self):
        result = await create_photo_filter(data=self.body, user_id=1, db=self.session)
        [self.assertEqual(result.__dict__[item],
                          self.body.__dict__[item]) for item in self.body.__dict__]
        self.assertTrue(hasattr(result, 'id'))

    @patch('src.repository.photo_filters.advanced_rights_check', return_value=None)
    async def test_update_photo_filter_found(self, _):
        self.session.get.return_value = self.photo_filter
        self.session.query().filter_by().update.return_value = 1

        result = await update_photo_filter(filter_id=1,
                                           data=self.body,
                                           user_id=1,
                                           user_role=Role.user,
                                           db=self.session)
        self.assertEqual(result.name, "Avatar1")

    @patch('src.repository.photo_filters.advanced_rights_check', return_value=None)
    async def test_update_photo_filter_not_found(self, _):
        self.session.get.return_value = None
        result = await update_photo_filter(filter_id=1,
                                           data=self.body,
                                           user_id=1,
                                           user_role=Role.user,
                                           db=self.session)
        self.assertIsNone(result)

    @patch('src.repository.photo_filters.advanced_rights_check', return_value=None)
    async def test_remove_photo_filter_found(self, _):
        self.session.get.return_value = self.photo_filter
        result = await remove_photo_filter(filter_id=1, user_id=1, user_role=Role.user, db=self.session)
        self.assertEqual(result, self.photo_filter.id)

    @patch('src.repository.photo_filters.advanced_rights_check', return_value=None)
    async def test_remove_photo_filter_not_found(self, _):
        self.session.get.return_value = None
        result = await remove_photo_filter(filter_id=1, user_id=1, user_role=Role.user, db=self.session)
        self.assertIsNone(result)
