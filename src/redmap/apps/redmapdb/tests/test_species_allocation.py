"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from datetime import datetime
from django.contrib.auth.models import User, Group
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users, \
    load_test_sighting
from redmap.apps.redmapdb.models import *
from redmap.apps.redmapdb.utils import find_region


def set_availability(user, is_avail):
    profile = user.profile
    profile.is_available = is_avail
    profile.save()


class TestSpeciesAllocation(TestCase):

    def setUp(self):
        load_redmapdb_data()
        load_test_users()

    def log_photo_sighting(self, **kwargs):
        return load_test_sighting(photo_url="test.jpg", **kwargs)

    def log_swansea_sighting(self, *args, **kwargs):
        return self.log_photo_sighting(
            latitude=-42.1278, longitude=148.0761, **kwargs)

    def log_perth_sighting(self, *args, **kwargs):
        return self.log_photo_sighting(
            latitude=-31.9554, longitude=115.8585, **kwargs)

    def log_sydney_sighting(self, *args, **kwargs):
        return self.log_photo_sighting(
            latitude=-33.8683, longitude=151.2086, **kwargs)

    def test_expert_allocations(self):

        s1, s2, s3, s4 = Species.objects.all()[0:4]

        r1 = Region.objects.get(description="Tasmania")
        r2 = Region.objects.get(description="New South Wales")
        r3 = Region.objects.get(description="Western Australia")
        r4 = Region.objects.get(description="Victoria")

        # make users
        a1 = User.objects.get(username='admin1')
        e1 = User.objects.get(username='scientist1')
        e2 = User.objects.get(username='scientist2')
        e3 = User.objects.get(username='scientist3')
        ra2 = User.objects.get(username='regionaladmin1')
        u1 = User.objects.get(username='user1')

        # assign to NSW region
        AdministratorAllocation(region=r2, person=ra2).save()

        # make some sightings
        f1 = self.log_swansea_sighting(species=s1, user=u1)
        f2 = self.log_sydney_sighting(species=s2, user=u1)
        f3 = self.log_perth_sighting(species=s3, user=u1)

        # clear assignments
        SpeciesAllocation.objects.all().delete()

        # add assignments for species 1 in different regions to different
        # scientist
        SpeciesAllocation(
            species=s1, region=r1, person=e1, contact_in_range=True).save()
        SpeciesAllocation(
            species=s1, region=r2, person=e2, contact_in_range=True).save()
        SpeciesAllocation(
            species=s1, region=r3, person=e3, contact_in_range=True).save()

        # add global assignment for species 2 to expert 2
        SpeciesAllocation(
            species=s2, region=None, person=e2, contact_in_range=True).save()

        # add global out_of_range assignment for species 3 to expert 3
        SpeciesAllocation(
            species=s3, region=r3, person=e3, contact_in_range=False).save()

        # check we can see all assignments
        self.assertEqual(SpeciesAllocation.objects.count(), 5)
        set_availability(e1, True)

        # check species_match works
        self.assertEqual(
            SpeciesAllocation.objects.species_match(s1).count(), 3)

        # check region_match works
        self.assertEqual(
            SpeciesAllocation.objects.region_match(r1).count(), 2)
        self.assertEqual(
            SpeciesAllocation.objects.region_match(r2).count(), 2)
        self.assertEqual(
            SpeciesAllocation.objects.region_match(r3).count(), 3)
        self.assertEqual(
            SpeciesAllocation.objects.region_match(None).count(), 1)

        # check range_filter works
        is_out_of_range = True
        is_trusted_user = True
        self.assertEqual(
            SpeciesAllocation.objects.range_filter(is_out_of_range).count(),
            5)
        self.assertEqual(
            SpeciesAllocation.objects.range_filter(
                not is_out_of_range).count(),
            4)

        # find match by sighting
        r_ = None  # no region match

        # unexpected s1 sighting in r1 => e1
        self.assertEqual(
            SpeciesAllocation.objects.find_experts(
                s1, r1, is_out_of_range, not is_trusted_user).count(),
            1)

        # unexpected s2 sighting in r1 => e2
        self.assertEqual(
            SpeciesAllocation.objects.find_experts(
                s2, r1, is_out_of_range, not is_trusted_user).count(),
            1)

        # typical s2 sighting in r1 => e2
        self.assertEqual(
            SpeciesAllocation.objects.find_experts(
                s2, r1, not is_out_of_range, not is_trusted_user).count(),
            1)

        # typical s3 sighting in r3 => no matches
        self.assertEqual(
            SpeciesAllocation.objects.find_experts(
                s3, r3, not is_out_of_range, not is_trusted_user).count(),
            0)

        # unexpected s3 sighting in r3 => e3
        self.assertEqual(
            SpeciesAllocation.objects.find_experts(
                s3, r3, is_out_of_range, not is_trusted_user).count(), 1)

        # test expert picking
        self.assertEqual(f1.pick_expert().pk, e1.pk)
        self.assertEqual(f2.pick_expert().pk, e2.pk)
        self.assertEqual(f3.pick_expert().pk, e3.pk)

        # flex fallback to global admin
        f4 = Sighting.objects.quick_log(
            species=s4, latitude=-31.9554, longitude=115.8585) # Perth
        self.assertEqual(f4.pick_expert(), a1)

        # test regional admin fallback for species with no associated
        # allocations
        f5 = self.log_sydney_sighting(species=s4)
        self.assertEqual(f5.pick_expert(), ra2)

        # test fallback to global expert
        self.assertEqual(
            self.log_perth_sighting(species=s2).pick_expert(), e2)

        # TODO: test filtering trusted user sightings

    # TODO: test trusted user sightings visible by default

    def test_default_routing(self):
        """
        If no allocation matches, route to global administrator
        """
        # clear all allocations
        SpeciesAllocation.objects.all().delete()
        # find expert
        # expert = SpeciesAllocation.objects.get_next_expert(sighting)


    def test_allocation_fairness(self):

        species = Species.objects.all()[0]
        region = Region.objects.get(slug="tas")
        scientist1 = User.objects.get(username="scientist1")
        scientist2 = User.objects.get(username="scientist2")

        s1, s2, s3, s4 = [
            load_test_sighting(
                latitude= -42.1278,
                longitude= 148.0761,
                species= species,
                photo_url= "a/photo")
            for x in range(4)]

        SpeciesAllocation.objects.all().delete()
        for person in [scientist1, scientist2]:
            SpeciesAllocation.objects.create(
                species=species, region=region, person=person,
                contact_in_range=True)

        # Give scientist1 an assignment
        s1.assign(scientist1)

        # Make sure scientist2 is next choice
        self.assertEqual(s2.pick_expert(), scientist2)

        # Give scientist2 two assignments
        s2.assign(scientist2)
        s3.assign(scientist2)

        # Make sure next choice is scientist1
        self.assertEqual(s4.pick_expert(), scientist1)
