from datetime import datetime
from django.contrib.auth.models import User, Group
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users, \
    load_test_sighting
from redmap.apps.redmapdb.models import *


class SightingTests(TestCase):

    def setUp(self):
        load_redmapdb_data()
        load_test_users()

        self.user1 = User.objects.get(username="user1")
        self.scientist1 = User.objects.get(username="scientist1")

    def test_log_with_data(self):
        """
        Check the api for logging sightings works
        """

        data = {
            'latitude': -42.1278,
            'longitude': 148.0761,
            'region': Region.objects.all()[0],
            'species': Species.objects.all()[0],
            'sighting_date': datetime.now(),
            'time': Time.objects.all()[0]}
        
        Sighting.objects.log_with_data(self.user1, data)

        data['photo_url'] = "the/photo.jpg"
        Sighting.objects.log_with_data(self.user1, data)

    def test_get_public_photo(self):
        # start with sightings
        Sighting.objects.all().delete()
        self.assertEqual(Sighting.objects.get_public_photo().count(), 0)

        # log a sighting
        sighting1 = load_test_sighting()
        self.assertEqual(Sighting.objects.get_public_photo().count(), 0)

        # log a sighting with photo
        sighting1 = load_test_sighting(photo_url="test")
        self.assertEqual(Sighting.objects.get_public_photo().count(), 0)

        # log another and mark it as invalid
        sighting2 = load_test_sighting(photo_url="test")
        sighting2.assign(self.scientist1)
        sighting2.report_invalid("Not able to verify")
        self.assertEqual(Sighting.objects.get_public_photo().count(), 0)

        # log another and mark it as valid
        sighting3 = load_test_sighting(photo_url="test")
        sighting3.assign(self.scientist1)
        sighting3.report_valid_with_photo(PHOTO_MATCHES_SPECIES_YES, "Looks good", True)
        self.assertEqual(Sighting.objects.get_public_photo().count(), 1)

        # log another and mark it as valid
        sighting4 = load_test_sighting(photo_url="test")
        sighting4.assign(self.scientist1)
        sighting4.report_valid_with_photo(PHOTO_MATCHES_SPECIES_MAYBE,
            "Valid but photo isn't clear", True)
        self.assertEqual(Sighting.objects.get_public_photo().count(), 1)

        # log another and mark it as valid
        sighting5 = load_test_sighting(photo_url="test")
        sighting5.assign(self.scientist1)
        sighting5.report_valid_with_photo(PHOTO_MATCHES_SPECIES_NO,
            "Valid but photo isn't of any use", True)
        self.assertEqual(Sighting.objects.get_public_photo().count(), 1)

    def test_get_recent(self):

        # Create a bunch of valid photo sightings to query
        for x in range(10):
            for species in Species.objects.all()[0:3]:
                sighting = load_test_sighting(
                    species=species, photo_url="some/url")
                sighting.assign(self.scientist1)
                sighting.report_valid_with_photo(
                    PHOTO_MATCHES_SPECIES_YES, "", True)

        # ...and a bunch of other_species sightings
        for x in range(10):
            for other_species in ["DogFish", "CatFish"]:
                sighting = load_test_sighting(
                    species=None, other_species=other_species,
                    photo_url="some/url")
                sighting.assign(self.scientist1)
                sighting.report_valid_with_photo(
                    PHOTO_MATCHES_SPECIES_YES, "", True)

        # Should get 3 results for basic case
        self.assertEqual(Sighting.objects.get_recent().count(), 3)

        # Should not include the species selected to filter
        sightings = Sighting.objects.get_recent()
        s1 = sightings[0]
        self.assertNotIn(s1, Sighting.objects.get_recent(s1))

        # Should all match species provided as filter
        s2 = Sighting.objects.exclude(species__isnull=True)[0]
        self.assertEquals(
            [s2.species.pk]*3,
            [s.species.pk for s in Sighting.objects.get_recent(s2)])

        # Or should all match other_species provided as filter
        s3 = Sighting.objects.filter(other_species="DogFish")[0]
        self.assertNotIn(s3, Sighting.objects.get_recent(s3))
        self.assertEquals(
            [s3.other_species]*3,
            [s.other_species for s in Sighting.objects.get_recent(s3)])

    def test_get_public(self):
        # start with sightings
        Sighting.objects.all().delete()
        self.assertEqual(Sighting.objects.get_public().count(), 0)

        # log a sighting
        sighting1 = load_test_sighting()
        self.assertEqual(Sighting.objects.get_public().count(), 0)

        # log another and mark it as spam
        sighting2 = load_test_sighting()
        sighting2.assign(self.scientist1)
        sighting2.report_spam("That's gross!")
        self.assertEqual(Sighting.objects.get_public().count(), 0)

        # log another and mark it as invalid
        sighting3 = load_test_sighting()
        sighting3.assign(self.scientist1)
        sighting3.report_invalid("I can't use this data")
        self.assertEqual(Sighting.objects.get_public().count(), 0)

        # log another and mark it as valid
        sighting4 = load_test_sighting()
        sighting4.assign(self.scientist1)
        sighting4.report_valid_without_photo(
            "Nice sighting", True)
        self.assertEqual(Sighting.objects.get_public().count(), 1)

        # log another and mark it as valid (but with hidden comment)
        sighting4 = load_test_sighting()
        sighting4.assign(self.scientist1)
        sighting4.report_valid_without_photo(
            "Nothing interesting to say", False)
        self.assertEqual(Sighting.objects.get_public().count(), 2)
