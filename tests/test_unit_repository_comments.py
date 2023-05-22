import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.database.models import Comment, User, Photo
from src.schemas.comments import CommentModel, CommentResponse, CommentUpdateModel
from src.repository.comments import (
    add_comment,
    get_comment_by_id,
    get_comments_by_photo,
    update_comment,
    remove_comment
)


class TestComment(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.photo = Photo(id=1)
        self.comment = Comment(id=1)

    async def test_add_comment(self):
        body = CommentModel(photo_id=1, text_comment="test comment")
        result = await add_comment(body=body, user=self.user, db=self.session)
        self.assertEqual(result.photo_id, body.photo_id)
        self.assertEqual(result.text_comment, body.text_comment)
        self.assertTrue(hasattr(result, "user_id"))
        self.assertTrue(hasattr(result, "id"))

    async def test_get_comment_by_id(self):
        result = await get_comment_by_id(1, self.session)
        self.assertTrue(hasattr(result, 'id'))

    async def test_get_comments_by_photo(self):
        comments = [Comment(), Comment(), Comment()]
        self.session.query().filter().all.return_value = comments
        result = await get_comments_by_photo(1, self.session)
        self.assertEqual(result, comments)

    async def test_update_comment_success(self):
        comment_id = 1
        body = CommentUpdateModel(text_comment="New text comment")
        comment = Comment(id=comment_id, text_comment="Old text comment")
        get_comment_by_id_mock = MagicMock(return_value=comment)
        self.session.query.return_value.filter.return_value.update.return_value = 1
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        result = await update_comment(body, comment_id, self.session)
        self.assertTrue(hasattr(result, 'id'))

    async def test_update_comment_not_found(self):
        comment_id = 1
        body = CommentUpdateModel(text_comment="New text comment")
        get_comment_by_id_mock = MagicMock(return_value=None)
        self.session.query.return_value.filter.return_value.update.return_value = 0
        result = await update_comment(body, comment_id, self.session)
        self.assertIsNone(result)

    async def test_remove_comment(self):
        self.session.query().filter().delete.return_value = 1
        result = await remove_comment(1, self.session)
        self.assertEqual(result, 1)
