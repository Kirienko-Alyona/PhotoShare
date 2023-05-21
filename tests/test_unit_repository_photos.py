import io
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Role
from src.schemas.photos import PhotoResponse
from src.repository import tags as repository_tags
import qrcode as qrcode
from src.repository.photos import (
    add_photo,
    get_photos_by_tag_name,
    get_photo_by_id,
    get_photo_by_id_oper,
    delete_photo,
    generate_qrcode,
    update_tags_descriptions_for_photo,
    untach_tag,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1,
                         roles=Role.user)
        self.photo_test = Photo(
            id=1,
            user_id=self.user.id,
            cloud_public_id=f'ca4598c8749b4237a5f4b9d2583e4045',
            url_photo=f'https://res.cloudinary.com/web9storage/image/upload/v1684580219/ca4598c8749b4237a5f4b9d2583e4045.jpg',
            description=f'Man jump over a hill',
        )

    async def test_delete_photo(self):
        photo = self.photo_test
        self.session.query().filter().first.return_value = photo
        result = await delete_photo(photo_id=self.photo_test.id,
                                    db=self.session,
                                    user=self.user)
        self.assertEqual(result, photo)

    async def test_delete_photo_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_photo(photo_id=self.photo_test.id, db=self.session, user=self.user)
        self.assertIsNone(result)

    async def test_delete_photo_wrong_user_id(self):
        photo = Photo(id=1,
                      user_id=2)
        result = await delete_photo(photo_id=photo.id,
                                    db=self.session,
                                    user=self.user)
        self.assertIsNone(result)

    async def test_delete_photo_wrong_user_id_Admin(self):
        photo = Photo(id=1,
                      user_id=2,
                      )
        user = User(id=1,
                    roles=Role.admin,
                    )
        self.session.query().filter().first.return_value = photo
        result = await delete_photo(photo_id=photo.id,
                                    db=self.session,
                                    user=user)
        self.assertEqual(result, photo)

    async def test_delete_photo_wrong_user_id_Moderator(self):
        photo = Photo(id=1,
                      user_id=2,
                      )
        user = User(id=1,
                    roles=Role.moderator,
                    )
        self.session.query().filter().first.return_value = photo
        result = await delete_photo(photo_id=photo.id,
                                    db=self.session,
                                    user=user)
        self.assertEqual(result, photo)

    async def test_get_photo_by_id(self):
        photo = self.photo_test
        self.session.query().filter().first.return_value = photo
        result = await get_photo_by_id(photo_id=photo.id,
                                       db=self.session,
                                       user=self.user)
        self.assertEqual(result, photo)

    async def test_get_photo_by_id_wrong_user_id(self):
        photo = Photo(id=1,
                      user_id=2,
                      )
        result = await get_photo_by_id(photo_id=photo.id,
                                       db=self.session,
                                       user=self.user)
        self.assertIsNone(result)

    async def test_get_photo_by_id_wrong_user_id_Admin(self):
        photo = Photo(id=1,
                      user_id=2,
                      )
        user = User(id=1,
                    roles=Role.admin,
                    )
        self.session.query().filter().first.return_value = photo
        result = await get_photo_by_id(photo_id=photo.id,
                                       db=self.session,
                                       user=user)
        self.assertEqual(result, photo)

    # need check
    async def test_update_tags_descriptions_for_photo(self):
        photo = self.photo_test = Photo(
            id=1,
            user_id=self.user.id,
            cloud_public_id=f'ca4598c8749b4237a5f4b9d2583e4045',
            url_photo=f'https://res.cloudinary.com/web9storage/image/upload/v1684580219/ca4598c8749b4237a5f4b9d2583e4045.jpg',
            description='New jump',
            tags=[],
        )
        new_descr = 'New jump'
        tag = 'new_tag'
        photo.description = new_descr
        # photo.tags = [tag]
        self.session.query().filter().first.return_value = photo
        result = await update_tags_descriptions_for_photo(photo_id=photo.id,
                                                          new_description=new_descr,
                                                          tags=tag,
                                                          db=self.session,
                                                          user=self.user)
        self.assertEqual(result, photo)

    # need check
    async def test_generate_qrcode(self):
        qrcode.make = MagicMock(spec=qrcode)
        io.BytesIO = MagicMock()
        photo = self.photo_test
        img = qrcode.make(photo.url_photo)
        buffer = io.BytesIO
        # img.save(buffer)
        result = await generate_qrcode(photo_url=photo.url_photo)
        self.assertEqual(result['qrcode_encode'], img)

    async def test_untach_tag(self):
        photo = Photo(
            id=1,
            user_id=self.user.id,
            cloud_public_id=f'ca4598c8749b4237a5f4b9d2583e4045',
            url_photo=f'https://res.cloudinary.com/web9storage/image/upload/v1684580219/ca4598c8749b4237a5f4b9d2583e4045.jpg',
            description=f'Man jump over a hill',
            tags=[],
        )
        self.session.query().filter().first.return_value = photo
        result = await untach_tag(photo_id=photo.id, tags='test', db=self.session, user=self.user)
        self.assertEqual(result, photo)


if __name__ == '__main__':
    unittest.main()
