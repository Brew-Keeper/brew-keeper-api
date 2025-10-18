"""Tests for BrewNote API actions."""

from django.contrib.auth.models import User
import pytest
from rest_framework import status

from api.models import BrewNote, Recipe
from api.tests.helpers import authenticate_user

########################################
# Parametrize Test Case Definitions
########################################

creator_username = "donpablo"
other_username = "not_the_creator"

status_201_or_404_test_cases = [
    # username, expected_status
    (  # 0 - creator User
        creator_username,
        status.HTTP_201_CREATED,
    ),
    (  # 1 - other User
        other_username,
        status.HTTP_404_NOT_FOUND,
    ),
]

status_200_or_404_test_cases = [
    # username, expected_status
    (  # 0 - creator User
        creator_username,
        status.HTTP_200_OK,
    ),
    (  # 1 - other User
        other_username,
        status.HTTP_404_NOT_FOUND,
    ),
]

status_204_or_404_test_cases = [
    # username, expected_status
    (  # 0 - creator User
        creator_username,
        status.HTTP_204_NO_CONTENT,
    ),
    (  # 1 - other User
        other_username,
        status.HTTP_404_NOT_FOUND,
    ),
]


brewnotes_endpoint = "/api/users/%s/recipes/{}/brewnotes/" % creator_username


class TestBrewNotes:
    """Tests for BrewNote API actions."""

    def setup_method(self):
        user = User.objects.create(username=creator_username, password="password")
        recipe = Recipe.objects.create(
            user=user, title="The Original", bean_name="Arabica"
        )
        brewnote = BrewNote.objects.create(recipe=recipe, body="Test Brewnote")
        self.brewnote_url = "{}{}/".format(
            brewnotes_endpoint.format(brewnote.recipe_id), brewnote.pk
        )

        User.objects.create(username=other_username, password="password")
        self.client = authenticate_user()

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_201_or_404_test_cases)
    def test_create_brewnote(self, username, expected_status):
        """Ensure only creator can create a new BrewNote object."""
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.first()
        url = brewnotes_endpoint.format(recipe.pk)
        brewnote_body = "A test brewnote"
        with pytest.raises(BrewNote.DoesNotExist):
            BrewNote.objects.get(body=brewnote_body)

        # Act
        response = self.client.post(url, {"body": brewnote_body})

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_201_CREATED:
            return
        assert BrewNote.objects.filter(body=brewnote_body).count() == 1

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_200_or_404_test_cases)
    def test_get_brewnote(self, username, expected_status):
        """Ensure only creator can read a BrewNote object."""
        # Arrange
        self.client = authenticate_user(username=username)
        brewnote = BrewNote.objects.first()

        # Act
        response = self.client.get(self.brewnote_url)

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_200_OK:
            return
        assert response.data["id"] == brewnote.pk

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_200_or_404_test_cases)
    def test_patch_brewnote(self, username, expected_status):
        """
        Ensure only creator can change a field in a BrewNote object.
        """
        # Arrange
        self.client = authenticate_user(username=username)
        brewnote = BrewNote.objects.first()
        new_body = "A new brewnote body"
        assert brewnote.body != new_body

        # Act
        response = self.client.patch(
            self.brewnote_url, {"body": new_body}, format="json"
        )

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_200_OK:
            return
        brewnote.refresh_from_db()
        assert brewnote.body == new_body

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_204_or_404_test_cases)
    def test_delete_brewnote(self, username, expected_status):
        """Ensure only creator can delete a BrewNote object."""
        # Arrange
        self.client = authenticate_user(username=username)
        brewnote = BrewNote.objects.first()

        # Act
        response = self.client.delete(self.brewnote_url)

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_204_NO_CONTENT:
            return
        with pytest.raises(BrewNote.DoesNotExist):
            BrewNote.objects.get(pk=brewnote.pk)
