# from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets  # , mixins  # , permissions, serializers
from .models import Recipe, Step, BrewNote
# from .permissions import IsAPIUser
from . import serializers as api_serializers


# Create your views here.

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = api_serializers.RecipeSerializer

    # def get_queryset(self):
    #     return self.request.user.activity_set.all()

    def get_serializer_class(self):
        if self.action is 'list':
            return api_serializers.RecipeListSerializer
        else:
            return api_serializers.RecipeDetailSerializer


class StepViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.StepSerializer

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        return Step.objects.all().filter(
            # user=self.request.user,
            recipe=recipe)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        return context

    def perform_destroy(self, instance):
        instance.recipe.total_duration -= instance.duration
        instance.recipe.save()
        instance.delete()


class BrewNoteViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.BrewNoteSerializer

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        return BrewNote.objects.all().filter(
            # user=self.request.user,
            recipe=recipe)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        return context
