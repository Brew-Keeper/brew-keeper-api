from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from .helpers import authenticate_user
from api.models import Step, Recipe

steps_endpoint = "/api/users/don.pablo/recipes/{}/steps/"


def step_url(step):
    return "{}{}/".format(steps_endpoint.format(step.recipe_id), step.pk)


class StepTests(APITestCase):

    def setUp(self):
        user = User.objects.create(username="don.pablo", password="password")
        recipe = Recipe.objects.create(
            user=user, title="The Original", bean_name="Arabica"
        )
        Step.objects.create(
            recipe=recipe, duration=10, step_number=1, step_title="Step 1"
        )
        self.client = authenticate_user()

    def test_create_step(self):
        """Ensure we can create a new Step object."""
        recipe = Recipe.objects.first()
        url = steps_endpoint.format(recipe.pk)
        self.assertEqual(recipe.steps.count(), 1)

        response = self.client.post(
            url,
            {
                "duration": 12,
                "step_number": 2,
                "step_title": "Step 2",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe.steps.count(), 2)

    def test_create_reorders_step(self):
        """Ensure new Step with duplicate step_number reorders the others."""
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.steps.count(), 1)
        first_step = recipe.steps.first()
        middle_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=2, step_title="Step 2"
        )
        end_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=3, step_title="Step 3"
        )
        url = steps_endpoint.format(recipe.pk)

        response = self.client.post(
            url,
            {
                "duration": 12,
                "step_number": 2,
                "step_title": "New Step 2",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        first_step.refresh_from_db()
        middle_step.refresh_from_db()
        end_step.refresh_from_db()
        self.assertEqual(first_step.step_number, 1)
        self.assertEqual(middle_step.step_number, 3)
        self.assertEqual(end_step.step_number, 4)

    def test_get_step(self):
        """Ensure we can read a Step object."""
        step = Step.objects.first()

        response = self.client.get(step_url(step))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], step.pk)

    def test_patch_step(self):
        """Ensure we can change a field in a Step object."""
        step = Step.objects.first()
        new_duration = 18
        self.assertNotEqual(step.duration, new_duration)

        response = self.client.patch(
            step_url(step),
            {"duration": new_duration, "step_number": 1, "step_title": "Step 1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        step.refresh_from_db()
        self.assertEqual(step.duration, new_duration)

    def test_patch_reorders_step(self):
        """Ensure Steps reorder when patched step_number overlaps existing."""
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.steps.count(), 1)
        first_step = recipe.steps.first()
        self.assertEqual(first_step.step_number, 1)
        middle_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=2, step_title="Step 2"
        )
        end_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=3, step_title="Step 3"
        )

        response = self.client.patch(
            step_url(middle_step),
            {"duration": 10, "step_number": 1, "step_title": "Was Step 2"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_step.refresh_from_db()
        middle_step.refresh_from_db()
        end_step.refresh_from_db()
        self.assertEqual(first_step.step_number, 2)
        self.assertEqual(middle_step.step_number, 1)
        self.assertEqual(end_step.step_number, 3)

    def test_delete_step(self):
        """Ensure we can delete a Step object."""
        step = Step.objects.first()

        response = self.client.delete(step_url(step))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Step.DoesNotExist):
            Step.objects.get(pk=step.pk)

    def test_delete_middle_step(self):
        """Ensure deleting a middle Step properly reorders remaining."""
        recipe = Recipe.objects.first()
        middle_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=2, step_title="Step 2"
        )
        end_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=3, step_title="Step 3"
        )

        response = self.client.delete(step_url(middle_step))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        end_step.refresh_from_db()
        self.assertEqual(end_step.step_number, 2)
