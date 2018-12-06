"""
Test CMS functionality
"""

from redmap.common.tests import GenericUrlTestCase, urlaccess, AnonymousUserTestCase,\
    UserTestCase, ScientistTestCase, RegionalAdminTestCase, AdminTestCase

from redmap.apps.cms.data import load_cms_data
from redmap.apps.cms.models import CopyBlock, Page, SitewideContent
from redmap.apps.cms.utils import cached_copy

from django.test import TestCase


class CmsTestCase(object):

    def setUp(self):
        super(CmsTestCase, self).setUp()

        load_cms_data()

        root = Page(title='Test Book', slug='test-book', content='Hello')
        root.save()

        page = Page(title='Test Page', slug='test-page', content='Test page',
            parent=root)
        page.save()

        CopyBlock.objects.create(
            id=1,
            slug='test-block',
            text='This is a test copy block')


class CachedCopyTest(CmsTestCase, TestCase):
    """
    Check that the CachedCopyHelper works properly
    """

    def setUp(self):
        super(CachedCopyTest, self).setUp()
        cached_copy.clear_all()

    def test_fetch_singletons(self):
        sitewide = SitewideContent.objects.get(pk=1)

        self.assertEqual(cached_copy['site'], sitewide)

    def test_does_cache(self):
        with self.assertNumQueries(1, msg_prefix="Only hit the database once"):
            sitewide_1 = cached_copy['site']
            sitewide_2 = cached_copy['site']

        self.assertEqual(sitewide_1, sitewide_2,
            "The same database object is returned")

    def test_update_on_save(self):
        sitewide = SitewideContent.objects.get(pk=1)

        sitewide.site_title = 'version 1'
        sitewide.save()

        sitewide_1 = cached_copy['site']
        self.assertEqual(sitewide_1.site_title, 'version 1',
            "The new instance has the updated content")

        sitewide.site_title = 'version 2'
        sitewide.save()

        sitewide_2 = cached_copy['site']
        self.assertEqual(sitewide_2.site_title, 'version 2',
            "The new instance has the updated content")

        self.assertEqual(sitewide_1.pk, sitewide_2.pk,
            "The model instances represent the same database object")


class TestAnonymousUserAccess(GenericUrlTestCase, CmsTestCase,
    AnonymousUserTestCase):

    test_urls = [
        urlaccess('/page/test-page', True),
        urlaccess('/panel/content/books/', False),
        urlaccess('/panel/content/books/add/', False),
        urlaccess('/panel/content/books/1/', False),
        urlaccess('/panel/content/books/1/edit/', False),
        urlaccess('/panel/content/books/1/edit/2/', False),
        urlaccess('/panel/content/books/1/delete/1/', False),
        urlaccess('/panel/content/homepage/', False),
        urlaccess('/panel/content/blocks/', False),
        urlaccess('/panel/content/blocks/add/', False),
        urlaccess('/panel/content/blocks/edit/1/', False),
        urlaccess('/panel/content/blocks/delete/1/', False),
    ]


class TestUserAccess(GenericUrlTestCase, CmsTestCase, UserTestCase):

    test_urls = [
        urlaccess('/page/test-page', True),
        urlaccess('/panel/content/books/', False),
        urlaccess('/panel/content/books/add/', False),
        urlaccess('/panel/content/books/1/', False),
        urlaccess('/panel/content/books/1/edit/', False),
        urlaccess('/panel/content/books/1/edit/2/', False),
        urlaccess('/panel/content/books/1/delete/1/', False),
        urlaccess('/panel/content/homepage/', False),
        urlaccess('/panel/content/blocks/', False),
        urlaccess('/panel/content/blocks/add/', False),
        urlaccess('/panel/content/blocks/edit/1/', False),
        urlaccess('/panel/content/blocks/delete/1/', False),
    ]


class TestScientistAccess(GenericUrlTestCase, CmsTestCase, ScientistTestCase):
    test_urls = [
        urlaccess('/page/test-page', True),
        urlaccess('/panel/content/books/', False),
        urlaccess('/panel/content/books/add/', False),
        urlaccess('/panel/content/books/1/', False),
        urlaccess('/panel/content/books/1/edit/', False),
        urlaccess('/panel/content/books/1/edit/2/', False),
        urlaccess('/panel/content/books/1/delete/1/', False),
        urlaccess('/panel/content/homepage/', False),
        urlaccess('/panel/content/blocks/', False),
        urlaccess('/panel/content/blocks/add/', False),
        urlaccess('/panel/content/blocks/edit/1/', False),
        urlaccess('/panel/content/blocks/delete/1/', False),
    ]


class TestRegionalAdminAccess(GenericUrlTestCase, CmsTestCase,
    RegionalAdminTestCase):

    test_urls = [
        urlaccess('/page/test-page', True),
        urlaccess('/panel/content/books/', True),
        urlaccess('/panel/content/books/add/', False),
        urlaccess('/panel/content/books/1/', True),
        urlaccess('/panel/content/books/1/edit/', False),
        urlaccess('/panel/content/books/1/edit/2/', True),
        urlaccess('/panel/content/books/1/delete/1/', True),
        urlaccess('/panel/content/homepage/', False),
        urlaccess('/panel/content/blocks/', False),
        urlaccess('/panel/content/blocks/add/', False),
        urlaccess('/panel/content/blocks/edit/1/', False),
        urlaccess('/panel/content/blocks/delete/1/', False),
    ]


class TestAdminAccess(GenericUrlTestCase, CmsTestCase, AdminTestCase):
    test_urls = [
        urlaccess('/page/test-page', True),
        urlaccess('/panel/content/books/', True),
        urlaccess('/panel/content/books/add/', True),
        urlaccess('/panel/content/books/1/', True),
        urlaccess('/panel/content/books/1/edit/', True),
        urlaccess('/panel/content/books/1/edit/2/', True),
        urlaccess('/panel/content/books/1/delete/1/', True),
        urlaccess('/panel/content/homepage/', True),
        urlaccess('/panel/content/blocks/', True),
        urlaccess('/panel/content/blocks/add/', True),
        urlaccess('/panel/content/blocks/edit/1/', True),
        urlaccess('/panel/content/blocks/delete/1/', True),
    ]
