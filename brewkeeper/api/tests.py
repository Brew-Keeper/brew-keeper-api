# from django.test import TestCase
# from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Recipe


# Create your tests here.

class RecipeTests(APITestCase):

    def setUp(self):
        Recipe.objects.create(title="The Original", bean_name="Arabica")

    def test_create_recipe(self):
        """
        Ensure we can create a new recipe object.
        """
        url = '/api/users/don.pablo/recipes/'
        print("Number is: {}".format(Recipe.objects.count()))
        response = self.client.post(url, {"title": "The Impostor"})  # , "bean_name": "Arabica"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Number is: {}".format(Recipe.objects.count()))
        self.assertEqual(Recipe.objects.count(), 2)
        posted_recipe = Recipe.objects.filter(title='The Impostor')
        self.assertEqual(posted_recipe.title, 'The Impostor')


    def test_patch_recipe(self):
        """
        Ensure we can change a field in a recipe.
        """
        # url = '/api/users/don.pablo/recipes/1/'
        # with open('api/testdata/recipe_user_input.json') as data:
        response = self.client.patch('/api/users/don.pablo/recipes/1/', data={"bean_name": "Robusto"})
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Recipe.objects.get().bean_name, 'Robusto')


    def test_read_recipe(self):
        """
        Ensure we can read a recipe object.
        """
        url = '/api/users/don.pablo/recipes/1/'
        # with open('api/testdata/recipe_user_input.json') as data:
        response = self.client.get(url, orientation="Regular")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Recipe.objects.get().orientation, 'Regular')
