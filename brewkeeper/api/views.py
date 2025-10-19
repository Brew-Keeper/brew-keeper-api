"""
The views for the BrewKeeper API app.

This has all of the custom classes and functions used by the urls.py
endpoints.
"""

import random
import re

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg, Sum
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
import requests
from rest_framework import filters, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api import serializers as api_serializers
from api.exceptions import IntegrationError
from api.models import BrewNote, PublicComment, PublicRating, Recipe, Step, UserInfo


class RecipeViewSet(viewsets.ModelViewSet):
    """The class controlling views of Recipes."""

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = (
        "title",
        "bean_name",
        "roast",
        "steps__step_body",
        "brewnotes__body",
        "=shared_by",
    )
    ordering_fields = ("rating", "brew_count", "created_on")
    permission_classes = []

    def get_queryset(self):  # noqa
        if (
            self.kwargs["user_username"] == "public"
            and self.request.method in permissions.SAFE_METHODS
        ):
            user = User.objects.get(username="public")
            self.request.user = user
            return user.recipes.all().prefetch_related(
                "public_comments", "public_ratings", "steps"
            )
        return self.request.user.recipes.all().prefetch_related("steps", "brewnotes")

    def get_serializer_context(self):  # noqa
        context = super().get_serializer_context().copy()
        if self.kwargs["user_username"] == "public" and self.request.method == "POST":
            context["username"] = "public"
        else:
            context["username"] = self.request.user.username
        return context

    def get_serializer_class(self):  # noqa
        if self.kwargs["user_username"] == "public":
            if self.action == "list":
                return api_serializers.PublicRecipeListSerializer
            return api_serializers.PublicRecipeDetailSerializer
        if self.action == "list":
            return api_serializers.RecipeListSerializer
        return api_serializers.RecipeDetailSerializer


class StepViewSet(viewsets.ModelViewSet):
    """The class controlling views of Steps."""

    permission_classes = []
    serializer_class = api_serializers.StepSerializer

    def get_queryset(self):  # noqa
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        if (
            recipe.user.username == "public"
            and self.kwargs["user_username"] == "public"
        ) or recipe.user == self.request.user:
            return Step.objects.all().filter(recipe=recipe)
        raise Http404

    def get_serializer_context(self):  # noqa
        context = super().get_serializer_context().copy()
        context["recipe_id"] = self.kwargs["recipe_pk"]
        return context

    @transaction.atomic
    def perform_create(self, serializer: api_serializers.StepSerializer):
        """Update total duration and rearrange steps if necessary"""
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        if recipe.user != self.request.user:
            raise Http404
        existing_steps = recipe.steps.all().order_by("step_number")

        overlap = False
        for step in existing_steps:
            if step.step_number == int(serializer.initial_data["step_number"]):
                overlap = True
            if overlap:
                step.step_number += 1
                step.save()

        serializer.save()
        total = recipe.steps.aggregate(Sum("duration"))
        recipe.total_duration = total["duration__sum"]
        recipe.save()

    @transaction.atomic
    def perform_update(self, serializer: api_serializers.StepSerializer):
        """Rearrange steps if necessary."""
        instance = self.get_object()
        if instance.recipe.user != self.request.user:
            raise Http404
        new_step_num = int(serializer.initial_data["step_number"])
        if instance.step_number != new_step_num:
            curr_steps = instance.recipe.steps.all().order_by("step_number")
            overlap = False

            # If new num is lower, + 1 to all steps between it an new val
            if new_step_num < instance.step_number:
                for step in curr_steps:
                    if step.step_number == new_step_num:
                        overlap = True
                    if overlap and step.step_number < instance.step_number:
                        step.step_number += 1
                        step.save()

            # If new num is bigger, - 1 from all steps between it and new val
            if new_step_num > instance.step_number:
                for step in curr_steps[::-1]:
                    if step.step_number == new_step_num:
                        overlap = True
                    if overlap and step.step_number > instance.step_number:
                        step.step_number -= 1
                        step.save()

        serializer.save()
        total = instance.recipe.steps.aggregate(Sum("duration"))
        instance.recipe.total_duration = total["duration__sum"]
        instance.recipe.save()

    @transaction.atomic
    def perform_destroy(self, instance: Step):  # noqa
        if instance.recipe.user != self.request.user:
            raise Http404
        curr_steps = instance.recipe.steps.all().order_by("step_number")
        for step in curr_steps:
            if step.step_number > instance.step_number:
                step.step_number -= 1
                step.save()

        new_total = instance.recipe.total_duration - instance.duration
        if new_total < 0:
            instance.recipe.total_duration = 0
        else:
            instance.recipe.total_duration = new_total
        instance.recipe.save()
        instance.delete()


