# from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Recipe  # , Step, BrewNote


# class StepSerializer(serializers.HyperlinkedModelSerializer):
#     recipe_id = serializers.PrimaryKeyRelatedField(many=False,
#                                                    read_only=True,
#                                                    source='recipe')
#
#     class Meta:
#         model = Step
#         fields = ('id', 'recipe_id', 'body', 'date')
#
#     def create(self, validated_data):
#         validated_data['recipe_id'] = self.context['recipe_id']
#         step = Step.objects.create(**validated_data)
#         return step


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    # username = serializers.PrimaryKeyRelatedField(many=False,
    #                                              read_only=True,
    #                                              source='user_username')

    # steps = StepSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'created_on', 'last_brewed_on', 'title', 'orientation',
                  'rating', 'general_recipe_comment', 'bean_name', 'roast',
                  'grind', 'total_bean_amount', 'bean_units', 'water_type',
                  'total_water_amount', 'water_units', 'temp', 'brew_count',
                  'total_duration',
                #   'steps', 'brew_notes'
                  )
