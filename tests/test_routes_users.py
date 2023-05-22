from unittest.mock import AsyncMock, MagicMock

import pytest

from src.database.models import User, Role
from src.conf import messages


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


def test_read_me(client, token, user):
    response = client.get(
        "api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["email"] == user["email"]
    assert result["roles"] == "admin"
    assert result["username"] == user["username"]
