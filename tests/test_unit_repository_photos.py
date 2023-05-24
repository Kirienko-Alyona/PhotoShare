import base64
import io
import unittest
from fastapi.responses import Response
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Role
from src.schemas.photos import PhotoResponse
from src.repository import tags as repository_tags
import qrcode as qrcode
from src.repository.photos import (
    add_photo,
    get_photos,
    get_photo_by_id,
    #get_photo_by_id_oper,
    delete_photo,
    generate_qrcode,
    update_tags_descriptions_for_photo,
    untach_tag,
)


class TestPhotos(unittest.IsolatedAsyncioTestCase):
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


    async def test_update_tags_descriptions_for_photo(self):
        photo = self.photo_test = Photo(
            id=1,
            user_id=self.user.id,
            cloud_public_id=f'ca4598c8749b4237a5f4b9d2583e4045',
            url_photo=f'https://res.cloudinary.com/web9storage/image/upload/v1684580219/ca4598c8749b4237a5f4b9d2583e4045.jpg',
            description='New jump',
            tags=[],
        )
        self.session.query().filter().first.return_value = photo
        result = await update_tags_descriptions_for_photo(photo_id=photo.id,
                                                          new_description=None,
                                                          tags=None,
                                                          db=self.session,
                                                          user=self.user)
        self.assertEqual(result, photo)


    async def test_generate_qrcode(self):
        img = qrcode.make(self.photo_test.url_photo)
        buffer = io.BytesIO()
        img.save(buffer)
        #qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        result = await generate_qrcode(photo_url=self.photo_test.url_photo)
        self.assertIsInstance(result, Response)
        #self.assertEqual(result["qrcode_encode"], qr_base64)


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

    # need check
    async def test_add_photo(self):
        photo = self.photo_test
        result = await add_photo(url=photo.url_photo,
                                 public_id=photo.cloud_public_id,
                                 description=photo.description,
                                 tags=None,
                                 db=self.session,
                                 user=self.user)
        self.assertEqual(result.url_photo, photo.url_photo)
        self.assertEqual(result.description, photo.description)
        self.assertEqual(result.cloud_public_id, photo.cloud_public_id)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_photos(self):
        photos = [(
            self.photo_test.id,
            self.photo_test.url_photo,
            self.photo_test.description,
            None
        )]
        self.session.query().outerjoin().group_by().limit().offset().all.return_value = photos
        result = await get_photos(user_id=None,
                                  cur_user_id=None,
                                  cur_user_role=Role.user,
                                  tag_name=None,
                                  rate_min=None,
                                  rate_max=None,
                                  created_at_min=None,
                                  created_at_max=None,
                                  limit=10,
                                  offset=0,
                                  db=self.session
                                  )
        self.assertIsInstance(result, list)
        self.assertEqual(result[0].id, self.photo_test.id)
        self.assertEqual(result[0].url_photo, self.photo_test.url_photo)
        self.assertEqual(result[0].description, self.photo_test.description)
        self.assertIsNone(result[0].rating)


if __name__ == '__main__':
    unittest.main()
