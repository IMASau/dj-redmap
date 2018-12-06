from django.core.management.base import BaseCommand
from redmap.apps.redmapdb.data import load_test_sightings


class Command(BaseCommand):
    args = ''
    help = 'Loads basic test sightings'

    def handle(self, *args, **options):
        load_test_sightings()
        self.stdout.write('Successfully added test sightings\n')
