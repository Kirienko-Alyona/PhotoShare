import cloudinary

from src.conf.config import settings
from src.schemas.photo_transformations import TransformationModel


def build_transformed_url(public_id: str, transformation: TransformationModel) -> str:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation.preset)
