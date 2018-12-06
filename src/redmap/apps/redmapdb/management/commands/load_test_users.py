from django.core.management.base import BaseCommand
from redmap.apps.redmapdb.data import load_test_users

class Command(BaseCommand):
    args = ''
    help = 'Loads basic data required by Redmap'

    def handle(self, *args, **options):
        load_test_users()
        self.stdout.write('Successfully loaded data\n')
