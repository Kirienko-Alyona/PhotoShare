from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
#import redis.asyncio as redis

from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()


# client_redis = redis.Redis(
#     host=settings.redis_host,
#     port=settings.redis_port,
#     #password=settings.redis_password,
#     db=0,
# )

# client_redis_for_main = redis.Redis(
#     host=settings.redis_host,
#     port=settings.redis_port,
#     #password=settings.redis_password,
#     db=0,
#     encoding="utf-8",
#     decode_responses=True
# )
