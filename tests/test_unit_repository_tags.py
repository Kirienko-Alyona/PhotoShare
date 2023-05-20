import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Tag, User, Photo, Role
from src.repository.tags import (
    get_tags,
    get_tags_by_user_id,
    handler_tags,
    get_tag_name,
    add_tag,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_tags(self):
        tags = [Tag(), Tag(), Tag()]
        self.session.query().all.return_value = tags
        result = await get_tags(db=self.session)
        self.assertEqual(result, tags)

    async def test_get_tags_by_user_id(self):
        photo = Photo(id=1)
        user = User(id=1, roles=Role.admin)
        self.session.query().filter().first.return_value = photo
        result = await get_tags_by_user_id(photo_id=1, db=self.session, user=user)
        self.assertEqual(result, photo)

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


if __name__ == '__main__':
    unittest.main()
