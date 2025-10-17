"""Tests for BrewNotes."""

from django.contrib.auth.models import User
import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.models import BrewNote, Recipe

from .helpers import authenticate_user

brewnotes_endpoint = "/api/users/donpablo/recipes/{}/brewnotes/"


class BrewNoteTests(APITestCase):
    """Tests for BrewNotes."""

    def setUp(self):
        user = User.objects.create(username="donpablo", password="password")
        recipe = Recipe.objects.create(
            user=user, title="The Original", bean_name="Arabica"
        )
        brewnote = BrewNote.objects.create(recipe=recipe, body="Test Brewnote")
        self.brewnote_url = "{}{}/".format(
            brewnotes_endpoint.format(brewnote.recipe_id), brewnote.pk
        )
        self.client = authenticate_user()

    def test_create_brewnote(self):
        """Ensure we can create a new BrewNote object."""
        recipe = Recipe.objects.first()
        url = brewnotes_endpoint.format(recipe.pk)
        brewnote_body = "A test brewnote"
        with pytest.raises(BrewNote.DoesNotExist):
            BrewNote.objects.get(body=brewnote_body)

        response = self.client.post(url, {"body": brewnote_body})

        assert response.status_code == status.HTTP_201_CREATED
        assert BrewNote.objects.filter(body=brewnote_body).count() == 1

    def test_get_brewnote(self):
        """Ensure we can read a BrewNote object."""
        brewnote = BrewNote.objects.first()

        response = self.client.get(self.brewnote_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == brewnote.pk

    def test_patch_brewnote(self):
        """Ensure we can change a field in a BrewNote object."""
        brewnote = BrewNote.objects.first()
        new_body = "A new brewnote body"
        assert brewnote.body != new_body

        response = self.client.patch(
            self.brewnote_url, {"body": new_body}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        brewnote.refresh_from_db()
        assert brewnote.body == new_body

    def test_delete_brewnote(self):
        """Ensure we can delete a BrewNote object."""
        brewnote = BrewNote.objects.first()

        response = self.client.delete(self.brewnote_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(BrewNote.DoesNotExist):
            BrewNote.objects.get(pk=brewnote.pk)
