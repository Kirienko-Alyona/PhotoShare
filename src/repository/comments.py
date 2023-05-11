from sqlalchemy.orm import Session

from src.database.models import Comment, User, Photo

from src.schemas.comments import CommentModel


async def add_comment(db: Session, user: User, body: CommentModel):
    comment = Comment(**body.dict(), user_id=user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comment_by_id(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    return comment


async def get_comments_by_photo(db: Session, photo: Photo):
    comments = db.query(Comment).join(Photo).filter(Photo.id == photo.id).all()
    return comments


async def update_comment(db: Session, comment_id: int, body: CommentModel):
    comment = await get_comment_by_id(db, comment_id)
    if comment:
        comment.text_comment = body.text_comment
        db.commit()
    return comment


async def remove_comment(db: Session, comment_id: int):
    comment = await get_comment_by_id(db, comment_id)
    if comment:
        db.delete(comment)
        db.commit()
    return comment
