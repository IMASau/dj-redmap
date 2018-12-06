"""
Test frontend functionality
"""

from redmap.common.tests import GenericUrlTestCase, urlaccess, AnonymousUserTestCase,\
    UserTestCase, ScientistTestCase, RegionalAdminTestCase, AdminTestCase
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from redmap.apps.redmapdb.models import Sighting, FBGroup
from redmap.apps.frontend.models import Faq, Sponsor, SponsorCategory
from redmap.apps.frontend.views import Homepage
from redmap.apps.cms.data import load_cms_data
# from redmap.apps.frontend.views import AddWizard
# from redmap.apps.frontend.views import region_landing_page
# from redmap.apps.frontend.views import SightingDetailView
# from redmap.apps.frontend.views import SpeciesInCategoryList
# from redmap.apps.frontend.views import Faqs
# from redmap.apps.frontend.views import Scientists
# from redmap.apps.frontend.views import Articles
# from redmap.apps.frontend.views import SpeciesDetailView
# from redmap.apps.frontend.views import NewsletterSignup
# from redmap.apps.frontend.views import render_cluster
# from redmap.apps.frontend.views import SightingsPhoto
# from redmap.apps.frontend.views import SightingsList
# from redmap.apps.frontend.views import SightingsMap
# from redmap.apps.frontend.views import SpeciesCategoryView
# from redmap.apps.frontend.views import GroupsList
# from redmap.apps.frontend.views import GroupView
# from redmap.apps.frontend.views import GroupEdit
# from redmap.apps.frontend.views import GroupDelete


class HomepageViewTest(TestCase):

    def setUp(self):
        """Setup some test data"""
        load_cms_data()

        # build a client for browser style requests
        self.client = Client()

        user=User.objects.create_user("bob", "123", "bob@example.com")

        # Unverified sighting
        Sighting.objects.create(
            id=1,
            user=user,
            sighting_date=u'2012-01-01',
            longitude=142.0,
            latitude=-42.0
        )

        # Verified sighting
        Sighting.objects.create(
            id=2,
            user=user,
            sighting_date=u'2012-01-01',
            is_verified_by_scientist=True,
            is_valid_sighting=True,
            photo_matches_species=True,
            photo_url=u'uploads/default.jpg',
            longitude=142.0,
            latitude=-42.0
        )

    def testHomepageLoads(self):

        # Fetch page
        response = self.client.get("/")

        # Check it loads
        self.assertEqual(response.status_code, 200)

        # Check context
        self.assertEqual('request' in response.context, True)
        self.assertEqual('photo_sightings' in response.context, True)
        self.assertEqual('sponsors' in response.context, True)
        self.assertEqual('recent_news' in response.context, True)

        photo_sightings_ids = [s.pk for s in response.context['photo_sightings']]
        self.assertEqual([2], photo_sightings_ids)

        # Check templates used
        template_names = [template.name for template in response.templates]
        self.assertIn('homepage.html', template_names)
        self.assertIn('site_base.html', template_names)

    def test_cant_see_unverified_sighting(self):
        """
        We should not be able to see unverified sightings
        """
        response = self.client.get("/sightings/1/")
        self.assertEqual(response.status_code, 404)

    def test_can_see_verified_sighting(self):
        """
        We should be able to see verified sightings
        """
        response = self.client.get("/sightings/2/")
        self.assertEqual(response.status_code, 200)

    def test_must_be_registered_to_log_a_sighting(self):
        """
        Check that unregistered users can not log sightings
        302 response expected - indicated we have been redirected
        """
        response = self.client.get("/sightings/add/")
        self.assertEqual(response.status_code, 302)

class FrontendTestCase(object):

    def setUp(self):
        super(FrontendTestCase, self).setUp()

        load_cms_data()

        Faq.objects.create(
            id = 1,
            title = 'Test FAQ',
            content = 'This is some example text',
        )

        FBGroup.objects.create(
            id = 1,
            description = 'This is a test group',
        )

        SponsorCategory.objects.create(
            id = 1,
            name = 'Test sponsor category'
        )

        Sponsor.objects.create(
            id = 1,
            name = 'Test Sponsor',
            image_url = '',
            is_major = True
        )


