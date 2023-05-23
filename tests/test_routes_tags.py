from unittest.mock import MagicMock

import pytest

from src.database.models import Tag, User, Role
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


def test_get_tags_not_found(client, token, session):
    response = client.get(
        "api/tags",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.TAGS_NOT_FOUND


def test_get_tags(client, token, session):
    tag = Tag(tag_name="tag_name")
    session.add(tag)
    session.commit()

    response = client.get(
        "api/tags",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["tag_name"] == tag.tag_name
    assert "id" in data[0]


def test_delete_tag(client, token, session):
    response = client.delete(
        "api/tags/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204, response.text


def test_delete_tag_not_found(client, token, session):
    response = client.delete(
        "api/tags/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.TAG_NOT_FOUND
