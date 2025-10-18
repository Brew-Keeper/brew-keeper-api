"""Tests for Recipe API actions."""

from django.contrib.auth.models import User
import pytest
from rest_framework import status

from api.models import Recipe
from api.serializers import RecipeDetailSerializer
from api.tests.helpers import authenticate_user

########################################
# Parametrize Test Case Definitions
########################################

creator_username = "donpablo"
other_username = "not_the_creator"

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


recipes_endpoint = f"/api/users/{creator_username}/recipes/"


class TestRecipes:
    """Tests for Recipe API actions."""

    def setup_method(self):
        user = User.objects.create(username="donpablo", password="password")
        recipe = Recipe.objects.create(
            user=user, title="The Original", bean_name="Arabica"
        )
        self.recipe_url = "{}{}/".format(recipes_endpoint, recipe.pk)

        User.objects.create(username=other_username, password="password")

    @pytest.mark.django_db
    def test_create_recipe(self):
        """Ensure we can create a new Recipe object."""
        # Arrange
        self.client = authenticate_user(username=creator_username)
        title = "The Impostor"
        with pytest.raises(Recipe.DoesNotExist):
            Recipe.objects.get(title=title)

        # Act
        response = self.client.post(recipes_endpoint, {"title": title})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.filter(title=title).count() == 1
        assert list(response.json().keys()) == [*RecipeDetailSerializer.Meta.fields]

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_200_or_404_test_cases)
    def test_get_recipe(self, username, expected_status):
        """Ensure only creator can read a Recipe object."""
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.first()

        # Act
        response = self.client.get(self.recipe_url)

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_200_OK:
            return
        assert response.data["id"] == recipe.pk

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_200_or_404_test_cases)
    def test_patch_recipe(self, username, expected_status):
        """Ensure only creator can change a field in a Recipe object."""
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.get(title="The Original")
        new_bean_name = "Robusto"
        assert recipe.bean_name != new_bean_name

        # Act
        response = self.client.patch(
            self.recipe_url, {"bean_name": new_bean_name}, format="json"
        )

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_200_OK:
            return
        recipe.refresh_from_db()
        assert recipe.bean_name == new_bean_name

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_204_or_404_test_cases)
    def test_delete_recipe(self, username, expected_status):
        """Ensure only creator can delete a Recipe object."""
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.get(title="The Original")

        # Act
        response = self.client.delete(self.recipe_url)

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_204_NO_CONTENT:
            return
        with pytest.raises(Recipe.DoesNotExist):
            Recipe.objects.get(pk=recipe.pk)