class TestAnonymousUserAccess(GenericUrlTestCase, FrontendTestCase,
    AnonymousUserTestCase):

    test_urls = [

        # Frontend views
        urlaccess('/', True),
        urlaccess('/sightings/', True),
        urlaccess('/sightings/latest/', True),
        urlaccess('/sightings/map/', True),
        urlaccess('/sightings/1/', True),
        urlaccess('/sightings/add/', False),
        urlaccess('/species/', True),
        urlaccess('/species/2/', True),
        urlaccess('/species/2/2/', True),
        urlaccess('/scientists/', True),
        urlaccess('/faq/', True),
        urlaccess('/articles/', True),
        urlaccess('/newsletter/', False),
        urlaccess('/render/cluster/12/', True),
        urlaccess('/region/nsw/', True),
        urlaccess('/groups/', True),
        urlaccess('/groups/view/1/', True),
        urlaccess('/groups/add/', False),
        urlaccess('/groups/edit/1/', False),
        urlaccess('/groups/delete/1/', False),

        # Backend views
        urlaccess('/panel/content/faq/', False),
        urlaccess('/panel/content/faq/add/', False),
        urlaccess('/panel/content/faq/edit/1/', False),
        urlaccess('/panel/content/faq/delete/1/', False),
        urlaccess('/panel/admin/sponsors/', False),
        urlaccess('/panel/admin/sponsors/add/', False),
        urlaccess('/panel/admin/sponsors/edit/1/', False),
        urlaccess('/panel/admin/sponsors/delete/1/', False),
        urlaccess('/panel/admin/sponsor_categories/', False),
        urlaccess('/panel/admin/sponsor_categories/add/', False),
        urlaccess('/panel/admin/sponsor_categories/edit/1/', False),
        urlaccess('/panel/admin/sponsor_categories/delete/1/', False),
    ]


class TestUserAccess(GenericUrlTestCase, FrontendTestCase, UserTestCase):

    test_urls = [

        # Frontend views
        urlaccess('/', True),
        urlaccess('/sightings/', True),
        urlaccess('/sightings/latest/', True),
        urlaccess('/sightings/map/', True),
        urlaccess('/sightings/1/', True),
        urlaccess('/sightings/add/', True),
        urlaccess('/species/', True),
        urlaccess('/species/2/', True),
        urlaccess('/species/2/2/', True),
        urlaccess('/scientists/', True),
        urlaccess('/faq/', True),
        urlaccess('/articles/', True),
        urlaccess('/newsletter/', True),
        urlaccess('/render/cluster/12/', True),
        urlaccess('/region/nsw/', True),
        urlaccess('/groups/', True),
        urlaccess('/groups/view/1/', True),
        urlaccess('/groups/add/', True),
        urlaccess('/groups/edit/1/', True),
        urlaccess('/groups/delete/1/', True),

        # Backend views
        urlaccess('/panel/content/faq/', False),
        urlaccess('/panel/content/faq/add/', False),
        urlaccess('/panel/content/faq/edit/1/', False),
        urlaccess('/panel/content/faq/delete/1/', False),
        urlaccess('/panel/admin/sponsors/', False),
        urlaccess('/panel/admin/sponsors/add/', False),
        urlaccess('/panel/admin/sponsors/edit/1/', False),
        urlaccess('/panel/admin/sponsors/delete/1/', False),
        urlaccess('/panel/admin/sponsor_categories/', False),
        urlaccess('/panel/admin/sponsor_categories/add/', False),
        urlaccess('/panel/admin/sponsor_categories/edit/1/', False),
        urlaccess('/panel/admin/sponsor_categories/delete/1/', False),
    ]


class TestScientistAccess(GenericUrlTestCase, FrontendTestCase, ScientistTestCase):
    test_urls = [

        # Frontend views
        urlaccess('/', True),
        urlaccess('/sightings/', True),
        urlaccess('/sightings/latest/', True),
        urlaccess('/sightings/map/', True),
        urlaccess('/sightings/1/', True),
        urlaccess('/sightings/add/', True),
        urlaccess('/species/', True),
        urlaccess('/species/2/', True),
        urlaccess('/species/2/2/', True),
        urlaccess('/scientists/', True),
        urlaccess('/faq/', True),
        urlaccess('/articles/', True),
        urlaccess('/newsletter/', True),
        urlaccess('/render/cluster/12/', True),
        urlaccess('/region/nsw/', True),
        urlaccess('/groups/', True),
        urlaccess('/groups/view/1/', True),
        urlaccess('/groups/add/', True),
        urlaccess('/groups/edit/1/', True),
        urlaccess('/groups/delete/1/', True),

        # Backend views
        urlaccess('/panel/content/faq/', False),
        urlaccess('/panel/content/faq/add/', False),
        urlaccess('/panel/content/faq/edit/1/', False),
        urlaccess('/panel/content/faq/delete/1/', False),
        urlaccess('/panel/admin/sponsors/', False),
        urlaccess('/panel/admin/sponsors/add/', False),
        urlaccess('/panel/admin/sponsors/edit/1/', False),
        urlaccess('/panel/admin/sponsors/delete/1/', False),
        urlaccess('/panel/admin/sponsor_categories/', False),
        urlaccess('/panel/admin/sponsor_categories/add/', False),
        urlaccess('/panel/admin/sponsor_categories/edit/1/', False),
        urlaccess('/panel/admin/sponsor_categories/delete/1/', False),
    ]


