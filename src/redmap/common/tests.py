"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from collections import namedtuple

from django.test import TestCase
from django.conf import settings

from django.contrib.auth.models import User, Group

from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users, \
    load_test_sighting


class PermissionTestCase(TestCase):
    """
    Base TestCase for testing views protected by the auth system
    """

    login_url = settings.LOGIN_URL

    def assertAccess(self, url, access, message=None):
        """
        Assert that a request to a url succeeds (200 response) or fails (302
        response).
        """
        response = self.client.get(url, follow=True)

        if message is None:
            message = 'Test {0} {1} access {2}'.format(
                self.user.username if hasattr(self, 'user') else 'user',
                'can' if access else 'can not',
                url)

        redirected_url = '{0}?next={1}'.format(self.login_url, url)
        if access:
            self.assertEqual(response.redirect_chain, [], message)
        else:
            self.assertRedirects(response, redirected_url, msg_prefix=message)

    def assertCanAccess(self, url, message):
        """
        Assert that a request to a url succeeds with a 200 response
        """
        self.assertAccess(url, True, message)

    def assertCanNotAccess(self, url, message):
        """
        Assert that a request to a url fails with a 302 response
        """
        self.assertAccess(url, False, message)


urlaccess = namedtuple('UrlAccess', ['url', 'accessible'])


class GenericUrlTestCase(object):
    """
    Automatically test a bunch of urls to see if a user has access rights.
    Define the urls as a list on the `test_urls` property.

    Combined with one of the User/Scientist/Admin/etc TestCase classes below,
    this provides a very quick and easy way of testing user access to many urls
    quickly.

    >>> ExampleTestCase(GenericUrlTestCase, UserTestCase):
            test_urls = [
                # A normal user should be able to access /page/
                urlaccess('/page/', True),
                # A normal user should not be able to access /panel/
                urlaccess('/panel/', False),
            ]
    """

    test_urls = None

    def test_access(self):

        for page in self.test_urls:
            self.assertAccess(page.url, page.accessible)


class AnonymousUserTestCase(PermissionTestCase):

    def setUp(self):
        super(AnonymousUserTestCase, self).setUp()

        load_redmapdb_data()
        load_test_users()


class UserTestCase(PermissionTestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()

        load_redmapdb_data()
        load_test_users()

        self.user = User.objects.get(username='user1')
        self.assertTrue(
            self.client.login(username='user1', password='u1'),
            "Can log in")


class ScientistTestCase(PermissionTestCase):

    def setUp(self):
        super(ScientistTestCase, self).setUp()

        load_redmapdb_data()
        load_test_users()

        self.user = User.objects.get(username='scientist1')
        self.assertTrue(
            self.client.login(username='scientist1', password='s1'),
            "Can log in")


class RegionalAdminTestCase(PermissionTestCase):

    def setUp(self):
        super(RegionalAdminTestCase, self).setUp()

        load_redmapdb_data()
        load_test_users()

        self.user = User.objects.get(username='regionaladmin1')
        self.assertTrue(
            self.client.login(username='regionaladmin1', password='ra1'),
            "Can log in")


class SiteAdminTestCase(PermissionTestCase):

    def setUp(self):
        super(SiteAdminTestCase, self).setUp()

        load_redmapdb_data()
        load_test_users()

        self.user = User.objects.get(username='siteadmin1')
        self.assertTrue(
            self.client.login(username='siteadmin1', password='sa1'),
            "Can log in")


class AdminTestCase(PermissionTestCase):

    def setUp(self):
        super(AdminTestCase, self).setUp()

        load_redmapdb_data()
        load_test_users()

        self.user = User.objects.get(username='admin1')
        self.assertTrue(
            self.client.login(username='admin1', password='a1'),
            "Can log in")
