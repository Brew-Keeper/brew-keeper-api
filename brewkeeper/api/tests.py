# from django.test import TestCase
# from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Recipe


# Create your tests here.

class RecipeTests(APITestCase):

    def setUp(self):
        Recipe.objects.create(title="The Original", bean_name="Arabica")

    def test_read_recipe(self):
        """
        Ensure we can read a recipe object.
        """
        orig_recipe = Recipe.objects.filter(title='The Original')
        orig_url = '/api/users/don.pablo/recipes/' + str(orig_recipe[0].pk) + '/'
        response = self.client.get(orig_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'The Original')


    def test_create_recipe(self):
        """
        Ensure we can create a new recipe object.
        """
        url = '/api/users/don.pablo/recipes/'
        response = self.client.post(url, {"title": "The Impostor"})  # , "bean_name": "Arabica"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)
        posted_recipe = Recipe.objects.filter(title='The Impostor')
        self.assertEqual(posted_recipe[0].title, 'The Impostor')


    def test_patch_recipe(self):
        """
        Ensure we can change a field in a recipe.
        """
        orig_recipe = Recipe.objects.filter(title='The Original')
        orig_url = '/api/users/don.pablo/recipes/' + str(orig_recipe[0].pk) + '/'
        response = self.client.patch(orig_url,
                                     {'bean_name': 'Robusto'},
                                     format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(orig_recipe[0].bean_name, 'Robusto')
