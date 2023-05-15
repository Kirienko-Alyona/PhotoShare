from uuid import uuid4

from fastapi import UploadFile
import cloudinary
import cloudinary.uploader
import cloudinary.api

from src.conf.config import settings


def upload_photo(file: UploadFile) -> tuple[str, str]:
    """
    The upload_avatar function takes in a file and name, uploads the file to cloudinary,
    and returns the url of that image. The function is asynchronous because it uses await.

    :param file: UploadFile: Get the file from the request
    :param name: str: Give the image a unique name
    :return: The url of the uploaded image
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    public_id = uuid4().hex
    cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    image_info = cloudinary.api.resource(public_id)
    src_url = image_info['secure_url']
    return src_url, public_id
