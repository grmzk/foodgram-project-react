import json
import sys

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, MeasurementUnit

INGREDIENTS_FILE = 'static/ingredients.json'


class Command(BaseCommand):
    help = 'Import data from JSON-files to database'

    def import_ingredients(self):

        with open(INGREDIENTS_FILE) as file:
            json_obj = json.load(file)
            for item in json_obj:
                unit, _ = MeasurementUnit.objects.get_or_create(
                    name=item['measurement_unit']
                )
                Ingredient.objects.get_or_create(name=item['name'],
                                                 measurement_unit=unit)

    def handle(self, *args, **options):
        self.stdout.write('Recommendation: do <python manage.py flush> '
                          'before this operation!\n'
                          'Input <Yes> to continue')
        answer = sys.stdin.readline()
        if answer.lower() != 'yes\n':
            return

        try:
            self.import_ingredients()
        except Exception as error:
            self.stderr.write(f'{error}\nIngredients import failed!')
            return

        self.stdout.write(self.style.SUCCESS(
            'Everything has been imported successfully'
        ))
