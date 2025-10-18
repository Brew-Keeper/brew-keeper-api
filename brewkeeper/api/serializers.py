"""Serializers for the BrewKeeper app."""

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import BrewNote, PublicComment, PublicRating, Recipe, Step, UserInfo


class StepSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Step objects."""

    recipe_id = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="recipe"
    )

    class Meta:  # noqa
        model = Step
        fields = (
            "id",
            "recipe_id",
            "step_number",
            "step_title",
            "step_body",
            "duration",
            "water_amount",
            "water_units",
        )

    def create(self, validated_data: dict):  # noqa
        validated_data["recipe_id"] = self.context["recipe_id"]
        try:
            validated_data["water_units"]
        except KeyError:
            recipe = get_object_or_404(Recipe, pk=self.context["recipe_id"])
            validated_data["water_units"] = recipe.water_units
        return Step.objects.create(**validated_data)


class BrewNoteSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for BrewNote objects."""

    recipe_id = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="recipe"
    )

    class Meta:  # noqa
        model = BrewNote
        fields = ("id", "recipe_id", "body", "timestamp")

    def create(self, validated_data: dict):  # noqa
        validated_data["recipe_id"] = self.context["recipe_id"]
        return BrewNote.objects.create(**validated_data)


class PublicRatingSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for PublicRating objects."""

    recipe_id = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="recipe"
    )
    username = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="user.username"
    )

    class Meta:  # noqa
        model = PublicRating
        fields = ("id", "recipe_id", "username", "public_rating")

    def create(self, validated_data: dict):  # noqa
        validated_data["recipe_id"] = self.context["recipe_id"]
        user = get_object_or_404(User, username=self.context["username"])
        validated_data["user"] = user
        return PublicRating.objects.create(**validated_data)


class PublicCommentSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for PublicComment objects."""

    recipe_id = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="recipe"
    )
    username = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="user.username"
    )

    class Meta:  # noqa
        model = PublicComment
        fields = ("id", "recipe_id", "username", "public_comment", "comment_timestamp")

    def create(self, validated_data: dict):  # noqa
        validated_data["recipe_id"] = self.context["recipe_id"]
        user = get_object_or_404(User, username=self.context["username"])
        validated_data["user"] = user
        return PublicComment.objects.create(**validated_data)


class RecipeListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for RecipeList objects."""

    username = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="user.username"
    )
    steps = StepSerializer(many=True, read_only=True)

    class Meta:  # noqa
        model = Recipe
        fields = (
            "id",
            "title",
            "rating",
            "bean_name",
            "roast",
            "brew_count",
            "username",
            "steps",
            "total_duration",
            "water_units",
        )


class RecipeDetailSerializer(RecipeListSerializer):
    """Serializer for RecipeDetail objects."""

    brewnotes = BrewNoteSerializer(many=True, read_only=True)

    class Meta:  # noqa
        model = Recipe
        detail_fields = [
            "created_on",
            "last_brewed_on",
            "orientation",
            "general_recipe_comment",
            "grind",
            "total_bean_amount",
            "bean_units",
            "water_type",
            "total_water_amount",
            "brewnotes",
            "temp",
        ]
        fields = (*list(RecipeListSerializer.Meta.fields), *detail_fields)

    def create(self, validated_data: dict):
        """Username in context defined in RecipeViewSet in views.py."""
        user = get_object_or_404(User, username=self.context["username"])
        validated_data["user"] = user
        return Recipe.objects.create(**validated_data)


class PublicRecipeListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for PublicRecipeList objects."""

    username = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="user.username"
    )
    steps = StepSerializer(many=True, read_only=True)
    public_ratings = serializers.SerializerMethodField()
    combined_rating = serializers.SerializerMethodField()

    class Meta:  # noqa
        model = Recipe
        fields = (
            "id",
            "title",
            "rating",
            "bean_name",
            "roast",
            "brew_count",
            "username",
            "steps",
            "total_duration",
            "water_units",
            "average_rating",
            "public_ratings",
            "combined_rating",
            "shared_by",
        )

    def get_public_ratings(self, obj: Recipe):
        """
        Get the User's PublicRating for the Recipe in question.

        :param obj: Recipe The Recipe in question
        :return: dict The serialized ratings
        """
        try:
            user = self.context["request"].user
            public_rating = PublicRating.objects.get(user=user, recipe=obj)
            serializer = PublicRatingSerializer(public_rating)
            return serializer.data
        except PublicRating.DoesNotExist:
            return {}

    def get_combined_rating(self, obj: Recipe):
        """
        Get the User's PublicRating for the Recipe in question.
        """
        try:
            user = self.context["request"].user
            user_rating = PublicRating.objects.get(user=user, recipe=obj)
            return user_rating.public_rating
        except PublicRating.DoesNotExist:
            return obj.average_rating


class PublicRecipeDetailSerializer(PublicRecipeListSerializer):
    """Serializer for PublicRecipeDetail objects."""

    brewnotes = BrewNoteSerializer(many=True, read_only=True)
    public_comments = PublicCommentSerializer(many=True, read_only=True)

    class Meta:  # noqa
        model = Recipe
        detail_fields = [
            "created_on",
            "last_brewed_on",
            "orientation",
            "general_recipe_comment",
            "grind",
            "total_bean_amount",
            "bean_units",
            "water_type",
            "total_water_amount",
            "brewnotes",
            "temp",
            "public_comments",
        ]
        fields = (*list(PublicRecipeListSerializer.Meta.fields), *detail_fields)

    def create(self, validated_data: dict):
        """Username in context defined in RecipeViewSet in views.py"""
        user = get_object_or_404(User, username=self.context["username"])
        validated_data["user"] = user
        return Recipe.objects.create(**validated_data)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for User objects."""

    class Meta:  # noqa
        model = User
        fields = ("username", "password", "email")
        extra_kwargs = {"password": {"write_only": True}, "email": {"write_only": True}}

    def create(self, validated_data: dict):  # noqa
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserInfoSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for UserInfo objects."""

    username = serializers.PrimaryKeyRelatedField(
        many=False, read_only=True, source="user.username"
    )
    email = serializers.EmailField(allow_blank=False)
    new_password = serializers.CharField(max_length=None)
    reset_string = serializers.CharField(max_length=27)

    class Meta:  # noqa
        model = UserInfo
        fields = ("id", "username", "email", "new_password", "reset_string")
        extra_kwargs = {"new_password": {"write_only": True}}
