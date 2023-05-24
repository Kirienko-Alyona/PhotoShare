from unittest.mock import MagicMock

import pytest

from src.database.models import User, Role
from src.conf import messages

FILTER_ID = 1
PHOTO_FILTER = {
    "name": "Avatar",
    "description": "Photo transformation preset for avatars",
    "preset": [
        {"gravity": "face", "height": 400, "width": 400, "crop": "crop"},
        {"radius": "max"},
        {"width": 200, "crop": "scale"},
        {"fetch_format": "auto"}
    ]
}


PHOTO_FILTER_UPDATED = {
    "id": 1,
    "name": "Avatar1",
    "description": "Photo transformation preset for avatars updated",
    "preset": []
}


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


def test_create_photo_filter(client, token):
    response = client.post(
        "/api/filters",
        json=PHOTO_FILTER,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data


def test_get_my_photo_filters_found(client, token):
    response = client.get(
        "/api/filters/my/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_update_photo_filter_found(client, token, session):
    response = client.put(
        f"/api/filters/{FILTER_ID}",
        json=PHOTO_FILTER_UPDATED,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == PHOTO_FILTER_UPDATED["name"]


def test_delete_photo_filter(client, token):
    response = client.delete(f"/api/filters/{FILTER_ID}",
                             headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204, response.text


def test_delete_photo_filter_not_found(client, token):
    response = client.delete(f"/api/filters/{FILTER_ID}",
                             headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.COULD_NOT_FIND_FOTO_FILTER


def test_get_my_photo_filters_not_found(client, token):
    response = client.get(
        "/api/filters/my/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text


def test_update_photo_filter_not_found(client, token, session):
    response = client.put(
        f"/api/filters/{FILTER_ID}",
        json=PHOTO_FILTER_UPDATED,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
