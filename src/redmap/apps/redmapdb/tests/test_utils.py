
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data
from redmap.apps.redmapdb.models import Region
from redmap.apps.redmapdb.utils import find_region


class FindRegionTest(TestCase):

    def setUp(self):
        load_redmapdb_data()

    def test_get_by_coordinates(self):
        region = Region.objects.get_by_coordinates(-42.1278, 148.0761)
        self.assertEqual(region.description, "Tasmania")

    def test_find_region(self):
        """
        Tests the find region utility method
        """
        self.assertEqual(
            find_region(-42.1278, 148.0761), "Tasmania")  # Swansea
        self.assertEqual(
            find_region(-33.8683, 151.2086), "New South Wales")  # Sydney
        self.assertEqual(
            find_region(-31.9554, 115.8585), "Western Australia")  # Perth