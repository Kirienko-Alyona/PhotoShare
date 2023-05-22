from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import File

from src.database.models import Tag, User, Role
from src.conf import messages
from src.schemas.photo_transformations import PhotoTransformationModel
from src.services.auth import auth_service


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
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post("/api/photos/",
                               data={'photo': File(rf'C:\Users\nikolay.grishyn\Documents\Tree.jfif'),
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

# def test_get_photo_id(client,token):
#     with patch.object(auth_service, 'r') as r_mock:
#         r_mock.get.return_value = None
#         response = client.get("/api/contacts/1",
#                               headers={"Authorization": f"Bearer {token}"}
#                               )
#         assert response.status_code == 200, response.text
#         data = response.json()
