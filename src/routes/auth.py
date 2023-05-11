from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.users import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:   
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD)

    access_token: str = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token: str = await auth_service.create_refresh_token(data={'sub': user.email})
    await auth_service.get_current_user(access_token, db)
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.post('/request_email')
async def request_email(body: RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: Session = Depends(get_db)) -> dict:

    user = await repository_users.get_user_by_email(body.email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)

    if user.confirmed:
        return {'message': messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED}

    background_tasks.add_task(send_email, email=user.email,
                              subject='Confirm email',
                              template_name='email_template.html',
                              username=user.username,
                              host=request.base_url)
    return {'message': messages.CHECK_YOUR_EMAIL_FOR_CONFIRMATION}


@router.post('/singup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def singup(body: UserModel,
                 background_tasks: BackgroundTasks,
                 request: Request,
                 db: Session = Depends(get_db)) -> dict:

    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_ALREADY_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(send_email, email=new_user.email,
                              subject='Confirm email',
                              template_name='email_template.html',
                              username=new_user.username,
                              host=request.base_url)
    return {'user': new_user, 'detail': messages.USER_SUCCESSFULLY_CREATED}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)) -> dict:

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)

    access_token: str = await auth_service.create_access_token(data={'sub': email})
    refresh_token: str = await auth_service.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:

    email, type_ = await auth_service.get_email_type_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if type_ != 'Confirm email' or user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR)
    if user.confirmed:
        return {'message': messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED}
    await repository_users.confirmed_email(user, db)
    return {'message': messages.EMAIL_CONFIRMED}