class BrewNoteViewSet(viewsets.ModelViewSet):
    """The class controlling views of BrewNotes."""

    serializer_class = api_serializers.BrewNoteSerializer

    def get_queryset(self):  # noqa
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        if recipe.user == self.request.user:
            return BrewNote.objects.all().filter(recipe=recipe)
        raise Http404

    def get_serializer_context(self):  # noqa
        context = super().get_serializer_context().copy()
        context["recipe_id"] = self.kwargs["recipe_pk"]
        return context

    def perform_create(self, serializer: api_serializers.BrewNoteSerializer):
        """
        Ensure only authorized users can create BrewNotes.
        """
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        if recipe.user != self.request.user:
            raise Http404
        super().perform_create(serializer)


class PublicRatingViewSet(viewsets.ModelViewSet):
    """The class controlling views of PublicRatings."""

    serializer_class = api_serializers.PublicRatingSerializer

    def get_queryset(self):  # noqa
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        return PublicRating.objects.filter(recipe=recipe, user=self.request.user)

    def get_serializer_context(self):  # noqa
        context = super().get_serializer_context().copy()
        context["recipe_id"] = self.kwargs["recipe_pk"]
        context["username"] = self.request.user.username
        return context

    @transaction.atomic
    def perform_create(self, serializer: api_serializers.PublicRatingSerializer):
        """
        Create public rating, then update the public average rating.
        """
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        serializer.initial_data["user"] = self.request.user
        serializer.save()
        rating_calc = recipe.public_ratings.aggregate(Avg("public_rating"))
        recipe.average_rating = rating_calc["public_rating__avg"]
        recipe.save()

    @transaction.atomic
    def perform_update(self, serializer: api_serializers.PublicRatingSerializer):
        """
        Update public rating, then update the public average rating.
        """
        serializer.save()
        instance = self.get_object()
        rating_calc = instance.recipe.public_ratings.aggregate(Avg("public_rating"))
        instance.recipe.average_rating = rating_calc["public_rating__avg"]
        instance.recipe.save()

    @transaction.atomic
    def perform_destroy(self, instance: BrewNote):
        """
        Delete public rating, then update the public average rating.
        """
        recipe = instance.recipe
        instance.delete()
        rating_calc = recipe.public_ratings.aggregate(Avg("public_rating"))
        recipe.average_rating = rating_calc["public_rating__avg"]
        recipe.save()


class PublicCommentViewSet(viewsets.ModelViewSet):
    """The class controlling views of PublicComments."""

    serializer_class = api_serializers.PublicCommentSerializer

    def get_queryset(self):  # noqa
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        return PublicComment.objects.all().filter(recipe=recipe)

    def get_serializer_context(self):  # noqa
        context = super().get_serializer_context().copy()
        context["recipe_id"] = self.kwargs["recipe_pk"]
        context["username"] = self.request.user.username
        return context

    def perform_create(self, serializer: api_serializers.PublicCommentSerializer):  # noqa
        serializer.validated_data["user"] = self.request.user
        serializer.save()


class UserViewSet(viewsets.GenericViewSet):
    """The class controlling views of Users."""

    serializer_class = api_serializers.UserSerializer
    lookup_field = "username"

    def get_queryset(self):  # noqa
        return User.objects.filter(username=self.kwargs["username"])


