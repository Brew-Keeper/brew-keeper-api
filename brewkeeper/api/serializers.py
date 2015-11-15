from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Recipe, Step, BrewNote, PublicRating, PublicComment, UserInfo


class StepSerializer(serializers.HyperlinkedModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(many=False,
                                                   read_only=True,
                                                   source='recipe')

    class Meta:
        model = Step
        fields = ('id', 'recipe_id', 'step_number', 'step_title', 'step_body',
                  'duration', 'water_amount', 'water_units')

    def create(self, validated_data):
        validated_data['recipe_id'] = self.context['recipe_id']
        try:
            validated_data['water_units']
        except:
            recipe = get_object_or_404(Recipe, pk=self.context['recipe_id'])
            validated_data['water_units'] = recipe.water_units
        step = Step.objects.create(**validated_data)
        return step


class BrewNoteSerializer(serializers.HyperlinkedModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(many=False,
                                                   read_only=True,
                                                   source='recipe')

    class Meta:
        model = BrewNote
        fields = ('id', 'recipe_id', 'body', 'timestamp')

    def create(self, validated_data):
        validated_data['recipe_id'] = self.context['recipe_id']
        brew_note = BrewNote.objects.create(**validated_data)
        return brew_note


class PublicRatingSerializer(serializers.HyperlinkedModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(many=False,
                                                   read_only=True,
                                                   source='recipe')
    username = serializers.PrimaryKeyRelatedField(many=False,
                                                  read_only=True,
                                                  source='user.username')

    class Meta:
        model = PublicRating
        fields = ('id',
                  'recipe_id',
                  'username',
                  'public_rating')
        # extra_kwargs = {'username': {'write_only': True}}

    def create(self, validated_data):
        validated_data['recipe_id'] = self.context['recipe_id']
        user = get_object_or_404(User, username=self.context['username'])
        validated_data['user'] = user
        public_rating = PublicRating.objects.create(**validated_data)
        return public_rating


class PublicCommentSerializer(serializers.HyperlinkedModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(many=False,
                                                   read_only=True,
                                                   source='recipe')
    username = serializers.PrimaryKeyRelatedField(many=False,
                                                  read_only=True,
                                                  source='user.username')

    class Meta:
        model = PublicComment
        fields = ('id',
                  'recipe_id',
                  'username',
                  'public_comment',
                  'comment_timestamp')

    def create(self, validated_data):
        validated_data['recipe_id'] = self.context['recipe_id']
        user = get_object_or_404(User, username=self.context['username'])
        validated_data['user'] = user
        public_comment = PublicComment.objects.create(**validated_data)
        return public_comment


class RecipeListSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.PrimaryKeyRelatedField(many=False,
                                                  read_only=True,
                                                  source='user.username')
    steps = StepSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'rating', 'bean_name', 'roast', 'brew_count',
                  'username', 'steps', 'total_duration', 'water_units')


class RecipeDetailSerializer(RecipeListSerializer):
    brewnotes = BrewNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = tuple(list(RecipeListSerializer.Meta.fields) +
                       ['created_on', 'last_brewed_on', 'orientation',
                        'general_recipe_comment', 'grind', 'total_bean_amount',
                        'bean_units', 'water_type', 'total_water_amount',
                        'brewnotes', 'temp'])

    def create(self, validated_data):
        '''username in context defined in RecipeViewSet in views.py'''
        user = get_object_or_404(User, username=self.context['username'])
        validated_data['user'] = user
        recipe = Recipe.objects.create(**validated_data)
        return recipe


class PublicRecipeListSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.PrimaryKeyRelatedField(many=False,
                                                  read_only=True,
                                                  source='user.username')
    steps = StepSerializer(many=True, read_only=True)
    public_ratings = PublicRatingSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'rating', 'bean_name', 'roast', 'brew_count',
                  'username', 'steps', 'total_duration', 'water_units',
                  'average_rating', 'public_ratings')


class PublicRecipeDetailSerializer(PublicRecipeListSerializer):
    brewnotes = BrewNoteSerializer(many=True, read_only=True)
    public_comments = PublicCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = tuple(list(PublicRecipeListSerializer.Meta.fields) +
                       ['created_on', 'last_brewed_on', 'orientation',
                        'general_recipe_comment', 'grind', 'total_bean_amount',
                        'bean_units', 'water_type', 'total_water_amount',
                        'brewnotes', 'temp', 'public_comments'])

    def create(self, validated_data):
        '''username in context defined in RecipeViewSet in views.py'''
        user = get_object_or_404(User, username=self.context['username'])
        validated_data['user'] = user
        recipe = Recipe.objects.create(**validated_data)
        return recipe


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True},
                        'email': {'write_only': True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserInfoSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.PrimaryKeyRelatedField(many=False,
                                                  read_only=True,
                                                  source='user.username')
    email = serializers.EmailField(allow_blank=False)
    new_password = serializers.CharField(max_length=None)
    reset_string = serializers.CharField(max_length=27)

    class Meta:
        model = UserInfo
        fields = ('id', 'username', 'email', 'new_password', 'reset_string')
        extra_kwargs = {'new_password': {'write_only': True}}
