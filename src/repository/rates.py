from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.models import Rate, User

from src.schemas.rates import RateModel


async def add_rate(body: RateModel, db: Session, user: User):
    rate = Rate(**body.dict(), user_id=user.id)
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


async def get_rate_photo_by_user(photo_id: int, db: Session, user: User):
    rate = db.query(Rate).filter(Rate.photo_id == photo_id, Rate.user_id == user.id).first()
    return rate


async def get_rating_by_photo_id(photo_id: int, db: Session):
    result = db.query(func.count(Rate.user_id), func.avg(Rate.rate)).filter(Rate.photo_id == photo_id).first()
    return {'average_rate': result[1] or 0, 'rate_count': result[0]}


async def get_detail_rating_by_photo(photo_id: int, db: Session):
    rates = db.query(Rate).filter(Rate.photo_id == photo_id).all()
    return rates


async def remove_rating(photo_id: int, user_id: int, db: Session):
    count = db.query(Rate).filter(Rate.photo_id == photo_id, Rate.user_id == user_id).delete()
    db.commit()
    return count
