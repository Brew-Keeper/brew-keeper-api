from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .helpers import authenticate_user
from api.models import Recipe, BrewNote

brewnotes_endpoint = '/api/users/don.pablo/recipes/{}/brewnotes/'


def brewnote_url(brewnote):
    return '/api/users/don.pablo/recipes/{}/brewnotes/{}/'.format(
        brewnote.recipe_id, brewnote.pk)


class BrewNoteTests(APITestCase):

    def setUp(self):
        user = User.objects.create(username='don.pablo', password='password')
        recipe = Recipe.objects.create(
            user=user,
            title="The Original",
            bean_name="Arabica")
        BrewNote.objects.create(recipe=recipe, body='Test Brewnote')

    def test_create_brewnote(self):
        """
        Ensure we can create a new brewnote object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.first()
        url = brewnotes_endpoint.format(recipe.pk)
        brewnote_body = 'A test brewnote'
        with self.assertRaises(BrewNote.DoesNotExist):
            BrewNote.objects.get(body=brewnote_body)

        response = client.post(url, {'body': brewnote_body})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            BrewNote.objects.filter(body=brewnote_body).count(), 1)

    def test_get_brewnote(self):
        """
        Ensure we can read a brewnote object.
        """
        client = authenticate_user()
        brewnote = BrewNote.objects.first()

        response = client.get(brewnote_url(brewnote))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], brewnote.pk)

    def test_patch_brewnote(self):
        """
        Ensure we can change a field in a brewnote object.
        """
        client = authenticate_user()
        brewnote = BrewNote.objects.first()
        new_body = 'A new brewnote body'
        self.assertNotEqual(brewnote.body, new_body)

        response = client.patch(
            brewnote_url(brewnote), {'body': new_body}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        brewnote.refresh_from_db()
        self.assertEqual(brewnote.body, new_body)

    def test_delete_brewnote(self):
        """
        Ensure we can delete a brewnote object.
        """
        client = authenticate_user()
        brewnote = BrewNote.objects.first()

        response = client.delete(brewnote_url(brewnote))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(BrewNote.DoesNotExist):
            BrewNote.objects.get(pk=brewnote.pk)
