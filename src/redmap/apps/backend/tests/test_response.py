"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from redmap.apps.backend.models import ValidationResponse, SightingValidationCondition
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users
from redmap.apps.redmapdb.data import load_test_sighting
from redmap.apps.redmapdb.models import PHOTO_MATCHES_SPECIES_YES

class ValidationResponseTests(TestCase):

    def setUp(self):
        load_redmapdb_data()
        load_test_users()
        self.user1=User.objects.get(username="user1")
        self.scientist1=User.objects.get(username="scientist1")

    def test_get_photo_matches_species_response_with_photo(self):
        """
        Tests that get_photo_matches_species_response works.
        """
        # User logs a sighting
        sighting = load_test_sighting(user=self.user1, photo_url="a/photo")

        # Sighting gets assigned
        sighting.assign(self.scientist1)

        # Data scientists responses are saved
        responses = [c for c in SightingValidationCondition.objects.all()
                       if not c.section.is_radiogroup]
        responses.append(SightingValidationCondition.objects
            .get_sighting_matches_species_yes())
        ValidationResponse.objects.record_responses(sighting, responses)

        # Sighting is validated
        sighting.report_valid_with_photo(
            PHOTO_MATCHES_SPECIES_YES, "Good specimen", True)

        # Fetch the get_photo_matches_species_response
        self.assertEquals(
            PHOTO_MATCHES_SPECIES_YES,
            ValidationResponse.objects.get_photo_matches_species_response(sighting))

    def test_get_photo_matches_species_response_for_no_photo(self):
        """
        Tests that get_photo_matches_species_response works.
        """
        # User logs a sighting
        sighting = load_test_sighting(user=self.user1)

        # Sighting gets assigned
        sighting.assign(self.scientist1)

        # Data scientists responses are saved
        responses = []
        ValidationResponse.objects.record_responses(sighting, responses)

        # Sighting is validated
        sighting.report_invalid("Details didn't make sense")

        # Fetch the get_photo_matches_species_response
        self.assertIsNone(ValidationResponse.objects.get_photo_matches_species_response(sighting))
