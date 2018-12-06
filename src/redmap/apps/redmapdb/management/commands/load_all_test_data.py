from django.core.management.base import BaseCommand
from redmap.apps.redmapdb.data import load_all_data


class Command(BaseCommand):
    args = ''
    help = 'Loads basic data required by Redmap'

    def handle(self, *args, **options):
        load_all_data
        self.stdout.write('Successfully loaded data\n')
