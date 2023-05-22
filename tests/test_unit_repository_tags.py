import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from src.database.models import Tag, User, Photo, Role
from src.conf import messages
from src.repository.tags import (
    get_tags,
    handler_tags,
    get_tag_name,
    add_tag,
    add_tags_for_photo,
    update_tags,
    delete_tag
)


class TestTag(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_tags(self):
        tags = [Tag(), Tag(), Tag()]
        self.session.query().all.return_value = tags
        result = await get_tags(db=self.session)
        self.assertEqual(result, tags)

    def test_handler_tags(self):
        result = handler_tags("test1")
        self.assertEqual(result, ["#test1"])

    async def test_get_tag_name(self):
        tag = Tag()
        self.session.query().filter().first.return_value = tag
        result = await get_tag_name(tag_name="test", db=self.session)
        self.assertEqual(result, tag)

    async def test_add_tag(self):
        tag_name = "test"
        user_id = 1
        result = await add_tag(tag_name=tag_name, user_id=user_id, db=self.session)
        self.assertEqual(result.tag_name, tag_name)
        self.assertEqual(result.user_id, user_id)
        self.assertTrue(hasattr(result, "id"))

    async def test_add_tags_for_photo_without_tag(self):
        tag = Tag(tag_name="#test")
        tag_name = "test"
        user = User(id=1)
        self.session.query().filter().first.return_value = None
        result = await add_tags_for_photo(tags=tag_name, user=user, db=self.session)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0].tag_name, tag.tag_name)
        self.assertEqual(result[0].user_id, user.id)
        self.assertTrue(hasattr(result[0], "id"))

    async def test_add_tags_for_photo_tag_None(self):
        tag_name = None
        user = User(id=1)
        result = await add_tags_for_photo(tags=tag_name, user=user, db=self.session)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    async def test_add_tags_for_photo_with_tag(self):
        tag = Tag(tag_name="#test", user_id=1)
        tag_name = "test"
        user = User(id=1)
        self.session.query().filter().first.return_value = tag
        result = await add_tags_for_photo(tags=tag_name, user=user, db=self.session)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0].tag_name, tag.tag_name)
        self.assertEqual(result[0].user_id, user.id)
        self.assertTrue(hasattr(result[0], "id"))

    async def test_add_tags_for_photo_to_many_tags(self):
        tag_name = "test1 test2, test3 test4 test5 test6"
        user = User(id=1)
        try:
            await add_tags_for_photo(tags=tag_name, user=user, db=self.session)
        except HTTPException as error:
            self.assertEqual(error.detail, messages.TOO_MANY_TAGS)

    async def test_update_tags_to_many_tags(self):
        tag_name = "test"
        photo = Photo(id=1, tags=[Tag() for _ in range(5)])
        user = User(id=1, roles=Role.admin)
        self.session.query(Photo).filter().first.return_value = photo
        try:
            await update_tags(new_tags=tag_name, photo_id=photo.id, db=self.session, user=user)
        except HTTPException as error:
            self.assertEqual(error.detail, messages.TOO_MANY_TAGS_UNDER_THE_PHOTO)

    async def test_update_tags(self):
        tag_name = "test2"
        tag = Tag()
        photo = Photo()
        user = User(id=1, roles=Role.admin)
        self.session.side_effect = [photo, tag]
        result = await update_tags(new_tags=tag_name, photo_id=photo.id, db=self.session, user=user)
        self.assertIsInstance(result, MagicMock)

    async def test_delete_tag(self):
        number = 1
        self.session.query().filter_by().delete.return_value = number
        result = await delete_tag(tag_id=number, db=self.session)
        self.assertEqual(result, number)


if __name__ == '__main__':
    unittest.main()
