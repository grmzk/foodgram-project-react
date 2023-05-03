import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand

DUMP_PATH = 'static'
APPS = [
    'users',
    'recipes',
]


class Command(BaseCommand):
    help = f'Dump data to `{DUMP_PATH}` folder'

    def handle(self, *args, **options):
        sysout = sys.stdout

        try:
            for app in APPS:
                sys.stdout = open(f'{DUMP_PATH}/{app}.json', 'w')
                call_command('dumpdata', app)
        except Exception as error:
            self.stderr.write(f'{error}\nModels dump failed!')
            return

        sys.stdout = sysout

        self.stdout.write(self.style.SUCCESS(
            'Everything has been dumped successfully'
        ))
