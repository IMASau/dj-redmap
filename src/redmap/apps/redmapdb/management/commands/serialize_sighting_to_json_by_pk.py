from django.core.management.base import BaseCommand
from redmap.apps.redmapdb.models import Sighting
from django.core import serializers
from django.db.models.fields.related import ForeignKey


class Command(BaseCommand):
    args = ''
    help = 'Convert a single sighting to json to check attributes and relations'

    def handle(self, *args, **options):
        sighting = None
        try:
            sighting = Sighting.objects.get(pk=args[0])
        except Sighting.DoesNotExist:
            self.stdout.write('That sighting does not exist\n')

        exclude = ['user', ]
        fk_fields = filter(lambda field: isinstance(field, ForeignKey) and not field.name in exclude, sighting._meta.fields)
        fk_field_names = map(lambda field: field.name, fk_fields)

        serialized_obj = serializers.serialize('json', [sighting, ], indent=2)
        #serialized_obj = serializers.serialize('json2', [sighting, ], indent=2, relations=tuple(fk_field_names))
        self.stdout.write(serialized_obj + "\n")
