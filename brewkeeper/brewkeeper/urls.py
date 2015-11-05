"""brewkeeper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework_nested import routers
from api import views as api_views


router = routers.SimpleRouter()

router.register(r'recipes', api_views.RecipeViewSet)

recipes_steps_router = routers.NestedSimpleRouter(router,
                                                  r'recipes',
                                                  lookup='recipe')
recipes_steps_router.register(r'steps',
                              api_views.StepViewSet,
                              base_name='step_list')

recipes_brewnotes_router = routers.NestedSimpleRouter(router,
                                                      r'recipes',
                                                      lookup='recipe')

recipes_brewnotes_router.register(r'brewnotes',
                                  api_views.BrewNoteViewSet,
                                  base_name='brewnote_list')

recipes_ratings_router = routers.NestedSimpleRouter(router,
                                                    r'recipes',
                                                    lookup='recipe')

recipes_ratings_router.register(r'ratings',
                                api_views.PublicRatingViewSet,
                                base_name='public_ratings')

recipes_comments_router = routers.NestedSimpleRouter(router,
                                                     r'recipes',
                                                     lookup='recipe')

recipes_comments_router.register(r'comments',
                                 api_views.PublicCommentViewSet,
                                 base_name='public_comments')

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^docs/', include('rest_framework_swagger.urls')),

    url(r'^api/users/don\.pablo/', include(router.urls)),

    url(r'^api/users/don\.pablo/', include(recipes_steps_router.urls)),

    url(r'^api/users/don\.pablo/', include(recipes_brewnotes_router.urls)),

    url(r'^api/users/don\.pablo/', include(recipes_ratings_router.urls)),

    url(r'^api/users/don\.pablo/', include(recipes_comments_router.urls)),

    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
]
