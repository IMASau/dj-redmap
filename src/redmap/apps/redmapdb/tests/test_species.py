from datetime import datetime
from django.contrib.auth.models import User, Group
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users, \
    load_test_sighting
from redmap.apps.redmapdb.models import *


class SpeciesTests(TestCase):

    def setUp(self):
        load_redmapdb_data()

    def test_get_redmap_species(self):
        """
        Check get_redmap species returns expected results
        """
        total_count = Species.objects.all().count()
        redmap_count = Species.objects.get_redmap().count()
        
        # In test data, all species are active
        self.assertEqual(total_count, redmap_count)
        
        # We should be able to hide a species by marking active=False
        species = Species.objects.all()[0]
        species.active=False
        species.save()
        self.assertEqual(redmap_count-1, Species.objects.get_redmap().count())
        
        # We should be able to show it again by marking active=True
        species.active=True
        species.save()
        self.assertEqual(redmap_count, Species.objects.get_redmap().count())
        