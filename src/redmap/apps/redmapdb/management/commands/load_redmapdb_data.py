from django.core.management.base import BaseCommand
from redmap.apps.redmapdb.data import load_redmapdb_data


class Command(BaseCommand):
    args = ''
    help = 'Loads all the basic testing data required by Redmap'

    def handle(self, *args, **options):
        load_redmapdb_data()
        self.stdout.write('Successfully loaded data\n')
