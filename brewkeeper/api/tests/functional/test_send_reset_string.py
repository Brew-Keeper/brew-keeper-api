"""Test send_reset_string."""

from dataclasses import dataclass

from django.contrib.auth.models import User
import pytest
from rest_framework import status

from api.exceptions import IntegrationError
from api.models import UserInfo
from api.tests.helpers import authenticate_user

########################################
# Parametrize Test Case Definitions
########################################

send_reset_string_test_cases = [
    # mailgun_response_code, expected_error, expected_status
    (  # 0 - Happy path
        status.HTTP_200_OK,
        None,
        status.HTTP_200_OK,
    ),
    (  # 0 - Happy path
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        IntegrationError,
        None,
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mailgun_response_code, expected_error, expected_status",
    send_reset_string_test_cases,
)
def test_send_reset_string(
    mocker, mailgun_response_code, expected_error, expected_status
):
    """Test that we rollback if Mailgun fails."""
    # Arrange
    @dataclass
    class TestResponseType:
        status_code: int

    mocker.patch(
        "api.views.requests.post", return_value=TestResponseType(status_code=mailgun_response_code)
    )
    user = User.objects.create(username="donpablo", password="password")
    client = authenticate_user()
    data = {"username": "donpablo"}

    if expected_error:
        # Act/Assert
        with pytest.raises(expected_error):
            client.post("/api/get-reset/", data=data)

        # demonstrate that the UserInfo object creation was rolled back
        with pytest.raises(UserInfo.DoesNotExist):
            UserInfo.objects.get(user_id=user.pk)
        return

    # Act
    response = client.post("/api/get-reset/", data=data)

    # Assert
    assert response.status_code == expected_status
