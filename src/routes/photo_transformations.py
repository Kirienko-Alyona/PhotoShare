from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.conf.allowed_operation import allowed_operation_create, allowed_operation_update, allowed_operation_delete
from src.conf.messages import COULD_NOT_FIND_FOTO_BY_ID, COULD_NOT_FIND_FOTO_TRANSFORMATION_BY_ID
from src.database.db import get_db
from src.database.models import User
from src.repository import photo_transformations as repository_transformations
from src.schemas.photo_transformations import (
    PhotoTransformationModelDb,
    PhotoTransformationModel,
    NewDescTransformationModel)
from src.services.auth import auth_service

router = APIRouter(prefix="/photos/transformed", tags=['photo transformations'])


@router.post('/', response_model=PhotoTransformationModelDb,
             name='Create photo transformation', status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create)])
async def create_transformation(transformation: PhotoTransformationModel,
                                db: Session = Depends(get_db),
                                _: User = Depends(auth_service.get_current_user)):
    try:
        transformation = await repository_transformations.create_transformation(transformation, db)
    except repository_transformations.RecordNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{COULD_NOT_FIND_FOTO_BY_ID} {str(err)}')
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")
    return transformation


@router.patch('/{trans_id}', response_model=PhotoTransformationModelDb,
              name='Changing description of transformation', status_code=status.HTTP_200_OK,
              dependencies=[Depends(allowed_operation_update)])
async def change_description(trans_id: int, transformation: NewDescTransformationModel,
                             db: Session = Depends(get_db),
                             _: User = Depends(auth_service.get_current_user)):
    try:
        transformation = await repository_transformations.change_description(trans_id, transformation, db)
    except repository_transformations.RecordNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{COULD_NOT_FIND_FOTO_TRANSFORMATION_BY_ID} {str(err)}')
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")
    return transformation


@router.delete("/{trans_id}",
               name='Delete photo transformation',
               status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allowed_operation_delete)])
async def delete_transformation(trans_id: int,
                                db: Session = Depends(get_db),
                                _: User = Depends(auth_service.get_current_user)):
    try:
        await repository_transformations.remove_transformation(trans_id, db)
    except repository_transformations.RecordNotFound as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'{COULD_NOT_FIND_FOTO_TRANSFORMATION_BY_ID} {str(err)}')
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")
