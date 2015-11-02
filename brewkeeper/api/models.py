from django.db import models
# from django.contrib.auth.models import User

# Create your models here.


class Recipe(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    last_brewed_on = models.DateTimeField(auto_now=True)
    # user = models.ForeignKey(User)
    title = models.CharField(max_length=50)
    orientation = models.CharField(max_length=8)
    rating = models.PositiveSmallIntegerField()
    general_recipe_comment = models.TextField()
    bean_name = models.CharField(max_length=50)
    roast = models.CharField(max_length=25)
    grind = models.CharField(max_length=25)
    total_bean_amount = models.PositiveSmallIntergerField()
    bean_units = models.CharField(max_length=12)
    water_type = models.CharField(max_length=50)
    total_water_amount = models.PositiveSmallIntergerField()
    water_amount_units = models.CharField(max_length=12)
    temp = models.PositiveSmallIntegerField()
    brew_count = models.PositiveSmallIntegerField()
    total_duration = models.PositiveSmallIntegerField()

    def __str__(self):
        return "{}, rated as: {}, using: {}, and {}".format(self.title, self.rating, self.bean_name, self.roast)


class Step(models.Model):
    recipe = models.ForeignKey(Recipe)
    step_title = models.CharField(max_length=50)
    step_detail = models.Charfield(max_length=255)
    duration = models.PositiveSmallIntegerField()
    water_amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.step_title


class Brewnote(models.Model):
    recipe = models.ForeignKey(Recipe)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}, added on: {}".format(self.body, self.timestamp)
