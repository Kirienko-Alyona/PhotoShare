from jose import jwt

from src.services.auth import auth_service
from src.conf import messages

def test_get_email_from_token_invalid_token_email(client, user):
    to_encode = {"sub": user.get('email')}
    token = jwt.encode(to_encode, "123", auth_service.ALGORITHM)
    response = client.get(f"/api/auth/confirmed_email/{token}")
    assert response.status_code == 422, response.text
    payload = response.json()
    assert payload["detail"] == messages.INVALID_TOKEN_FOR_EMAIL_VERIFICATION 
      