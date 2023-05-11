from enum import Enum

from sqlalchemy import Boolean, Column, Date, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()
    
    
class Role(Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String(50), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(18), nullable=False)
    birthday = Column(Date)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    roles = Column(Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)
    active = Column(Boolean, default=False)
    role_id = Column(ForeignKey("roles.id", ondelete="CASCADE"), default=None)
    role = relationship("Role", backref="users")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint("username", "phone", "email", "id", name="unique_user_username_phone_email_id"), )
    
    
class Photo(Base):
    __tablename__ = "photos"   
    id = Column(Integer, primary_key=True) 
    url_photo = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    tag = relationship('Tag', cascade="all, delete-orphan", back_populates="photo")
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), default=None)
    __table_args__ = (UniqueConstraint("user_id", name="unique_photo_user"), )
    
    
class Tag(Base):
    __tablename__ = "tags"   
    id = Column(Integer, primary_key=True) 
    tag_name = Column(String, nullable=True)
    photo = relationship("Photo", back_populates="tag")
    user_id = Column(ForeignKey('users.id'), default=None)
    __table_args__ = (UniqueConstraint("tag_name", name="unique_tags_name"), )
    
    
class Comment(Base):
    __tablename__ = "comments"   
    id = Column(Integer, primary_key=True) 
    text_comment = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    photo_id = Column(ForeignKey('photos.id', ondelete='CASCADE'), default=None)
    photo = relationship('Photo', backref="comments", uselist=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), default=None)