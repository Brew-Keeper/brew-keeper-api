# from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets  # , mixins  # , permissions, serializers
from .models import Recipe, Step, BrewNote, PublicRating, PublicComment
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

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        serializer.save()
        total = recipe.steps.aggregate(Sum('duration'))
        recipe.total_duration = total['duration__sum']
        recipe.save()

    def perform_update(self, serializer):
        serializer.save()
        instance = self.get_object()
        total = instance.recipe.steps.aggregate(Sum('duration'))
        instance.recipe.total_duration = total['duration__sum']
        instance.recipe.save()

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


class PublicRatingViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.PublicRatingSerializer

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        return PublicRating.objects.all().filter(
            # user=self.request.user,
            recipe=recipe)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        serializer.save()
        rating_calc = recipe.public_ratings.aggregate(Avg('public_rating'))
        recipe.average_rating = rating_calc['public_rating__avg']
        recipe.save()

    def perform_update(self, serializer):
        serializer.save()
        instance = self.get_object()
        rating_calc = instance.recipe.public_ratings.aggregate(Avg('public_rating'))
        instance.recipe.average_rating = rating_calc['public_rating__avg']
        instance.recipe.save()

    def perform_destroy(self, instance):
        recipe = instance.recipe
        instance.delete()
        rating_calc = recipe.public_ratings.aggregate(Avg('public_rating'))
        recipe.average_rating = rating_calc['public_rating__avg']
        recipe.save()



class PublicCommentViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.PublicCommentSerializer

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        return PublicComment.objects.all().filter(
            # user=self.request.user,
            recipe=recipe)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        return context
