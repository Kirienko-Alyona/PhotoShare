from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import File, UploadFile

from src.database.models import Tag, User, Role, Photo
from src.conf import messages
from src.schemas.photo_transformations import PhotoTransformationModel
from src.services.auth import auth_service
from src.database.db import get_db, client_redis


def get_current_user(user, session):
    current_user: User = session.query(User).filter_by(email=user.get("email")).first()
    return current_user


@pytest.fixture()
def token(client, session, user, monkeypatch):
    monkeypatch.setattr("src.routes.auth.send_email", MagicMock())
    monkeypatch.setattr("src.services.auth.client_redis.get", AsyncMock(return_value=None))
    monkeypatch.setattr("src.services.auth.client_redis.set", AsyncMock())

    client.post("api/auth/singup", json=user)
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


def test_create_photo(client, token):
    # with patch.object(auth_service, 'r') as r_mock:
    #     r_mock.get.return_value = None
    file_path = r'C:\Users\nikolay.grishyn\Documents\GitHub\PhotoShare\static\images\favicon.ico'
    _file = open(file_path, "rb")
    response = client.post("/api/photos/",
                           data={'photo': _file,
                                 "description": "My new photo",
                                 "tags": None,
                                 "transformation": PhotoTransformationModel.Config.schema_extra['example'],
                                 "save_filter": False,
                                 'filter_name': None,
                                 'filter_description': None,
                                 'filter_id': None},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["description"] == "My new photo"
    assert "id" in data


def test_get_photo_id(client,token,session):
    photo = Photo(
        id=1,
        user_id=1,
        cloud_public_id=f'ca4598c8749b4237a5f4b9d2583e4045',
        url_photo=f'https://res.cloudinary.com/web9storage/image/upload/v1684580219/ca4598c8749b4237a5f4b9d2583e4045.jpg',
        description=f'Man jump over a hill',
        tags=[],
    )
    session.add(photo)
    session.commit()

    response = client.get("/api/photos/",
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 200, response.text
    # data = response.json()
