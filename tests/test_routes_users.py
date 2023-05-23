from unittest.mock import MagicMock, AsyncMock

import pytest

from src.database.models import User, Role, Photo
from src.conf import messages


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


def test_read_users(client, token, user):
    response = client.get(
        "api/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    users = response.json()
    assert isinstance(users, list)
    assert users[0]["email"] == user["email"]
    assert users[0]["roles"] == "admin"
    assert users[0]["username"] == "@" + user["username"]


def test_read_users_not_found(client, token, monkeypatch):
    monkeypatch.setattr("src.repository.users.get_users", AsyncMock())
    response = client.get(
        "api/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND


def test_read_user_by_id(client, token, user, session):
    current_user = get_current_user(user, session)
    response = client.get(
        f"api/users/{current_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["email"] == user["email"]
    assert result["roles"] == "admin"
    assert result["username"] == "@" + user["username"]


def test_read_user_by_id_not_found(client, token, monkeypatch):
    monkeypatch.setattr("src.repository.users.get_user_by_id", AsyncMock(return_value=None))
    response = client.get(
        f"api/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND


def test_read_me(client, token, user):
    response = client.get(
        "api/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["email"] == user["email"]
    assert result["roles"] == "admin"
    assert result["username"] == "@" + user["username"]


def test_read_me_quantity_photos(client, token, user, session):
    session.add(Photo(user_id=1, cloud_public_id="test", url_photo="test.com"))
    session.commit()
    response = client.get(
        "api/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["email"] == user["email"]
    assert result["roles"] == "admin"
    assert result["username"] == "@" + user["username"]
    assert result["quantity_photos"] == 1


def test_user_edit(client, token):
    body = {
        "username": "username",
        "email": "email@test",
        "birthday": "2023-05-23",
        "password": "password",
    }
    response = client.put(
        "api/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json=body
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["email"] == body["email"]
    assert result["roles"] == "admin"
    assert result["username"] == body["username"]
    assert result["birthday"] == body["birthday"]


def test_user_edit_not_found(client, token, monkeypatch):
    monkeypatch.setattr("src.repository.users.update_user", AsyncMock(return_value=None))
    body = {
        "username": "username",
        "email": "email@test",
        "birthday": "2023-05-23",
        "password": "password",
    }
    response = client.put(
        "api/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json=body
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND


def test_ban_user_not_found(client, token, monkeypatch):
    monkeypatch.setattr("src.repository.users.ban_user", AsyncMock(return_value=None))
    response = client.patch(
        "api/users/ban/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.USER_NOT_FOUND


def test_ban_user(client, token, user):
    response = client.patch(
        "api/users/ban/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 202, response.text
    result = response.json()
    assert result["active"] is False
