from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status  # , permissions, serializers
from rest_framework.decorators import api_view  # , detail_route
from rest_framework.response import Response
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
        new_total = instance.recipe.total_duration - instance.duration
        if new_total < 0:
            instance.recipe.total_duration = 0
        else:
            instance.recipe.total_duration = new_total
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


class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin,
                  mixins.UpdateModelMixin, mixins.RetrieveModelMixin):
    # permission_classes = (IsReadOnly,)
    queryset = User.objects.filter(username='username')
    serializer_class = api_serializers.UserSerializer
    lookup_field = 'username'


@api_view(['GET'])
def whoami(request):
    user = request.user
    if user.is_authenticated():
        serializer = api_serializers.UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response('', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def user_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponse('Successfully logged in.')
        else:
            # Return a 'disabled account' error message
            return HttpResponseBadRequest('Account disabled.')
    else:
        # Return an 'invalid login' error message.
        return HttpResponseBadRequest('Invalid login.')


@api_view(['POST'])
def user_logout(request):
    logout(request)
    return HttpResponse('Successfully logged out.')
