from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.db.models import Recipe


# Create your tests here.

class AccountTests(APITestCase):
    def test_create_recipe(self):
        """
        Ensure we can create a new recipe object.
        """
        url = reverse('recipe-list')
        with open('recipe_user_input.json') as data:
            response = self.client.post(url, data.read(), format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Recipe.objects.count(), 1)
            self.assertEqual(Recipe.objects.get().title, 'The Original')

    def test_modify_recipe(self):
        """
        Ensure we can change a field in a recipe.
        """
        url = reverse('recipe-list')
        with open('recipe_user_input.json') as data:
            response = self.client.patch(url, data.read(), format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(Recipe.objects.count(), 1)
            self.assertEqual(Recipe.objects.get().bean_name, 'Robusto')
