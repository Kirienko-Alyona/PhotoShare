from fastapi import Depends, status, APIRouter, File, UploadFile
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import photos as repository_photos
from src.schemas.photos import PhotoResponse
from src.services.auth import auth_service
from src.services.photos import upload_photo, update_filename


router = APIRouter(prefix='/photos', tags=['photos'])


@router.post('/', response_model=PhotoResponse, name='Create photo', status_code=status.HTTP_201_CREATED)
async def create_photo(photo: UploadFile = File(), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    
    public_id = update_filename(photo.filename)
    url = upload_photo(photo, public_id)
    photo = await repository_photos.add_photo(url, db, current_user)
    return photo
