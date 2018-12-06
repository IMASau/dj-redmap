"""
Test accounts functionality
"""

from redmap.apps.cms.data import load_cms_data

from redmap.common.tests import GenericUrlTestCase, urlaccess, AnonymousUserTestCase,\
    UserTestCase, ScientistTestCase, RegionalAdminTestCase, AdminTestCase

from django.contrib.auth.models import User


class AccountsTestCase(object):

    def setUp(self):
        super(AccountsTestCase, self).setUp()
        load_cms_data()


class TestAnonymousUserAccess(GenericUrlTestCase, AccountsTestCase,
    AnonymousUserTestCase):

    test_urls = [
        urlaccess('/my-redmap/', False),
        urlaccess('/my-redmap/edit/', False),
        urlaccess('/my-redmap/view/user1/', True),
        urlaccess('/my-redmap/groups/', False),
        urlaccess('/accounts/login/', True),
        urlaccess('/accounts/password/change/', False),
    ]


class TestUserAccess(GenericUrlTestCase, AccountsTestCase, UserTestCase):

    test_urls = [
        urlaccess('/my-redmap/', True),
        urlaccess('/my-redmap/edit/', True),
        urlaccess('/my-redmap/view/user1/', True),
        urlaccess('/my-redmap/groups/', True),
        urlaccess('/accounts/login/', True),
        urlaccess('/accounts/password/change/', True),
    ]


class TestScientistAccess(GenericUrlTestCase, AccountsTestCase,
    ScientistTestCase):
    test_urls = [
        urlaccess('/my-redmap/', True),
        urlaccess('/my-redmap/edit/', True),
        urlaccess('/my-redmap/view/user1/', True),
        urlaccess('/my-redmap/groups/', True),
        urlaccess('/accounts/login/', True),
        urlaccess('/accounts/password/change/', True),
    ]


class TestRegionalAdminAccess(GenericUrlTestCase, AccountsTestCase,
    RegionalAdminTestCase):

    test_urls = [
        urlaccess('/my-redmap/', True),
        urlaccess('/my-redmap/edit/', True),
        urlaccess('/my-redmap/view/user1/', True),
        urlaccess('/my-redmap/groups/', True),
        urlaccess('/accounts/login/', True),
        urlaccess('/accounts/password/change/', True),
    ]


class TestAdminAccess(GenericUrlTestCase, AccountsTestCase, AdminTestCase):
    test_urls = [
        urlaccess('/my-redmap/', True),
        urlaccess('/my-redmap/edit/', True),
        urlaccess('/my-redmap/view/user1/', True),
        urlaccess('/my-redmap/groups/', True),
        urlaccess('/accounts/login/', True),
        urlaccess('/accounts/password/change/', True),
    ]
