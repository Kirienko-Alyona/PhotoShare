from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings
from src.conf.logger import get_logger

logger = get_logger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="PhotoShare app",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three parameters:
            -email: EmailStr, the user's email address.
            -username: str, the username of the user who is registering for an account.  This will be used in a greeting message within the body of the email sent to them.
            -host: str, this is used as part of a URL that will be included in an HTML template for sending emails.

    :param email: EmailStr: Validate the email address
    :param username: str: Pass the username to the email template
    :param host: str: Pass the host of the server to the email template
    :return: A coroutine, which is a special type of object that works with asyncio
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        logger.error(err)


async def send_reset_password_email(email: EmailStr, username: str, host: str):
    """
    The send_forgot_password function sends an email to the user with a link to reset their password.
        Args:
            email (str): The user's email address.
            username (str): The user's username.
            host (str): The hostname of the server where this function is being called from.

    :param email: EmailStr: Specify the email address of the user who forgot their password
    :param username: str: Display the username in the email
    :param host: str: Pass the host name to the template
    :return: A coroutine, which is an object that can be used to start a task
    """
    try:
        token_verification = auth_service.create_password_token({"sub": email})
        message = MessageSchema(
            subject="Reset password.",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password_template.html")
    except ConnectionErrors as err:
        logger.error(err)
