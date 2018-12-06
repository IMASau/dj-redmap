from django.core.management.base import BaseCommand
from redmap.apps.cms.models import Page

class Command(BaseCommand):
    args = ''
    help = 'Migrates Pages using the `resource` template to `resource-listing`'

    def handle(self, *args, **options):

        for page in Page.objects.filter(template='resource.html'):
            page.template = 'resource-listing.html'
            page.save()

        self.stdout.write('Successfully migrated page templates\n')
