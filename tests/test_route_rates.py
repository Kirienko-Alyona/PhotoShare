from unittest.mock import MagicMock

import pytest

from src.database.models import User, Role, Photo
from src.conf import messages


def get_current_user(user, session):
    current_user: User = session.query(User).filter_by(email=user.get("email")).first()
    return current_user


@pytest.fixture()
def token_user(client, session, user, monkeypatch):
    monkeypatch.setattr("src.routes.auth.send_email", MagicMock())
    monkeypatch.setattr("src.services.auth.auth_service.redis_cache.get", MagicMock(return_value=None))
    monkeypatch.setattr("src.services.auth.auth_service.redis_cache.set", MagicMock())

    client.post("api/auth/signup", json=user)
    current_user = get_current_user(user, session)
    current_user.confirmed = True
    current_user.roles = Role.user
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


def test_create_rate_error_forbidden(client, token, session):
    photo = Photo(user_id=1, cloud_public_id="cloud_public_id", url_photo="url_photo")
    session.add(photo)
    session.commit()
    session.refresh(photo)
    response = client.post(
        "/api/rating",
        json={"photo_id": 1, "rate": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403, response.text


def test_create_rate_error_not_found(client, token, session):
    response = client.post(
        "/api/rating",
        json={"photo_id": 2, "rate": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text


def test_create_rate_success(client, token_user, session):
    response = client.post(
        "/api/rating",
        json={"photo_id": 2, "rate": 5},
        headers={"Authorization": f"Bearer {token_user}"}
    )
    assert response.status_code == 404, response.text


def test_get_rating_by_photo_id_forbidden(client, token_user, session):
    response = client.get(
        "/api/rating/1",
        headers={"Authorization": f"Bearer {token_user}"}
    )
    assert response.status_code == 403, response.text


def test_get_rating_by_photo_id_success(client, token, session):
    response = client.get(
        "/api/rating/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_remove_rate_not_found(client, token, session):
    response = client.delete(
        "/api/photos/10/users/2",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
