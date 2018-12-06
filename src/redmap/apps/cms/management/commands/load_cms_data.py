from django.core.management.base import BaseCommand
from redmap.apps.cms.data import load_cms_data

class Command(BaseCommand):
    args = ''
    help = 'Loads basic data required by the cms'

    def handle(self, *args, **options):
        load_cms_data()
        self.stdout.write('Successfully loaded cms data\n')
