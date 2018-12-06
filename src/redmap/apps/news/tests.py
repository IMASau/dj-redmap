"""
Test news functionality
"""

from redmap.common.tests import GenericUrlTestCase, urlaccess, AnonymousUserTestCase,\
    UserTestCase, ScientistTestCase, RegionalAdminTestCase, AdminTestCase

from datetime import datetime
from django.contrib.sites.models import Site
from zinnia.managers import PUBLISHED
from zinnia.models import Category, Entry


class NewsTestCase(object):

    def setUp(self):
        super(NewsTestCase, self).setUp()

        current_site = Site.objects.get_current()

        entry = Entry(
            title = 'Test News',
            slug = 'test-news',
            content = 'Test content of this test news item.',
            excerpt = 'Test content...',
            tags = 'Redmap,',
            status = PUBLISHED,
            creation_date = datetime(2012, 10, 30, 12, 30),
        )

        entry.save()

        news_category, created = Category.objects.get_or_create(slug='news')
        entry.categories.add(news_category)

        entry.sites.add(current_site)

        entry.save()

        article = Entry(
            title = 'Test Article',
            slug = 'test-article',
            content = 'Test content of this test article.',
            excerpt = 'Test content...',
            tags = 'Redmap,',
            status = PUBLISHED,
            creation_date = datetime(2012, 10, 30, 12, 30),
        )

        article.save()

        articles_category, created = Category.objects.get_or_create(
            slug='articles'
        )
        article.categories.add(articles_category)

        article.sites.add(current_site)

        article.save()


class TestAnonymousUserAccess(GenericUrlTestCase,
    NewsTestCase, AnonymousUserTestCase):

    test_urls = [
        urlaccess('/news/2012/10/30/test-news/', True),
        urlaccess('/panel/content/news/', False),
        urlaccess('/panel/content/news/add/', False),
        urlaccess('/panel/content/news/edit/1/', False),
        urlaccess('/panel/content/news/delete/1/', False),
        urlaccess('/article/test-article/', True),
        urlaccess('/panel/content/articles/', False),
        urlaccess('/panel/content/articles/add/', False),
        urlaccess('/panel/content/articles/edit/2/', False),
        urlaccess('/panel/content/articles/delete/2/', False),
    ]


class TestUserAccess(GenericUrlTestCase, NewsTestCase, UserTestCase):
    test_urls = [
        urlaccess('/news/2012/10/30/test-news/', True),
        urlaccess('/panel/content/news/', False),
        urlaccess('/panel/content/news/add/', False),
        urlaccess('/panel/content/news/edit/1/', False),
        urlaccess('/panel/content/news/delete/1/', False),
        urlaccess('/article/test-article/', True),
        urlaccess('/panel/content/articles/', False),
        urlaccess('/panel/content/articles/add/', False),
        urlaccess('/panel/content/articles/edit/2/', False),
        urlaccess('/panel/content/articles/delete/2/', False),
    ]


class TestScientistAccess(GenericUrlTestCase, NewsTestCase, ScientistTestCase):
    test_urls = [
        urlaccess('/news/2012/10/30/test-news/', True),
        urlaccess('/panel/content/news/', False),
        urlaccess('/panel/content/news/add/', False),
        urlaccess('/panel/content/news/edit/1/', False),
        urlaccess('/panel/content/news/delete/1/', False),
        urlaccess('/article/test-article/', True),
        urlaccess('/panel/content/articles/', False),
        urlaccess('/panel/content/articles/add/', False),
        urlaccess('/panel/content/articles/edit/2/', False),
        urlaccess('/panel/content/articles/delete/2/', False),
    ]


class TestRegionalAdminAccess(GenericUrlTestCase, NewsTestCase,
    RegionalAdminTestCase):
    test_urls = [
        urlaccess('/news/2012/10/30/test-news/', True),
        urlaccess('/panel/content/news/', True),
        urlaccess('/panel/content/news/add/', True),
        urlaccess('/panel/content/news/edit/1/', True),
        urlaccess('/panel/content/news/delete/1/', True),
        urlaccess('/article/test-article/', True),
        urlaccess('/panel/content/articles/', True),
        urlaccess('/panel/content/articles/add/', True),
        urlaccess('/panel/content/articles/edit/2/', True),
        urlaccess('/panel/content/articles/delete/2/', True),
    ]


class TestAdminAccess(GenericUrlTestCase, NewsTestCase, AdminTestCase):
    test_urls = [
        urlaccess('/news/2012/10/30/test-news/', True),
        urlaccess('/panel/content/news/', True),
        urlaccess('/panel/content/news/add/', True),
        urlaccess('/panel/content/news/edit/1/', True),
        urlaccess('/panel/content/news/delete/1/', True),
        urlaccess('/article/test-article/', True),
        urlaccess('/panel/content/articles/', True),
        urlaccess('/panel/content/articles/add/', True),
        urlaccess('/panel/content/articles/edit/2/', True),
        urlaccess('/panel/content/articles/delete/2/', True),
    ]
