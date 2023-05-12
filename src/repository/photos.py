from sqlalchemy.orm import Session

from src.database.models import User, Photo


async def add_photo(url: str, db: Session, user: User):
    photo = Photo(url_photo=url, user_id=user.id)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo