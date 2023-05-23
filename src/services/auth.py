from typing import Optional
from datetime import datetime, timedelta
import pickle

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import redis
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings
from src.conf import messages


class Auth:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    redis_cache = redis.Redis(host=settings.redis_host, 
                              port=settings.redis_port, 
                              password=settings.redis_password,
                              db=0)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        The verify_password function takes a plain-text password and hashed password as arguments.
        It then uses the pwd_context object to verify that the plain-text password matches the hashed one.

        :param self: Represent the instance of the class
        :param plain_password: str: Pass in the plain text password that is entered by the user
        :param hashed_password: str: Pass in the hashed password from the database
        :return: A boolean value of true or false
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is to be hashed
        :return: A password hash
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary containing the claims to be encoded in the JWT.
                expires_delta (Optional[float]): An optional timedelta of seconds for the token's expiration time.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: An encoded access token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(hours=2)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

        :param self: Represent the instance of the class
        :param data: dict: Pass the user id to the function
        :param expires_delta: Optional[float]: Set the expiry time of the refresh token
        :return: A refresh token that is encoded using the jwt library
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        encode_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encode_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        The decode_refresh_token function is used to decode the refresh token. It takes in a refresh_token as an
        argument and returns the email of the user who owns that token. If there is no such user, it raises an
        HTTPException with status code 401 (Unauthorized) and detail &quot;Could not validate credentials&quot;.


        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that was sent from the client
        :return: The email of the user who is trying to refresh their access token
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_SCOPE_FOR_TOKEN)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.COULD_NOT_VALIDATE_CREDENTIALS)

    def verify_access_token(self, token: str = Depends(oauth2_scheme)) -> str:
        """
        The verify_jwt_token function is a dependency for the protected endpoints.
        It will be called in the background to check if the user has access rights.
        If there is no valid token, it will raise an HTTPException with the error text.

        :param self: Represent the instance of a class
        :param token: str: Get the token from the authorization header
        :return: The email of the user
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise self.credentials_exception
            else:
                raise self.credentials_exception
        except JWTError as e:
            raise self.credentials_exception
        return email

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.COULD_NOT_VALIDATE_CREDENTIALS
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
            # check token in blacklist
            # black_list_token = await repository_users.find_blacklisted_token(token, db)
            # if black_list_token:
            #     raise credentials_exception
            
        except JWTError as e:
            raise credentials_exception
        
        # get user from redis_cache
        user = self.redis_cache.get(f'user:{email}')
        if user is None:
            print("USER POSTGRES")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.redis_cache.set(f'user:{email}', pickle.dumps(user))
            self.redis_cache.expire(f'user:{email}', 900)
        else:
            print("USER CACHE")
            user = pickle.loads(user)
        return user


    def create_email_token(self, data: dict) -> str:
        """
        The create_email_token function takes a dictionary of data and returns a token.
        The token is created by encoding the data with the SECRET_KEY and ALGORITHM,
        and adding an iat (issued at) timestamp and exp (expiration) timestamp to it.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into a jwt
        :return: A token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'email_token'})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address
        of user associated with that token. If the token is invalid, it raises an HTTPException.

        :param self: Represent the instance of the class
        :param token: str: Decode the token
        :return: Email
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'email_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_SCOPE_FOR_TOKEN)
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=messages.INVALID_TOKEN_FOR_EMAIL_VERIFICATION)


auth_service = Auth()
