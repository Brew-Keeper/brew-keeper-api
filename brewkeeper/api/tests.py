from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from .models import Recipe, BrewNote
from django.contrib.auth.models import User

recipe_endpoint = '/api/users/don.pablo/recipes/'


class RecipeTests(APITestCase):

    def setUp(self):
        user = User.objects.create(username='don.pablo', password='password')
        recipe = Recipe.objects.create(
            user=user,
            title="The Original",
            bean_name="Arabica")
        BrewNote.objects.create(recipe=recipe, body='Test Brewnote')

    def test_get_recipe(self):
        """
        Ensure we can read a recipe object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.first()
        url = "{}{}/".format(recipe_endpoint, recipe.pk)

        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], recipe.pk)

    def test_create_recipe(self):
        """
        Ensure we can create a new recipe object.
        """
        client = authenticate_user()

        response = client.post(recipe_endpoint, {"title": "The Impostor"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)
        self.assertEqual(
            Recipe.objects.filter(title='The Impostor').count(), 1)

    def test_delete_recipe(self):
        """
        Ensure we can delete a recipe object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.filter(title='The Original').first()
        url = "{}{}/".format(recipe_endpoint, recipe.pk)

        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_patch_recipe(self):
        """
        Ensure we can change a field in a recipe object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.filter(title='The Original').first()
        new_bean_name = 'Robusto'
        self.assertNotEqual(recipe.bean_name, new_bean_name)
        url = "{}{}/".format(recipe_endpoint, recipe.pk)

        response = client.patch(
            url,
            {'bean_name': new_bean_name},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.bean_name, new_bean_name)

    def test_create_brewnote(self):
        """
        Ensure we can create a new brewnote object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.first()
        url = "{}{}/brewnotes/".format(recipe_endpoint, recipe.pk)
        brewnote_body = 'A test brewnote'
        self.assertEqual(
            recipe.brewnotes.filter(body=brewnote_body).first(), None)

        response = client.post(url, {'body': brewnote_body})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(
            recipe.brewnotes.filter(body=brewnote_body).first(), None)

    def test_get_brewnote(self):
        """
        Ensure we can read a brewnote object.
        """
        client = authenticate_user()
        brewnote = BrewNote.objects.first()
        url = "{}{}/brewnotes/{}/".format(
            recipe_endpoint, brewnote.recipe_id, brewnote.pk)

        response = client.get(url)

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
        url = "{}{}/brewnotes/{}/".format(
            recipe_endpoint, brewnote.recipe_id, brewnote.pk)

        response = client.patch(url, {'body': new_body}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        brewnote.refresh_from_db()
        self.assertEqual(brewnote.body, new_body)

    def test_delete_brewnote(self):
        """
        Ensure we can delete a brewnote object.
        """
        client = authenticate_user()
        brewnote = BrewNote.objects.first()
        url = "{}{}/brewnotes/{}/".format(
            recipe_endpoint, brewnote.recipe_id, brewnote.pk)

        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BrewNote.objects.count(), 0)


def authenticate_user(username='don.pablo'):
    user = User.objects.get(username=username)
    client = APIClient()
    client.force_authenticate(user=user)
    return client