@api_view(["GET"])
@ensure_csrf_cookie
def whoami(request: HttpRequest):
    """
    Allows a user with valid auth token to retrieve their username.
    """
    user = request.user
    if user.is_authenticated:
        serializer = api_serializers.UserSerializer(user)
        return Response(serializer.data)
    return Response({"username": user.username}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def register_user(request: HttpRequest):
    """Add a new user to the system."""
    username = request.data["username"]
    password = request.data["password"]
    if re.search(r"\.|\/", username):
        return HttpResponse(
            "username cannot contain periods or slashes.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(username=username)
    if len(user) != 0:
        return HttpResponse(
            "That username is already in the database.",
            status=status.HTTP_400_BAD_REQUEST,
        )
    email = request.data.get("email", "")
    if email == "":
        return HttpResponse(
            "Email is a required field.", status=status.HTTP_400_BAD_REQUEST
        )
    new_user = User(username=username)
    new_user.set_password(password)
    new_user.email = email
    new_user.save()
    token, _ = Token.objects.get_or_create(user=new_user)
    add_default_recipes(new_user)
    return Response({"token": token.key}, status=status.HTTP_201_CREATED)


def add_default_recipes(new_user: User):
    """Add default recipes to a new User's account."""
    default_recipes = [190, 191, 192, 204]
    for recipe_num in default_recipes:
        try:
            def_rec = Recipe.objects.get(pk=recipe_num)
        except Recipe.DoesNotExist:
            continue
        new_rec = Recipe(
            title=def_rec.title,
            user=new_user,
            orientation=def_rec.orientation,
            general_recipe_comment=def_rec.general_recipe_comment,
            bean_name=def_rec.bean_name,
            roast=def_rec.roast,
            grind=def_rec.grind,
            total_bean_amount=def_rec.total_bean_amount,
            bean_units=def_rec.bean_units,
            water_type=def_rec.water_type,
            total_water_amount=def_rec.total_water_amount,
            water_units=def_rec.water_units,
            temp=def_rec.temp,
            total_duration=def_rec.total_duration,
        )
        new_rec.save()
        for step in def_rec.steps.all():
            new_step = Step(
                recipe=new_rec,
                step_number=step.step_number,
                step_title=step.step_title,
                step_body=step.step_body,
                duration=step.duration,
                water_amount=step.water_amount,
                water_units=step.water_units,
            )
            new_step.save()


@api_view(["POST"])
def login_user(request: HttpRequest):
    """Login an existing user."""
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(username=username, password=password)
    if user is None:
        # Return an 'invalid login' error message.
        return HttpResponseBadRequest("Invalid login.")
    if user.is_active:
        login(request, user)
        return HttpResponse("Successfully logged in.")
    # Return a 'disabled account' error message
    return HttpResponseBadRequest("Account disabled.")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def change_password(request: HttpRequest):
    """Allow Logged in user to change their password."""
    username = request.data["username"]
    old_password = request.data["old_password"]
    new_password = request.data["new_password"]
    user = User.objects.filter(username=username)
    if len(user) == 0:
        return HttpResponse("That username is not in the database.")
    if authenticate(username=username, password=old_password):
        u = user[0]
        u.set_password(new_password)
        u.save()
        token, _ = Token.objects.get_or_create(user=u)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes((AllowAny,))
@transaction.atomic
def send_reset_string(request: HttpRequest):
    """
    Email user a random_string with which to reset a forgotten password.
    """
    username = request.data["username"]
    user = User.objects.filter(username=username)
    if len(user) == 0:
        return HttpResponse()

    reset_string = "".join(
        [random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(27)]
    )

    try:
        userinfo = UserInfo.objects.get(user_id=user[0].pk)
    except UserInfo.DoesNotExist:
        userinfo = UserInfo(user_id=user[0].pk)
    userinfo.reset_string = reset_string
    userinfo.save()

    reset_link = f"{settings.FRONTEND_DOMAIN}/#/reset-pw"
    response = requests.post(
        f"https://api.mailgun.net/v3/{settings.MAILGUN_USER}/messages",
        auth=("api", settings.MAILGUN_KEY),
        data={
            "from": f"Mailgun Sandbox <postmaster@{settings.MAILGUN_USER}>",
            "to": user[0].email,
            "subject": "Brew Keeper Password Reset",
            "text": f"""
To reset your Brew Keeper password, please copy this code

{reset_string}

and paste it into the Reset String field at: {reset_link}
            """.strip(),
        },
    )
    if response.status_code != status.HTTP_200_OK:
        raise IntegrationError(f"mail sending status code: {response.status_code}")
    return HttpResponse()


@api_view(["POST"])
@permission_classes((AllowAny,))
@transaction.atomic
def reset_password(request: HttpRequest):
    """Email reset_string to create a new password."""
    new_password = request.data["new_password"]
    try:
        user = User.objects.get(username=request.data["username"])
    except User.DoesNotExist:
        return HttpResponse(
            "That username is not in the database.", status=status.HTTP_400_BAD_REQUEST
        )
    if user.email != request.data["email"]:
        return HttpResponse(
            "Email does not match registered email.", status=status.HTTP_400_BAD_REQUEST
        )
    try:
        reset_string = user.userinfo.reset_string
    except UserInfo.DoesNotExist:
        return HttpResponse(
            "You have not requested a password reset string.",
            status=status.HTTP_400_BAD_REQUEST,
        )
    if reset_string != request.data["reset_string"]:
        return HttpResponse(
            "Reset string does not match expected reset_string.",
            status=status.HTTP_400_BAD_REQUEST,
        )
    user.set_password(new_password)
    user.save()
    user.userinfo.delete()
    user = authenticate(username=request.data["username"], password=new_password)
    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {"token": token.key, "message": "Password successfully reset"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request: HttpRequest):
    """Logout a currently logged in User."""
    Token.objects.get(user=request.user).delete()
    return Response({"username": None})
