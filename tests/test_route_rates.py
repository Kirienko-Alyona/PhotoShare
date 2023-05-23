from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.database.models import User, Role, Rate, Photo
from src.conf import messages


def get_current_user(user, session):
    current_user: User = session.query(User).filter_by(email=user.get("email")).first()
    return current_user


@pytest.fixture()
def token(client, session, user, monkeypatch):
    monkeypatch.setattr("src.routes.auth.send_email", MagicMock())
    monkeypatch.setattr("src.servise.auth.auth_servise.redis_cache.get", AsyncMock(return_value=None))
    monkeypatch.setattr("src.servise.auth.auth_servise.redis_cache.set", AsyncMock())

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


@pytest.fixture()
def token_second_user(client, session, user, monkeypatch):
    monkeypatch.setattr("src.routes.auth.send_email", MagicMock())
    monkeypatch.setattr("src.services.auth.client_redis.get", AsyncMock(return_value=None))
    monkeypatch.setattr("src.services.auth.client_redis.set", AsyncMock())

    client.post("api/auth/singup", json=user)
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


def test_create_rate_success(client, token_second_user, session):
    response = client.post(
        "/api/rating",
        json={"photo_id": 1, "rate": 5},
        headers={"Authorization": f"Bearer {token_second_user}"}
    )
    assert response.status_code == 404, response.text


def test_get_rating_by_photo_id_forbidden(client, token_second_user, session):
    response = client.get(
        "/api/rating/1",
        headers={"Authorization": f"Bearer {token_second_user}"}
    )
    assert response.status_code == 403, response.text


def test_get_rating_by_photo_id_success(client, token, session):
    response = client.get(
        "/api/rating/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


# def test_remove_rate_success(client, token, session):
#     photo_id = 1
#     user_id = 1
#     url = f"/api/photos/{photo_id}/users/{user_id}"
#     response = client.delete(
#         url,
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 204, response.text


def test_remove_rate_not_found(client, token, session):
    photo_id = 1
    user_id = 2
    url = f"/api/photos/{photo_id}/users/{user_id}"
    response = client.delete(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
