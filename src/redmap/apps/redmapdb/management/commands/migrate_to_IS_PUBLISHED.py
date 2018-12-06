from django.core.management.base import BaseCommand
from redmap.apps.redmapdb.models import Sighting


class Command(BaseCommand):
    args = ''
    help = 'Migrates away from Sighting.IS_NOT_DISPLAYED in favour of Sighting.IS_PUBLISHED'

    def handle(self, *args, **options):
        sightings = Sighting.objects.all()
        length = sightings.count()

        for (count, sighting) in enumerate(sightings):
            sighting.is_published = not sighting.is_not_displayed and sighting.is_valid_sighting
            sighting.save()

            self.stdout.write("\r%d of %d done" % (count, length))
            self.stdout.flush()

        self.stdout.write('\nMigration complete\n')
