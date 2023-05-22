import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Rate, User, Photo
from src.schemas.rates import RateModel, RateResponse, PhotoRatingResponse
from src.repository.rates import (
    add_rate,
    get_rate_photo_by_user,
    get_rating_by_photo_id,
    get_detail_rating_by_photo,
    remove_rating
)


class TestRate(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.photo = Photo(id=1)
        self.rate = 5

    async def test_add_rate(self):
        body = RateModel(photo_id=1, rate=4)
        result = await add_rate(body=body, user=self.user, db=self.session)
        self.assertEqual(result.photo_id, body.photo_id)
        self.assertEqual(result.rate, body.rate)

    async def test_get_rate_photo_by_user(self):
        rate = Rate(photo_id=1, user_id=1, rate=5)
        self.session.query().filter().first.return_value = rate
        result = await get_rate_photo_by_user(1, self.session, User)
        self.assertTrue(hasattr(result, 'rate'))

    async def test_get_rating_by_photo_id(self):
        rating = [7, 4.58]
        self.session.query().filter().first.return_value = rating
        result = await get_rating_by_photo_id(1, self.session)
        assert result['average_rate'] == rating[1]
        assert result['rate_count'] == rating[0]

    async def test_get_detail_rating_by_photo(self):
        rates = [Rate(), Rate(), Rate(), Rate(), Rate()]
        self.session.query().filter().all.return_value = rates
        result = await get_detail_rating_by_photo(1, self.session)
        self.assertEqual(result, rates)

    #
    async def test_remove_rating(self):
        self.session.query().filter().delete.return_value = 1
        result = await remove_rating(1, 1, self.session)
        self.assertEqual(result, 1)
