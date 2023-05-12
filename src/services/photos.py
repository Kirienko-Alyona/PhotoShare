from uuid import uuid4

from fastapi import UploadFile
import cloudinary
import cloudinary.uploader
import cloudinary.api

from src.conf.config import settings


def update_filename(filename: str):
    '''
    The update_filename function takes a filename as an argument and returns the same filename with a random UUID appended to it.

    :param filename: str: Specify the type of data that is expected to be passed into the function
    :return: A new filename
    :doc-author: Trelent
    '''
    ext = filename.split('.')[-1]
    filename = f'{uuid4().hex}.{ext}'
    return filename


async def upload_photo(file: UploadFile, public_id: str) -> str:
    '''
    The upload_avatar function takes in a file and name, uploads the file to cloudinary,
    and returns the url of that image. The function is asynchronous because it uses await.

    :param file: UploadFile: Get the file from the request
    :param name: str: Give the image a unique name
    :return: The url of the uploaded image
    '''
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    await cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True,
                                     eager=[{'width': 250, 'height': 250, 'crop': 'fill'}])
    image_info = await cloudinary.api.resource(public_id)
    src_url = image_info['derived'][0]['secure_url']
    return src_url
