from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, status, filters, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Recipe, Step, BrewNote, PublicRating, PublicComment, UserInfo
from .permissions import IsAskerOrPublic
from . import serializers as api_serializers
import requests
import os


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title',
                     'bean_name',
                     'roast',
                     'step__step_body',
                     'brewnote__body',
                     'shared_by')
    ordering_fields = ('rating',
                       'brew_count',
                       'created_on')
    permission_classes = (IsAskerOrPublic,)

    def get_queryset(self):
        if self.kwargs['user_username'] == 'public' \
                and self.request.method in permissions.SAFE_METHODS:
            return User.objects.get(username='public').recipes.all() \
                .prefetch_related('public_comments', 'public_ratings', 'steps')
        return self.request.user.recipes.all() \
            .prefetch_related('steps', 'brewnotes')

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        if self.kwargs['user_username'] == 'public' \
                and self.request.method == 'POST':
            context['username'] = 'public'
        else:
            context['username'] = self.request.user.username
        return context

    def get_serializer_class(self):
        if self.kwargs['user_username'] == 'public':
            if self.action is 'list':
                return api_serializers.PublicRecipeListSerializer
            else:
                return api_serializers.PublicRecipeDetailSerializer
        if self.action is 'list':
            return api_serializers.RecipeListSerializer
        else:
            return api_serializers.RecipeDetailSerializer


class StepViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.StepSerializer
    # permission_classes = (IsAskerOrPublic,)

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        return Step.objects.all().filter(recipe=recipe)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        return context

    def perform_create(self, serializer):
        '''Update total duration and rearrange steps if necessary'''

        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        existing_steps = recipe.steps.all().order_by('step_number')

        overlap = False
        for step in existing_steps:
            if step.step_number == int(serializer.initial_data['step_number']):
                overlap = True
            if overlap:
                step.step_number += 1
                step.save()

        serializer.save()
        total = recipe.steps.aggregate(Sum('duration'))
        recipe.total_duration = total['duration__sum']
        recipe.save()

    def perform_update(self, serializer):
        '''Rearrange steps if necessary'''
        instance = self.get_object()
        new_step_num = int(serializer.initial_data['step_number'])
        if instance.step_number != new_step_num:
            curr_steps = instance.recipe.steps.all().order_by('step_number')
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
        total = instance.recipe.steps.aggregate(Sum('duration'))
        instance.recipe.total_duration = total['duration__sum']
        instance.recipe.save()

    def perform_destroy(self, instance):
        curr_steps = instance.recipe.steps.all().order_by('step_number')
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
    serializer_class = api_serializers.BrewNoteSerializer

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        return BrewNote.objects.all().filter(recipe=recipe)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        return context


class PublicRatingViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.PublicRatingSerializer

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        return PublicRating.objects.filter(recipe=recipe,
                                           user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        context['username'] = self.request.user.username
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])
        serializer.initial_data['user'] = self.request.user
        serializer.save()
        rating_calc = recipe.public_ratings.aggregate(Avg('public_rating'))
        recipe.average_rating = rating_calc['public_rating__avg']
        recipe.save()

    def perform_update(self, serializer):
        serializer.save()
        instance = self.get_object()
        rating_calc = instance.recipe.public_ratings.aggregate(
            Avg('public_rating'))
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
        return PublicComment.objects.all().filter(recipe=recipe)

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        context['recipe_id'] = self.kwargs['recipe_pk']
        context['username'] = self.request.user.username
        return context

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = api_serializers.UserSerializer
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(username=self.kwargs['username'])


@api_view(['GET'])
@ensure_csrf_cookie
def whoami(request):
    user = request.user
    if user.is_authenticated():
        serializer = api_serializers.UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response({"username": user.username},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register_user(request):
    username = request.data['username']
    password = request.data['password']
    user = User.objects.filter(username=username)
    if len(user) != 0:
        return HttpResponse('That username is already in the database.',
                            status=status.HTTP_400_BAD_REQUEST)
    if request.data.get('email', '') == '':
        return HttpResponse('Email is a required field.',
                            status=status.HTTP_400_BAD_REQUEST)
    new_user = User(username=username)
    new_user.set_password(password)
    new_user.email = request.data.get('email', '')
    new_user.save()
    add_default_recipes(new_user)
    token, created = Token.objects.get_or_create(user=new_user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


def add_default_recipes(new_user):
    DEFAULT_RECIPES = [190, 191, 192, 204]
    for recipe_num in DEFAULT_RECIPES:
        def_rec = Recipe.objects.get(pk=recipe_num)
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
            total_duration=def_rec.total_duration
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
                water_units=step.water_units
            )
            new_step.save()


@api_view(['POST'])
def login_user(request):
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
@permission_classes((IsAuthenticated, ))
def change_password(request):
    '''Allow Logged in user to change their password.'''
    username = request.data['username']
    old_password = request.data['old_password']
    new_password = request.data['new_password']
    user = User.objects.filter(username=username)
    if len(user) == 0:
        return HttpResponse('That username is not in the database.')
    if authenticate(username=username, password=old_password):
        u = user[0]
        u.set_password(new_password)
        u.save()
        token, created = Token.objects.get_or_create(user=u)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def send_reset_string(request):
    '''Email user with a random_string which will allow them to reset a
    forgotten password.'''
    username = request.data['username']
    user = User.objects.filter(username=username)
    if len(user) == 0:
        return HttpResponse('That username is not in the database. ')
    import random
    reset_string = "".join(
        [random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(27)])
    recipient = user[0].email
    html = 'https://brew-keeper.firebaseapp.com/#/reset-pw'
    MAILGUN_KEY = os.environ['MAILGUN_KEY']
    sandbox = 'sandbox014f80db3f0b441e94e5a6faff21f392.mailgun.org'
    request_url = 'https://api.mailgun.net/v3/{}/messages'.format(sandbox)
    request = requests.post(request_url, auth=('api', MAILGUN_KEY), data={
        'from': 'Mailgun Sandbox <postmaster@sandbox014f80db3f0b441e94e5a6faff21f392.mailgun.org>',
        'to': recipient,
        'subject': 'Brew Keeper Password Reset',
        'text': 'To reset your Brew Keeper password, please copy this code\n\n{}'.format(reset_string) +
        '\n\nand paste it into the Reset String field at: ' + html})
    try:
        userinfo = UserInfo.objects.get(user_id=user[0].pk)
    except:
        userinfo = UserInfo(user_id=user[0].pk)
    userinfo.reset_string = reset_string
    userinfo.save()
    if str(request.status_code) == '200':
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def reset_password(request):
    '''User can use emailed reset_string to create a new password, login and
    receive a new token.'''
    new_password = request.data['new_password']
    try:
        user = User.objects.get(username=request.data['username'])
    except:
        return HttpResponse('That username is not in the database.',
                            status=status.HTTP_400_BAD_REQUEST)
    if user.email != request.data['email']:
        return HttpResponse('Email does not match registered email.',
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        reset_string = user.userinfo.reset_string
    except:
        return HttpResponse('You have not requested a password reset string.',
                            status=status.HTTP_400_BAD_REQUEST)
    if reset_string != request.data['reset_string']:
        return HttpResponse('Reset string does not match expected reset_string.',
                            status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    user.userinfo.delete()
    user = authenticate(username=request.data['username'],
                        password=new_password)
    login(request, user)
    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key,
                     'message': 'Password successfully reset'},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def logout_user(request):
    Token.objects.get(user=request.user).delete()
    return Response({'username': None})
