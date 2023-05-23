from unittest.mock import MagicMock

import pytest

from src.database.models import User, Role, Comment, Photo
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


def test_add_comment(client, token, session):
    photo = Photo(user_id=1, cloud_public_id="cloud_public_id", url_photo="url_photo")
    session.add(photo)
    session.commit()
    session.refresh(photo)
    response = client.post(
        "/api/comments",
        json={"photo_id": 1, "text_comment": "Photo comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data


def test_get_comment_success(client, token, session):
    photo = Photo(user_id=1, cloud_public_id="cloud_public_id", url_photo="url_photo")
    session.add(photo)
    session.commit()
    session.refresh(photo)
    comment = Comment(photo_id=photo.id, user_id=1, text_comment="Photo comment")
    session.add(comment)
    session.commit()
    session.refresh(comment)
    response = client.get(
        "/api/comments/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["text_comment"] == comment.text_comment


def test_get_comment_not_found(client, token):
    response = client.get(
        "/api/comments/12",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND


def test_get_comments_by_photo_success(client, token, session):
    response = client.get(
        "/api/comments",
        params={"photo_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert "id" in data[0]


def test_update_comment_success(client, token, session):
    response = client.put(
        "/api/comments/1",
        json={"comment_id": 1, "text_comment": "New photo comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["text_comment"] == "New photo comment"


def test_update_comment_notfound(client, token, session):
    response = client.put(
        "/api/comments/12",
        json={"comment_id": 1, "text_comment": "New photo comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND


def test_remove_comment_success(client, token, session):
    response = client.delete(
        "api/comments/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204, response.text


def test_remove_comment_not_found(client, token, session):
    response = client.delete(
        "api/comments/12",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.NOT_FOUND
