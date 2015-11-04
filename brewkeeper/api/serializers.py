from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Recipe, Step, BrewNote


class StepSerializer(serializers.HyperlinkedModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(many=False,
                                                   read_only=True,
                                                   source='recipe')

    class Meta:
        model = Step
        fields = ('id', 'recipe_id', 'step_number', 'step_title', 'step_body',
                  'duration', 'water_amount')

    def create(self, validated_data):
        validated_data['recipe_id'] = self.context['recipe_id']
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


class RecipeListSerializer(serializers.HyperlinkedModelSerializer):
    # username = serializers.PrimaryKeyRelatedField(many=False,
    #                                              read_only=True,
    #                                              source='user_username')

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'rating', 'bean_name', 'roast', 'brew_count',
                  # 'username'
                  )


class RecipeDetailSerializer(RecipeListSerializer):
    # username = serializers.PrimaryKeyRelatedField(many=False,
    #                                              read_only=True,
    #                                              source='user_username')

    steps = StepSerializer(many=True, read_only=True)
    brewnotes = BrewNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = tuple(list(RecipeListSerializer.Meta.fields) +
                       ['created_on', 'last_brewed_on', 'orientation',
                        'general_recipe_comment', 'grind', 'total_bean_amount',
                        'bean_units', 'water_type', 'total_water_amount',
                        'water_units', 'temp', 'total_duration',
                        'steps', 'brewnotes'
                        ])


class UserSerializer(serializers.HyperlinkedModelSerializer):
    recipes = RecipeListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'recipes', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
