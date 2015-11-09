from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Recipe(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    last_brewed_on = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=50)
    orientation = models.CharField(max_length=8, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)
    general_recipe_comment = models.TextField(blank=True, null=True)
    bean_name = models.CharField(max_length=50, blank=True, null=True)
    roast = models.CharField(max_length=15, blank=True, null=True)
    grind = models.CharField(max_length=30, blank=True, null=True)
    total_bean_amount = models.PositiveSmallIntegerField(blank=True, null=True)
    bean_units = models.CharField(max_length=12, blank=True, null=True)
    water_type = models.CharField(max_length=50, blank=True, null=True)
    total_water_amount = models.PositiveSmallIntegerField(
        blank=True, null=True)
    water_units = models.CharField(max_length=12, blank=True, null=True)
    temp = models.PositiveSmallIntegerField(blank=True, null=True)
    brew_count = models.PositiveIntegerField(default=0)
    total_duration = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "{} rated as: {}, bean: {} roast: {}".format(
               self.title, self.rating, self.bean_name, self.roast)

    class Meta:
        ordering = ['-rating']
        default_related_name = 'recipes'


class Step(models.Model):
    recipe = models.ForeignKey(Recipe)
    step_number = models.PositiveSmallIntegerField()
    step_title = models.CharField(max_length=50)
    step_body = models.CharField(max_length=255, blank=True, null=True)
    duration = models.PositiveSmallIntegerField(default=0)
    water_amount = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.step_title

    class Meta:
        ordering = ['step_number']
        default_related_name = 'steps'


class BrewNote(models.Model):
    recipe = models.ForeignKey(Recipe)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}, added: {}".format(self.body, self.timestamp)

    class Meta:
        ordering = ['-timestamp']
        default_related_name = 'brewnotes'


class UserInfo(models.Model):
    user = models.OneToOneField(User)
    password_token = models.CharField(max_length=27, blank=True, null=True)
