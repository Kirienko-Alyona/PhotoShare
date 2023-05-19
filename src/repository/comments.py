from sqlalchemy.orm import Session

from src.database.models import Comment, User

from src.schemas.comments import CommentModel, CommentUpdateModel


async def add_comment(body: CommentModel, db: Session, user: User):
    comment = Comment(**body.dict(), user_id=user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comment_by_id(comment_id: int, db: Session):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    return comment


async def get_comments_by_photo(photo_id: int, db: Session):
    comments = db.query(Comment).filter(Comment.photo_id == photo_id).all()
    return comments


async def update_comment(body: CommentUpdateModel, comment_id: int, db: Session):
    comment = await get_comment_by_id(comment_id, db)
    if comment:
        count = db.query(Comment).filter(Comment.id == comment_id).update({
            'text_comment': body.text_comment
        })
        db.commit()
        if count == 1:
            db.refresh(comment)
            return comment
    return None


async def remove_comment(comment_id: int, db: Session):
    count = db.query(Comment).filter(Comment.id == comment_id).delete()
    db.commit()
    return count
