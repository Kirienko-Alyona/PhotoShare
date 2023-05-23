# from jose import jwt
from unittest.mock import MagicMock

from src.database.models import User
from src.conf import messages
from src.services.auth import auth_service


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["user"]["email"] == user.get('email')
    assert payload["detail"] == messages.USER_SUCCESSFULLY_CREATED


def test_repeat_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload["detail"] == messages.ACCOUNT_ALREADY_EXISTS


def test_login_user_not_confirmed_email(client, user):
    response = client.post(
        "/api/auth/login", data={'username': user.get('email'), 'password': user.get('password')})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == messages.EMAIL_NOT_CONFIRMED


def test_request_email_user_not_verified(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    current_user.confirmed == False
    response = client.post("/api/auth/request_email", json=user)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == messages.CHECK_YOUR_EMAIL_FOR_CONFIRMATION


def test_confirmed_email_user_none(client, user, session):
    current_user: User = session.query(User).filter(
        User.email == 'email@example.com').first()
    assert current_user == None
    token = auth_service.create_email_token(data={"sub": "email@example.com"})
    response = client.get(f"/api/auth/confirmed_email/{token}")
    assert response.status_code == 404, response.text
    payload = response.json()
    assert payload["detail"] == messages.NOT_FOUND 
    

def test_confirmed_email_user_verified(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    token = auth_service.create_email_token(data={"sub": user.get('email')})
    response = client.get(f"/api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == messages.EMAIL_CONFIRMED


def test_confirmed_email_user_already_verified(client, user):
    token = auth_service.create_email_token(data={"sub": user.get('email')})
    response = client.get(f"/api/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED
    
    
def test_login_user(client, user, session):
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login", data={'username': user.get('email'), 'password': user.get('password')})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["token_type"] == "bearer"


def test_login_user_with_wrong_password(client, user, session):
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login", data={'username': user.get('email'), 'password': 'password'})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == messages.INVALID_PASSWORD


def test_login_user_with_wrong_email(client, user, session):
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login", data={'username': 'email@example.com', 'password': user.get('password')})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == messages.INVALID_EMAIL


def test_request_email_user_confirmed(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    assert current_user.confirmed == True
    response = client.post("/api/auth/request_email", json=user)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == messages.YOUR_EMAIL_IS_ALREADY_CONFIRMED


def test_refresh_token_true(client, session, user):
    current_user: User = session.query(User).filter(
        User.email == user.get('email')).first()
    headers = {'Authorization': f'Bearer {current_user.refresh_token}'}
    response = client.get('api/auth/refresh_token', headers=headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['token_type'] == 'bearer'
    # TOKEN_TYPE    
    # assert response.json()['access_token'] is not None 
    # assert response.json()['refresh_token'] is not None

# def test_refresh_token_invalid_refresh_token(client, session, user):
#     token ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BleGFtcGxlLmNvbSIsImlhdCI6MTY4Mjk2MDAwNiwiZXhwIjoxNjgzNTY0ODA2LCJzY29wZSI6InJlZnJlc2hfdG9rZW4ifQ.UJE6dv7avuvlRcVRaBagaw69_sKRKhZ_vq3uscFzs3M" 
#     headers = {'Authorization': f'Bearer {token}'} 
#     response = client.get('api/auth/refresh_token', headers=headers) 
#     assert response.status_code == 401, response.text 
#     payload = response.json() 
#     assert payload['detail'] == messages.INVALID_REFRESH_TOKEN 
    
    
# def test_refresh_token_false(client, access_token):
#     headers = {'Authorization': f'Bearer {access_token}'}
#     response = client.get('api/auth/refresh_token', headers=headers)
#     assert response.status_code == 401, response.text
#     payload = response.json()
#     assert payload['detail'] == messages.INVALID_SCOPE_FOR_TOKEN    
    
    
# def test_confirmed_email_invalid_token(client, user, access_token):
#     response = client.get(f"/api/auth/confirmed_email/{access_token}")
#     assert response.status_code == 401, response.text
#     payload = response.json()
#     assert payload['detail'] == messages.INVALID_SCOPE_FOR_TOKEN  
     