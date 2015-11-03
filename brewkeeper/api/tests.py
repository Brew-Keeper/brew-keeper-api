# from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Recipe


# Create your tests here.

class AccountTests(APITestCase):

    def test_create_recipe(self):
        """
        Ensure we can create a new recipe object.
        """
        url = '/users/don.pablo/recipes'
        with open('api/testdata/recipe_user_input.json') as data:
            response = self.client.post(url, data={"title": "The Original"})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Recipe.objects.count(), 1)
            self.assertEqual(Recipe.objects.get().title, 'The Original')


    # def test_read_recipe(self):
    #     """
    #     Ensure we can update a recipe object.
    #     """
    #     url = '/users/don.pablo/recipes'
    #     with open('api/testdata/recipe_user_input.json') as data:
    #         response = self.client.get(url, data.read(), format='json')
    #         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #         self.assertEqual(Recipe.objects.count(), 1)
    #         self.assertEqual(Recipe.objects.get().orientation, 'Regular')


    def test_modify_recipe(self):
        """
        Ensure we can change a field in a recipe.
        """
        url = '/users/don.pablo/recipes/1/'
        with open('api/testdata/recipe_user_input.json') as data:
            response = self.client.patch(url, data.read(), format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Recipe.objects.count(), 1)
            self.assertEqual(Recipe.objects.get().bean_name, 'Robusto')
