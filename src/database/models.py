import enum
from sqlalchemy import Enum

from sqlalchemy import Boolean, Column, Date, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.schema import ForeignKey, Table
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True)
    # last_name = Column(String, nullable=True)
    username = Column(String(30), nullable=False)
    email = Column(String(50), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    # phone = Column(String(18), nullable=True)
    birthday = Column(Date)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    roles = Column(Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint('username', 'email', 'id', name='unique_user_username_email_id'),)


photo_m2m_tag = Table(
    'photo_m2m_tag',
    Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    cloud_public_id = Column(String(255), nullable=False)
    url_photo = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    transformations = relationship('PhotoTransformation', cascade='all, delete-orphan', back_populates='original_photo')
    tags = relationship('Tag', secondary=photo_m2m_tag, back_populates='photos')


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    tag_name = Column(String, nullable=True)
    photos = relationship('Photo', secondary=photo_m2m_tag, back_populates='tags')
    user_id = Column(ForeignKey('users.id'), default=None)
    __table_args__ = (UniqueConstraint('tag_name', name='unique_tags_name'),)


class Comment(Base):
    __tablename__ = 'comments'   
    id = Column(Integer, primary_key=True) 
    text_comment = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    photo_id = Column(ForeignKey('photos.id', ondelete='CASCADE'), nullable=False)
    photo = relationship('Photo', backref='comments')
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', backref='comments')


# class PhotoTransformer(Base):
#     __tablename__ = 'photo_transformers'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
#     name = Column(String(128), nullable=False, unique=True, index=True)
#     description = Column(String(255), nullable=True)
#     preset = Column(JSONB, nullable=False)  # [{'radius': "max"}, {'width': 200, 'crop': "scale"},]
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PhotoTransformation(Base):
    __tablename__ = 'photo_transformations'
    id = Column(Integer, primary_key=True)
    photo_id = Column(ForeignKey('photos.id', ondelete='CASCADE'), nullable=False)
    transformed_url = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    original_photo = relationship('Photo', back_populates='transformations')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