class TestRegionalAdminAccess(GenericUrlTestCase, FrontendTestCase,
    RegionalAdminTestCase):

    test_urls = [

        # Frontend views
        urlaccess('/', True),
        urlaccess('/sightings/', True),
        urlaccess('/sightings/latest/', True),
        urlaccess('/sightings/map/', True),
        urlaccess('/sightings/1/', True),
        urlaccess('/sightings/add/', True),
        urlaccess('/species/', True),
        urlaccess('/species/2/', True),
        urlaccess('/species/2/2/', True),
        urlaccess('/scientists/', True),
        urlaccess('/faq/', True),
        urlaccess('/articles/', True),
        urlaccess('/newsletter/', True),
        urlaccess('/render/cluster/12/', True),
        urlaccess('/region/nsw/', True),
        urlaccess('/groups/', True),
        urlaccess('/groups/view/1/', True),
        urlaccess('/groups/add/', True),
        urlaccess('/groups/edit/1/', True),
        urlaccess('/groups/delete/1/', True),

        # Backend views
        urlaccess('/panel/content/faq/', False),
        urlaccess('/panel/content/faq/add/', False),
        urlaccess('/panel/content/faq/edit/1/', False),
        urlaccess('/panel/content/faq/delete/1/', False),
        urlaccess('/panel/admin/sponsors/', False),
        urlaccess('/panel/admin/sponsors/add/', False),
        urlaccess('/panel/admin/sponsors/edit/1/', False),
        urlaccess('/panel/admin/sponsors/delete/1/', False),
        urlaccess('/panel/admin/sponsor_categories/', False),
        urlaccess('/panel/admin/sponsor_categories/add/', False),
        urlaccess('/panel/admin/sponsor_categories/edit/1/', False),
        urlaccess('/panel/admin/sponsor_categories/delete/1/', False),
    ]


class TestAdminAccess(GenericUrlTestCase, FrontendTestCase, AdminTestCase):
    test_urls = [

        # Frontend views
        urlaccess('/', True),
        urlaccess('/sightings/', True),
        urlaccess('/sightings/latest/', True),
        urlaccess('/sightings/map/', True),
        urlaccess('/sightings/1/', True),
        urlaccess('/sightings/add/', True),
        urlaccess('/species/', True),
        urlaccess('/species/2/', True),
        urlaccess('/species/2/2/', True),
        urlaccess('/scientists/', True),
        urlaccess('/faq/', True),
        urlaccess('/articles/', True),
        urlaccess('/newsletter/', True),
        urlaccess('/render/cluster/12/', True),
        urlaccess('/region/nsw/', True),
        urlaccess('/groups/', True),
        urlaccess('/groups/view/1/', True),
        urlaccess('/groups/add/', True),
        urlaccess('/groups/edit/1/', True),
        urlaccess('/groups/delete/1/', True),

        # Backend views
        urlaccess('/panel/content/faq/', True),
        urlaccess('/panel/content/faq/add/', True),
        urlaccess('/panel/content/faq/edit/1/', True),
        urlaccess('/panel/content/faq/delete/1/', True),
        urlaccess('/panel/admin/sponsors/', True),
        urlaccess('/panel/admin/sponsors/add/', True),
        urlaccess('/panel/admin/sponsors/edit/1/', True),
        urlaccess('/panel/admin/sponsors/delete/1/', True),
        urlaccess('/panel/admin/sponsor_categories/', True),
        urlaccess('/panel/admin/sponsor_categories/add/', True),
        urlaccess('/panel/admin/sponsor_categories/edit/1/', True),
        urlaccess('/panel/admin/sponsor_categories/delete/1/', True),
    ]
