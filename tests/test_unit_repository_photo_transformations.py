import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import PhotoTransformation, Role
from src.schemas.photo_transformations import PhotoTransformationModel, NewDescTransformationModel, TransformationModel

from src.repository.photo_transformations import (
    get_transformation_by_id,
    get_photo_user_id,
    get_photo_public_id,
    advanced_rights_check,
    get_transformed_photos,
    create_transformation_from_preset,
    create_transformation,
    change_description,
    remove_transformation
)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    transformation = None
    transformations = None
    transformation_model = None
    description = None
    preset = None
    advanced_roles_create = None
    advanced_roles_update = None
    advanced_roles_delete = None
    body = None

    @classmethod
    def setUpClass(cls):
        cls.transformation = PhotoTransformation()
        cls.transformations = [PhotoTransformation(), PhotoTransformation(), PhotoTransformation()]
        cls.transformation_model = TransformationModel(preset=[{"radius": "max"}])
        cls.description = NewDescTransformationModel(description='description')
        cls.preset = [{"radius": "max"}]

        cls.advanced_roles_create = []
        cls.advanced_roles_update = [Role.admin]
        cls.advanced_roles_delete = [Role.admin]

        cls.body = PhotoTransformationModel(
            photo_id=1,
            description="No description",
            transformation=cls.transformation_model  # {'preset': [{"radius": "max"}]}
        )

    @classmethod
    def tearDownClass(cls):
        cls.transformation = None
        del cls.transformations
        cls.transformation_model = None
        del cls.preset
        del cls.advanced_roles_update
        del cls.advanced_roles_delete
        cls.body = None

    def setUp(self):
        self.session = MagicMock(spec=Session)

    def tearDown(self):
        self.session = None

    async def test_get_transformation_by_id_found(self):
        self.session.get.return_value = self.transformation
        result = await get_transformation_by_id(trans_id=1, db=self.session)
        self.assertEqual(result, self.transformation)

    async def test_get_transformation_by_id_not_found(self):
        self.session.get.return_value = None
        result = await get_transformation_by_id(trans_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_get_photo_user_id_found(self):
        self.session.query().filter_by().one.return_value = (100,)
        result = await get_photo_user_id(photo_id=1, db=self.session)
        self.assertEqual(result, 100)

    async def test_get_photo_user_id_not_found(self):
        self.session.query().filter_by().one = MagicMock(side_effect=NoResultFound)
        with self.assertRaises(NoResultFound) as context:
            await get_photo_user_id(photo_id=1, db=self.session)
        self.assertTrue(context.exception)

    async def test_get_photo_public_id_found(self):
        self.session.query().filter_by().one.return_value = ('794055c8eebe4ae984841e3dfce19b80',)
        result = await get_photo_public_id(photo_id=1, db=self.session)
        self.assertEqual(result, '794055c8eebe4ae984841e3dfce19b80')

    async def test_get_photo_public_id_not_found(self):
        self.session.query().filter_by().one = MagicMock(side_effect=NoResultFound)
        with self.assertRaises(NoResultFound) as context:
            await get_photo_public_id(photo_id=1, db=self.session)
        self.assertTrue(context.exception)

    @patch('src.repository.photo_transformations.get_photo_user_id', return_value=1)
    async def test_advanced_rights_check_awaited(self, _):
        result = await advanced_rights_check(photo_id=1,
                                             cur_user_id=1,
                                             cur_user_role=Role.admin,
                                             advanced_roles=self.advanced_roles_update,
                                             db=self.session)
        self.assertIsNone(result)

    @patch('src.repository.photo_transformations.get_photo_user_id', return_value=2)
    async def test_advanced_rights_check_not_awaited(self, _):
        with self.assertRaises(HTTPException) as context:
            await advanced_rights_check(photo_id=1,
                                        cur_user_id=1,
                                        cur_user_role=Role.user,
                                        advanced_roles=self.advanced_roles_update,
                                        db=self.session)
        self.assertTrue(context.exception)

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    async def test_get_transformed_photos_found(self, _):
        self.session.query().filter_by().order_by().all.return_value = self.transformations
        result = await get_transformed_photos(photo_id=1, user_id=1, user_role=Role.user, db=self.session)
        self.assertEqual(result, self.transformations)

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    async def test_get_transformed_photos_not_found(self, _):
        self.session.query().filter_by().order_by().all.return_value = []
        result = await get_transformed_photos(photo_id=1, user_id=1, user_role=Role.user, db=self.session)
        self.assertEqual(result, [])

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    @patch('src.repository.photo_transformations.get_filter_preset_by_id', return_value=[{"radius": "max"}])
    @patch('src.repository.photo_transformations.get_photo_public_id', return_value="public_id")
    @patch('src.repository.photo_transformations.build_transformed_url', return_value="transformed_url")
    async def test_create_transformation_from_preset(self, *_):
        result = await create_transformation_from_preset(filter_id=1, photo_id=1,
                                                         description=self.description, user_id=1,
                                                         user_role=Role.user, db=self.session)
        self.assertTrue(hasattr(result, 'id'))

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    @patch('src.repository.photo_transformations.get_photo_public_id', return_value="public_id")
    @patch('src.repository.photo_transformations.build_transformed_url', return_value="transformed_url")
    async def test_create_transformation_no_filter_save(self, *_):
        result = await create_transformation(data=self.body,
                                             save_filter=False,
                                             filter_name=None,
                                             filter_description=None,
                                             user_id=1,
                                             user_role=Role.user,
                                             db=self.session)
        self.assertTrue(hasattr(result, 'id'))

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    @patch('src.repository.photo_transformations.get_photo_public_id', return_value="public_id")
    @patch('src.repository.photo_transformations.build_transformed_url', return_value="transformed_url")
    @patch('src.repository.photo_transformations.create_photo_filter', return_value=None)
    async def test_create_transformation_filter_save(self, *_):
        result = await create_transformation(data=self.body,
                                             save_filter=True,
                                             filter_name='Avatar',
                                             filter_description=None,
                                             user_id=1,
                                             user_role=Role.user,
                                             db=self.session)
        self.assertTrue(hasattr(result, 'id'))

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    @patch('src.repository.photo_transformations.get_photo_public_id', return_value="public_id")
    @patch('src.repository.photo_transformations.build_transformed_url', return_value="transformed_url")
    @patch('src.repository.photo_transformations.create_photo_filter', return_value=None)
    async def test_create_transformation_empty_filter_save(self, *_):
        with self.assertRaises(HTTPException) as context:
            await create_transformation(data=self.body,
                                        save_filter=True,
                                        filter_name=None,
                                        filter_description=None,
                                        user_id=1,
                                        user_role=Role.user,
                                        db=self.session)
        self.assertTrue(context.exception)

    @patch('src.repository.photo_transformations.get_transformation_by_id', return_value=PhotoTransformation())
    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    async def test_change_description(self, *_):
        self.session.query().filter_by().update.return_value = 1
        result = await change_description(trans_id=1, data=self.description,
                                          user_id=1, user_role=Role.user, db=self.session)
        self.assertEqual(type(result), PhotoTransformation)
        self.assertTrue(hasattr(result, 'id'))

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    @patch('src.repository.photo_transformations.get_transformation_by_id', return_value=PhotoTransformation(id=1))
    async def test_remove_transformation_found(self, *_):
        self.session.get.return_value = self.transformation
        result = await remove_transformation(trans_id=1, user_id=1, user_role=Role.user, db=self.session)
        self.assertEqual(result, 1)

    @patch('src.repository.photo_transformations.advanced_rights_check', return_value=None)
    @patch('src.repository.photo_transformations.get_transformation_by_id', return_value=PhotoTransformation())
    async def test_remove_transformation_not_found(self, *_):
        self.session.get.return_value = None
        result = await remove_transformation(trans_id=1, user_id=1, user_role=Role.user, db=self.session)
        self.assertIsNone(result)
