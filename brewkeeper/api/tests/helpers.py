from rest_framework.test import APIClient
from django.contrib.auth.models import User


def authenticate_user(username='donpablo'):
    user = User.objects.get(username=username)
    client = APIClient()
    client.force_authenticate(user=user)
    return client
