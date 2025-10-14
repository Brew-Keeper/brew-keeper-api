"""Tests of register_user view method."""

from django.test import Client
from rest_framework import status
import pytest

from api.models import User

bad_input_test_cases = [
    # username, password, email, expected_err_text
    (  # 0 - Username has '.'
        "don.pablo",
        "password",
        "don@pablo.com",
        "username cannot contain periods or slashes.",
    ),
    (  # 1 - Username has '/'
        "don/pablo",
        "password",
        "don@pablo.com",
        "username cannot contain periods or slashes.",
    ),
    (  # 1 - Email is required
        "donpablo",
        "password",
        "",
        "Email is a required field.",
    ),
]


class TestRegisterUser:
    """Tests of register_user view method."""

    @pytest.mark.django_db()
    @pytest.mark.parametrize(
        "username, password, email, expected_err_text", bad_input_test_cases
    )
    def test_bad_inputs(self, username, password, email, expected_err_text):
        """Ensure no periods or slashes."""
        # Act
        response = Client().post(
            "/api/register/",
            data={
                "username": username,
                "password": password,
                "email": email,
            },
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.text == expected_err_text

    @pytest.mark.django_db()
    def test_taken_username(self):
        """Ensure we can't register with an existing username."""
        # Arrange
        username = "donpablo"
        User.objects.create(username=username, password="password")

        # Act
        response = Client().post(
            "/api/register/",
            data={
                "username": username,
                "password": "password",
                "email": "don@pablo.com",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.text == "That username is already in the database."

    @pytest.mark.django_db()
    def test_can_create(self):
        """Ensure that someone can register."""
        # Act
        response = Client().post(
            "/api/register/",
            data={
                "username": "donpablo",
                "password": "password",
                "email": "don@pablo.com",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("token") is not None
