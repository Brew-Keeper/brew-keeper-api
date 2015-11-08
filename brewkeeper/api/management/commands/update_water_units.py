from django.core.management.base import BaseCommand
from api.models import Recipe


class Command(BaseCommand):

    def handle(self, *args, **options):
        '''Copy water_units from recipe into steps'''
        recipes = Recipe.objects.all()

        for recipe in recipes:
            steps = recipe.steps.all()

            for step in steps:
                step.water_units = recipe.water_units
                step.save()
