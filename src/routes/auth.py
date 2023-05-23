from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.schemas.users import UserModel, UserResponse, TokenModel
from src.schemas.email import RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.email import send_email
from src.conf import messages


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()
allowed_read = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post('/login', name="Login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
        The access token can be used to make requests on behalf of that user.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Access the database
    :return: A dictionary with the access token, refresh token and bearer
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD)
    if not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.FORBIDDEN)

    access_token: str = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token: str = await auth_service.create_refresh_token(data={'sub': user.email})
    await auth_service.get_current_user(access_token, db)
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.post('/admin_login', name="Admin Login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD)
    if not (user.active and (user.roles == Role.admin)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.FORBIDDEN)

    access_token: str = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token: str = await auth_service.create_refresh_token(data={'sub': user.email})
    await auth_service.get_current_user(access_token, db)
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.post('/request_email', name="Request Email")
async def request_email(body: RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: Session = Depends(get_db)) -> dict:
    """
    The request_email function is used to send a confirmation email to the user.
        The function takes in an email address and sends a confirmation link to that
        address. If the user does not exist, it returns an error message.

    :param body: RequestEmail: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Pass the database session to the repository functions
    :return: A message to the user if they are already confirmed
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)

    if user.confirmed:
        return {'message': messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED}

    background_tasks.add_task(send_email, email=user.email,
                              username=user.username,
                              host=request.base_url)
    return {'message': messages.CHECK_YOUR_EMAIL_FOR_CONFIRMATION}


@router.post('/signup', name="SignUp", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def singup(body: UserModel,
                 background_tasks: BackgroundTasks,
                 request: Request,
                 db: Session = Depends(get_db)) -> dict:
    """
    The singup function creates a new user in the database.
        It takes an email, username and password as input parameters.
        The function returns a JSON object with the newly created user's information.

    :param body: UserModel: Validate the data sent by the user
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the host url to send in the email
    :param db: Session: Get the database session
    :return: A dictionary with the user and a message
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_ALREADY_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(send_email, new_user.email,
                              new_user.username,
                              request.base_url)
    return {'user': new_user, 'detail': messages.USER_SUCCESSFULLY_CREATED}


@router.get('/refresh_token', name="Refresh Token", response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)) -> dict:
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.

    :param credentials: HTTPAuthorizationCredentials: Get the access token from the request header
    :param db: Session: Get the database session
    :return: A dictionary with the new access_token, refresh_token and token type
    """
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


@router.get('/confirmed_email/{token}', name="Confirmed Email")
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do not exist,
        an error message is returned. If they do exist but their email has already been confirmed,
        another error message is returned. Otherwise (if everything goes well), we update their
        record in our database so that their &quot;confirmed&quot; field becomes True.

    :param token: str: Get the token from the url
    :param db: Session: Access the database
    :return: A message
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    if user.confirmed:
        return {'message': messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED}
    await repository_users.confirmed_email(email, db)
    return {'message': messages.EMAIL_CONFIRMED}


@router.get("/logout", name="Logout", dependencies=[Depends(allowed_read)], status_code=status.HTTP_200_OK)
async def logout(credentials: HTTPAuthorizationCredentials = Security(security),
                 db: Session = Depends(get_db)):
    token = credentials.credentials
    await repository_users.block_token(token, db)
    return {"detail": messages.EXIT_COMPLETED_SUCCESSFULLY}

