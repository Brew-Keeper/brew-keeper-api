"""Tests for Step API actions."""

from django.contrib.auth.models import User
import pytest
from rest_framework import status

from api.models import Recipe, Step

from .helpers import authenticate_user

########################################
# Parametrize Test Case Definitions
########################################

creator_username = "donpablo"
other_username = "not_the_creator"

status_201_or_404_test_cases = [
    # username, expected_status
    (  # 0 - creator User
        creator_username,
        status.HTTP_201_CREATED,
    ),
    (  # 1 - other User
        other_username,
        status.HTTP_404_NOT_FOUND,
    ),
]

status_200_or_404_test_cases = [
    # username, expected_status
    (  # 0 - creator User
        creator_username,
        status.HTTP_200_OK,
    ),
    (  # 1 - other User
        other_username,
        status.HTTP_404_NOT_FOUND,
    ),
]

status_204_or_404_test_cases = [
    # username, expected_status
    (  # 0 - creator User
        creator_username,
        status.HTTP_204_NO_CONTENT,
    ),
    (  # 1 - other User
        other_username,
        status.HTTP_404_NOT_FOUND,
    ),
]


steps_endpoint = "/api/users/%s/recipes/{}/steps/" % creator_username


def step_url(step):
    return "{}{}/".format(steps_endpoint.format(step.recipe_id), step.pk)


class TestSteps:
    """Tests for Step API actions."""

    def setup_method(self):
        user = User.objects.create(username=creator_username, password="password")
        recipe = Recipe.objects.create(
            user=user, title="The Original", bean_name="Arabica"
        )
        Step.objects.create(
            recipe=recipe, duration=10, step_number=1, step_title="Step 1"
        )

        User.objects.create(username=other_username, password="password")

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_201_or_404_test_cases)
    def test_create_step(self, username, expected_status):
        """Ensure only creator can create a new Step object."""
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.first()
        url = steps_endpoint.format(recipe.pk)
        assert recipe.steps.count() == 1

        # Act
        response = self.client.post(
            url,
            {
                "duration": 12,
                "step_number": 2,
                "step_title": "Step 2",
            },
        )

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_201_CREATED:
            return
        assert recipe.steps.count() == 2

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_201_or_404_test_cases)
    def test_create_reorders_step(self, username, expected_status):
        """
        Ensure new Step with duplicate step_number reorders the others.

        Creator only!
        """
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.first()
        assert recipe.steps.count() == 1
        first_step = recipe.steps.first()
        middle_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=2, step_title="Step 2"
        )
        end_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=3, step_title="Step 3"
        )
        url = steps_endpoint.format(recipe.pk)

        # Act
        response = self.client.post(
            url,
            {
                "duration": 12,
                "step_number": 2,
                "step_title": "New Step 2",
            },
        )

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_201_CREATED:
            return
        first_step.refresh_from_db()
        middle_step.refresh_from_db()
        end_step.refresh_from_db()
        assert first_step.step_number == 1
        assert middle_step.step_number == 3
        assert end_step.step_number == 4

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_200_or_404_test_cases)
    def test_get_step(self, username, expected_status):
        """Ensure only creator can read a Step object."""
        # Arrange
        self.client = authenticate_user(username=username)
        step = Step.objects.first()

        # Act
        response = self.client.get(step_url(step))

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_200_OK:
            return
        assert response.data["id"] == step.pk

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_200_or_404_test_cases)
    def test_patch_reorders_step(self, username, expected_status):
        """
        Ensure Steps reorder when patched step_number overlaps existing.

        Creator only!
        """
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.first()
        assert recipe.steps.count() == 1
        first_step = recipe.steps.first()
        assert first_step.step_number == 1
        middle_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=2, step_title="Step 2"
        )
        end_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=3, step_title="Step 3"
        )

        # Act
        response = self.client.patch(
            step_url(middle_step),
            {"duration": 10, "step_number": 1, "step_title": "Was Step 2"},
            format="json",
        )

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_200_OK:
            return
        first_step.refresh_from_db()
        middle_step.refresh_from_db()
        end_step.refresh_from_db()
        assert first_step.step_number == 2
        assert middle_step.step_number == 1
        assert end_step.step_number == 3

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_204_or_404_test_cases)
    def test_delete_step(self, username, expected_status):
        """Ensure only creator can delete a Step object."""
        # Arrange
        self.client = authenticate_user(username=username)
        step = Step.objects.first()

        # Act
        response = self.client.delete(step_url(step))

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_204_NO_CONTENT:
            return
        with pytest.raises(Step.DoesNotExist):
            Step.objects.get(pk=step.pk)

    @pytest.mark.django_db
    @pytest.mark.parametrize("username, expected_status", status_204_or_404_test_cases)
    def test_delete_middle_step(self, username, expected_status):
        """
        Ensure deleting a middle Step properly reorders remaining.

        Creator only!
        """
        # Arrange
        self.client = authenticate_user(username=username)
        recipe = Recipe.objects.first()
        middle_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=2, step_title="Step 2"
        )
        end_step = Step.objects.create(
            recipe=recipe, duration=10, step_number=3, step_title="Step 3"
        )

        # Act
        response = self.client.delete(step_url(middle_step))

        # Assert
        assert response.status_code == expected_status
        if expected_status != status.HTTP_204_NO_CONTENT:
            return
        end_step.refresh_from_db()
        assert end_step.step_number == 2
