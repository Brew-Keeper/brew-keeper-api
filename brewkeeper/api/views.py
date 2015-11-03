# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins  # , permissions, serializers
from .models import Recipe  # , Step, BrewNote
# from .permissions import IsAPIUser
from .serializers import RecipeSerializer  # , RecipeListSerializer, StepSerializer, BrewNoteSerializer


# Create your views here.

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    # def get_queryset(self):
    #     return self.request.user.activity_set.all()

    # def get_serializer_class(self):
    #     if self.action is not 'list':
    #         return RecipeSerializer
    #     else:
    #         return RecipeListSerializer
