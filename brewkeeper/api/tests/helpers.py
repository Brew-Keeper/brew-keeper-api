"""Helper methods for tests."""

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


def authenticate_user(username="donpablo"):
    """Return an instantiated APIClient with credentials set."""
    client = APIClient()
    if username:
        user = User.objects.get(username=username)
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client
