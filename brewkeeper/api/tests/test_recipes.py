"""Tests for Recipe API actions."""

from django.contrib.auth.models import User
import pytest
from rest_framework import status

from api.models import Recipe

from .helpers import authenticate_user

creator_username = "donpablo"
other_username = "not_the_creator"


recipes_endpoint = f"/api/users/{creator_username}/recipes/"


class TestRecipes:
    """Tests for Recipe API actions."""

    def setup_method(self):
        user = User.objects.create(username="donpablo", password="password")
        recipe = Recipe.objects.create(
            user=user, title="The Original", bean_name="Arabica"
        )
        self.recipe_url = "{}{}/".format(recipes_endpoint, recipe.pk)
        self.client = authenticate_user()

    @pytest.mark.django_db
    def test_create_recipe(self):
        """Ensure we can create a new Recipe object."""
        # Arrange
        title = "The Impostor"
        with pytest.raises(Recipe.DoesNotExist):
            Recipe.objects.get(title=title)

        # Act
        response = self.client.post(recipes_endpoint, {"title": title})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.filter(title=title).count() == 1

    @pytest.mark.django_db
    def test_get_recipe(self):
        """Ensure we can read a Recipe object."""
        # Arrange
        recipe = Recipe.objects.first()

        # Act
        response = self.client.get(self.recipe_url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == recipe.pk

    @pytest.mark.django_db
    def test_patch_recipe(self):
        """Ensure we can change a field in a Recipe object."""
        # Arrange
        recipe = Recipe.objects.get(title="The Original")
        new_bean_name = "Robusto"
        assert recipe.bean_name != new_bean_name

        # Act
        response = self.client.patch(
            self.recipe_url, {"bean_name": new_bean_name}, format="json"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        recipe.refresh_from_db()
        assert recipe.bean_name == new_bean_name

    @pytest.mark.django_db
    def test_delete_recipe(self):
        """Ensure we can delete a Recipe object."""
        # Arrange
        recipe = Recipe.objects.get(title="The Original")

        # Act
        response = self.client.delete(self.recipe_url)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        with pytest.raises(Recipe.DoesNotExist):
            Recipe.objects.get(pk=recipe.pk)
