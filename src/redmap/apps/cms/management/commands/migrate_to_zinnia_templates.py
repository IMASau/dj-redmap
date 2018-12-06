from django.core.management.base import BaseCommand
from zinnia.models import Entry


class Command(BaseCommand):
    args = ''
    help = 'Migrates Entries templates to the new designs'

    def handle(self, *args, **options):

        i = 0

        for e in Entry.objects.filter(template='zinnia/article-with-photos.html'):
            e.template = 'zinnia/single_article_2_photos_left.html'
            e.save()
            i += 1

        for e in Entry.objects.filter(template='zinnia/photo-page-a.html'):
            e.template = 'zinnia/single_article_3_photos_below.html'
            e.save()
            i += 1

        self.stdout.write('Successfully migrated {0} entries templates\n'.format(i))
