
from django.contrib.auth.models import User
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users
from redmap.apps.redmapdb.models import *


class TestUserRoles(TestCase):

    def setUp(self):
        load_redmapdb_data()
        load_test_users()

    def test_user_roles(self):
        user = User.objects.get(username='user1')
        profile = user.get_profile()
        self.assertEqual(profile.is_regional_admin, False)
        self.assertEqual(profile.is_scientist, False)
        self.assertEqual(profile.is_site_admin, False)
        self.assertEqual(profile.is_global_admin, False)

    def test_scientist_roles(self):
        user = User.objects.get(username='scientist1')
        profile = user.get_profile()
        self.assertEqual(profile.is_regional_admin, False)
        self.assertEqual(profile.is_scientist, True)
        self.assertEqual(profile.is_site_admin, False)
        self.assertEqual(profile.is_global_admin, False)

    def test_regional_admin_roles(self):
        user = User.objects.get(username='regionaladmin1')
        profile = user.get_profile()
        self.assertEqual(profile.is_regional_admin, True)
        self.assertEqual(profile.is_scientist, True)  # TODO: should be false
        self.assertEqual(profile.is_site_admin, False)
        self.assertEqual(profile.is_global_admin, False)

    def test_admin_roles(self):
        user = User.objects.get(username='admin1')
        profile = user.get_profile()
        self.assertEqual(profile.is_regional_admin, False)
        self.assertEqual(profile.is_scientist, False)
        self.assertEqual(profile.is_site_admin, False)
        self.assertEqual(profile.is_global_admin, True)
