
from datetime import datetime
from django.contrib.auth.models import User, Group
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users, \
    load_test_sighting
from redmap.apps.redmapdb.models import *


class SightingTrackingTracking(TestCase):

    def setUp(self):
        load_redmapdb_data()
        load_test_users()

    def test_reassign_validation(self):
        sighting = load_test_sighting()
        scientist1 = User.objects.get(username="scientist1")
        scientist2 = User.objects.get(username="scientist2")
        with self.assertRaises(ObjectDoesNotExist):
            sighting.reassign(scientist1, "Automatic assignment")
        sighting.assign(scientist1, "Automatic assignment")
        sighting.reassign(scientist1, scientist2, "Passing to another expert")

    def test_assign_validation(self):
        sighting = load_test_sighting()
        scientist1 = User.objects.get(username="scientist1")
        sighting.assign(scientist1, "Automatic assignment")
        with self.assertRaises(Exception):
            sighting.assign(scientist1, "Automatic assignment")

    def test_reporting_invalid_sighting(self):

        # Setup environment
        scientist1 = User.objects.get(username="scientist1")
        sighting = load_test_sighting()

        # Should be initially unassigned
        self.assertEqual(sighting.is_assigned, False)

        # Assigning should generate a tracker
        sighting.assign(scientist1, "Automatic assignment")

        # Should now be assigned
        self.assertEqual(sighting.is_assigned, True)

        # Keep a reference to our tracker
        pk = sighting.tracker.pk

        # Check our tracker details
        self.assertEqual(sighting.tracker.person, scientist1)
        self.assertEqual(sighting.tracker.is_displayed_on_site, False)

        # Should be able to report invalid sighting
        sighting.report_invalid("It's an unverifiable sighting.")

        # Check that get_latest_tracker returns our report
        self.assertEqual(pk, SightingTracking.objects.get_latest_tracker(sighting).pk)

        # Sighting note should be visible
        self.assertEqual(
            sighting.sighting_tracking.get(pk=pk).is_displayed_on_site, False)

    def test_reporting_valid_sighting(self):

        # Setup environment
        scientist1 = User.objects.get(username="scientist1")
        sighting = load_test_sighting()

        # Should be initially unassigned
        self.assertEqual(sighting.is_assigned, False)

        # Assigning should generate a tracker
        sighting.assign(scientist1, "Automatic assignment")

        # Searching sighting_tracking lists
        self.assertIn(
            sighting.tracker, SightingTracking.active_assignments.all())
        self.assertNotIn(
            sighting.tracker, SightingTracking.valid_sightings.all())
        self.assertNotIn(
            sighting.tracker, SightingTracking.invalid_sightings.all())
        self.assertNotIn(
            sighting.tracker, SightingTracking.spam_sightings.all())

        # Should now be assigned
        self.assertEqual(sighting.is_assigned, True)

        # Keep a reference to our tracker
        pk = sighting.tracker.pk

        # Check our tracker details
        self.assertEqual(sighting.tracker.person, scientist1)
        self.assertEqual(sighting.tracker.is_displayed_on_site, False)

        # Should be able to report valid sighting
        sighting.report_valid_without_photo("It's a healthy specimine.", True)

        # Grab the current sighting_tracking instance
        tracker = sighting.sighting_tracking.get(pk=pk)

        # Sighting note should be visible
        self.assertEqual(tracker.is_displayed_on_site, True)

        # Searching sighting_tracking again
        self.assertNotIn(tracker, SightingTracking.active_assignments.all())
        self.assertIn(tracker, SightingTracking.valid_sightings.all())
        self.assertNotIn(tracker, SightingTracking.invalid_sightings.all())
        self.assertNotIn(tracker, SightingTracking.spam_sightings.all())

        # Should now be unassigned
        self.assertEqual(sighting.is_assigned, False)

        # Should not be able to report valid sighting now
        with self.assertRaises(ObjectDoesNotExist):
            sighting.report_valid_without_photo(
                "(private note: user=loser).", False)

    def test_reassigning_and_reporting_spam(self):

        # Setup environment
        scientist1 = User.objects.get(username="scientist1")
        scientist2 = User.objects.get(username="scientist2")
        sighting = load_test_sighting()

        # Should be initially unassigned
        self.assertEqual(sighting.is_assigned, False)

        # Assigning should generate a tracker
        sighting.assign(scientist1, "Automatic assignment")

        # Should now be assigned
        self.assertEqual(sighting.is_assigned, True)
        self.assertEqual(sighting.tracker.person, scientist1)

        # Reassign to another user
        sighting.reassign(scientist1, scientist2, "Sending to someone better skilled to verify")

        self.assertEqual(sighting.is_assigned, True)
        self.assertEqual(sighting.tracker.person, scientist2)

        # Report as spam
        sighting.report_spam("Photo is junk")
        self.assertEqual(sighting.is_assigned, False)
        self.assertEqual(sighting.is_published, False)
