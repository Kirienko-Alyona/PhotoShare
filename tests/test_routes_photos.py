from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import File, UploadFile

from src.database.models import Tag, User, Role, Photo
from src.conf import messages
from src.schemas.photo_transformations import PhotoTransformationModel
from src.services.auth import auth_service
from src.database.db import get_db


def get_current_user(user, session):
    current_user: User = session.query(User).filter_by(email=user.get("email")).first()
    return current_user


@pytest.fixture()
def token(client, session, user, monkeypatch):
    monkeypatch.setattr("src.routes.auth.send_email", MagicMock())
    monkeypatch.setattr("src.services.auth.auth_service.redis_cache.get", MagicMock(return_value=None))
    monkeypatch.setattr("src.services.auth.auth_service.redis_cache.set", MagicMock())

    client.post("api/auth/signup", json=user)
    current_user = get_current_user(user, session)
    current_user.confirmed = True
    current_user.roles = Role.admin
    session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user.get("email"),
            "password": user.get("password")
        }
    )
    data = response.json()
    return data["access_token"]


#need check or delete
# def test_create_photo(client, token):
#     file_path = r'C:\Users\nikolay.grishyn\Documents\GitHub\PhotoShare\static\images\favicon.ico'
#     _file = open(file_path, "rb")
#     response = client.post("/api/photos/?description=My new photo",
#                            data={'photo': UploadFile(file=_file)},
#                            headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 201, response.text
#     # data = response.json()
#     # assert data["description"] == "My new photo"
#     # assert "id" in data


def test_get_photo_id(client, token, session):
    photo = Photo(
        id=2,
        user_id=1,
        cloud_public_id=f'ca4598c8749b4237a5f4b9d2583e4045',
        url_photo=f'https://res.cloudinary.com/web9storage/image/upload/v1684580219/ca4598c8749b4237a5f4b9d2583e4045.jpg',
        description=f'Man jump over a hill',
        tags=[],
    )
    session.add(photo)
    session.commit()

    response = client.get("/api/photos/2",
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["description"] == 'Man jump over a hill'


def test_get_photo_id_not_found(client, token):
    response = client.get("/api/photos/3",
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND


def test_get_photos(client, token):
    response = client.get("/api/photos/",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)



def test_update_tags_by_photo(client, token):
    response = client.put('/api/photos/2?new_description=Updated description',
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["description"] == "Updated description"


def test_update_tags_by_photo_not_found(client, token):
    response = client.put("/api/photos/3?new_description=Updated description'",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.PHOTO_NOT_FOUND



def test_untach_tag_photo(client, token, session):
    tag = Tag(
        tag_name='#jump',
        user_id=1,
    )
    photo = Photo(
        id=4,
        user_id=1,
        cloud_public_id=f'ca4598c8749b4237a5f4b9d2583e4045',
        url_photo=f'https://res.cloudinary.com/web9storage/image/upload/v1684580219/ca4598c8749b4237a5f4b9d2583e4045.jpg',
        description=f'Man jump over a hill',
        tags=[tag]
    )
    session.add(photo)
    session.commit()
    response = client.patch("/api/photos/untach_tag/4?tags=jump",
                            headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text


def test_photo_remove(client, token):
    response = client.delete("/api/photos/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204, response.text


def test_photo_remove_not_found(client, token):
    response = client.delete("/api/photos/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND
