# from django.test import TestCase
# from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Recipe, BrewNote
from django.contrib.auth.models import User


# Create your tests here.

class RecipeTests(APITestCase):

    def setUp(self):
        user = User.objects.create(username='don.pablo', password='password')
        recipe = Recipe.objects.create(user=user, title="The Original", bean_name="Arabica")
        BrewNote.objects.create(recipe=recipe, body='Test Brewnote')

        # Include an appropriate `Authorization:` header on all requests.
        # token = Token.objects.get(user__username='don.pablo')
        # client = APIClient()
        # client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


    def test_get_recipe(self):
        """
        Ensure we can read a recipe object.
        """
        client = authenticate_user()
        orig_recipe = Recipe.objects.filter(title='The Original')
        orig_url = '/api/users/don.pablo/recipes/' + str(orig_recipe[0].pk) + '/'
        response = client.get(orig_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'The Original')

    def test_create_recipe(self):
        """
        Ensure we can create a new recipe object.
        """
        client = authenticate_user()
        url = '/api/users/don.pablo/recipes/'
        response = client.post(url, {"title": "The Impostor"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)
        posted_recipe = Recipe.objects.filter(title='The Impostor')
        self.assertEqual(posted_recipe[0].title, 'The Impostor')

    def test_delete_recipe(self):
        """
        Ensure we can delete a recipe object.
        """
        client = authenticate_user()
        orig_recipe = Recipe.objects.filter(title='The Original')
        orig_url = '/api/users/don.pablo/recipes/' + str(orig_recipe[0].pk) + '/'
        response = client.delete(orig_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_patch_recipe(self):
        """
        Ensure we can change a field in a recipe object.
        """
        client = authenticate_user()
        orig_recipe = Recipe.objects.filter(title='The Original')
        orig_url = '/api/users/don.pablo/recipes/' + str(orig_recipe[0].pk) + '/'
        response = client.patch(orig_url,
                                {'bean_name': 'Robusto'},
                                format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(orig_recipe[0].bean_name, 'Robusto')

    def test_create_brewnote(self):
        """
        Ensure we can create a new brewnote object.
        """
        client = authenticate_user()
        parent_recipe = Recipe.objects.filter(title='The Original')[0]
        brew_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                   '/brewnotes/'
        response = client.post(brew_url, {'body': 'A test brewnote'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        posted_brewnote = parent_recipe.brewnotes.filter(body='A test brewnote')
        self.assertEqual(posted_brewnote[0].body, 'A test brewnote')

    def test_get_brewnote(self):
        """
        Ensure we can read a brewnote object.
        """
        client = authenticate_user()
        parent_recipe = Recipe.objects.filter(title='The Original')[0]
        brewnotes = parent_recipe.brewnotes.all()
        brewnote_id = str(brewnotes[0].pk)
        brew_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                   '/brewnotes/' + brewnote_id + '/'
        response = client.get(brew_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['body'], 'Test Brewnote')

    def test_get_brewnote(self):
        """
        Ensure we can read a brewnote object.
        """
        parent_recipe = Recipe.objects.filter(title='The Original')[0]
        brewnotes = parent_recipe.brewnotes.all()
        brewnote_id = str(brewnotes[0].pk)
        brew_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                   '/brewnotes/' + brewnote_id + '/'
        response = self.client.get(brew_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['body'], 'Test Brewnote')


    def test_patch_brewnote(self):
        """
        Ensure we can change a field in a brewnote object.
        """
        client = authenticate_user()
        parent_recipe = Recipe.objects.filter(title='The Original')
        parent_recipe = parent_recipe[0]
        brewnotes = parent_recipe.brewnotes.all()
        brewnote_id = str(brewnotes[0].pk)
        brew_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                   '/brewnotes/' + brewnote_id + '/'
        response = client.patch(brew_url,
                                {'body': 'A test brewnote'},
                                format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recipe.objects.count(), 1)
        posted_brewnote = parent_recipe.brewnotes.filter(body='A test brewnote')
        self.assertEqual(posted_brewnote[0].body, 'A test brewnote')


    def test_delete_brewnote(self):
        """
        Ensure we can delete a brewnote object.
        """
        client = authenticate_user()
        parent_recipe = Recipe.objects.filter(title='The Original')[0]
        brewnotes = parent_recipe.brewnotes.all()
        brewnote_id = str(brewnotes[0].pk)
        brew_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                   '/brewnotes/' + brewnote_id + '/'
        response = self.client.delete(brew_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_create_comment(self):
        """
        Ensure we can create a new comment object.
        """
        parent_recipe = Recipe.objects.filter(title='The Original')[0]
        comment_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                      '/comments/'
        response = self.client.post(comment_url, {'body': 'A test comment'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        posted_comment = parent_recipe.public_comment.filter(body='A test comment')
        self.assertEqual(posted_comment[0].body, 'A test comment')


    def test_get_comment(self):
        """
        Ensure we can read a comment object.
        """
        parent_recipe = Recipe.objects.filter(title='The Original')[0]
        comment = parent_recipe.public_comment.all()
        comment_id = str(comment[0].pk)
        comment_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                      '/comments/' + comment_id + '/'
        response = self.client.get(comment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['public_comment'], 'A test comment')


    def test_patch_comment(self):
        """
        Ensure we can change a field in a comment object.
        """
        parent_recipe = Recipe.objects.filter(title='The Original')
        parent_recipe = parent_recipe[0]
        comment = parent_recipe.public_comment.all()
        comment_id = str(comment[0].pk)
        comment_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                      '/comments/' + comment_id + '/'
        response = self.client.patch(brew_url,
                                     {'body': 'A test comment'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recipe.objects.count(), 1)
        posted_comment = parent_recipe.public_comment.filter(body='A test comment')
        self.assertEqual(posted_comment[0].body, 'A test comment')


    def test_delete_comment(self):
        """
        Ensure we can delete a comment object.
        """
        parent_recipe = Recipe.objects.filter(title='The Original')[0]
        comment = parent_recipe.public_comment.all()
        comment_id = str(comment[0].pk)
        comment_url = '/api/users/don.pablo/recipes/' + str(parent_recipe.pk) + \
                      '/comments/' + comment_id + '/'
        response = self.client.delete(comment_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = client.delete(brew_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


def authenticate_user(username='don.pablo'):
    user = User.objects.get(username=username)
    client = APIClient()
    client.force_authenticate(user=user)
    return client
