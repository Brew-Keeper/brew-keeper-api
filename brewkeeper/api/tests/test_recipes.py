from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .helpers import authenticate_user
from api.models import Recipe

recipes_endpoint = '/api/users/don.pablo/recipes/'


class RecipeTests(APITestCase):

    def setUp(self):
        user = User.objects.create(username='don.pablo', password='password')
        recipe = Recipe.objects.create(
            user=user,
            title="The Original",
            bean_name="Arabica")
        self.recipe_url = "{}{}/".format(recipes_endpoint, recipe.pk)

    def test_create_recipe(self):
        """
        Ensure we can create a new recipe object.
        """
        client = authenticate_user()
        title = "The Impostor"
        with self.assertRaises(Recipe.DoesNotExist):
            Recipe.objects.get(title=title)

        response = client.post(recipes_endpoint, {"title": title})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.filter(title=title).count(), 1)

    def test_get_recipe(self):
        """
        Ensure we can read a recipe object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.first()

        response = client.get(self.recipe_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], recipe.pk)

    def test_patch_recipe(self):
        """
        Ensure we can change a field in a recipe object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.get(title='The Original')
        new_bean_name = 'Robusto'
        self.assertNotEqual(recipe.bean_name, new_bean_name)

        response = client.patch(
            self.recipe_url,
            {'bean_name': new_bean_name},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.bean_name, new_bean_name)

    def test_delete_recipe(self):
        """
        Ensure we can delete a recipe object.
        """
        client = authenticate_user()
        recipe = Recipe.objects.get(title='The Original')

        response = client.delete(self.recipe_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Recipe.DoesNotExist):
            Recipe.objects.get(pk=recipe.pk)
