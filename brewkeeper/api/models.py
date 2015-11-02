from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Recipe(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    last_brewed_on = models.DateTimeField(auto_now=True)
    user = models.ForiegnKey(User)
    title = models.CharField(max_length=50)
    orientation = models.BooleanField()
    user_rating = models.PositiveSmallIntegerField()
    general_recipe_comment = models.TextField()
    bean_type = models.CharField(max_length=50)
    bean_roast = models.CharField(max_length=50)
    grind = models.CharField(max_length=50)
    total_bean_amount = models.PositiveSmallIntergerField()
    bean_units = models.CharField(max_length=50)
    water_type = models.CharField(max_length=50)
    total_water_amount = models.PositiveSmallIntergerField()
    water_amount_units = models.CharField(max_length=50)
    temp = models.PositiveSmallIntegerField()
    brew_count = models.PositiveSmallIntegerField()
    total_duration = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.recipe_title


class Step(models.Model):
    recipe = models.ForeignKey(Recipe)
    step_title = models.CharField(max_length=50)
    step_detail = models.Charfield(max_length=255)
    duration = models.PositiveSmallIntegerField()
    water_amount = models.PositiveSmallIntegerField()


class Brewnote(models.Model):
    recipe = models.ForeignKey(Recipe)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    
