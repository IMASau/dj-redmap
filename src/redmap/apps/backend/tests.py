"""
Test that backend functionality works. This includes testing:

    * If a User can or can not access various views depending upon their group
"""

from redmap.apps.backend import views
from redmap.apps.cms.data import load_cms_data
from redmap.common.tests import GenericUrlTestCase, urlaccess, AnonymousUserTestCase,\
    UserTestCase, ScientistTestCase, RegionalAdminTestCase, AdminTestCase
from django.core.urlresolvers import reverse
from redmap.apps.redmapdb.data import load_test_sighting
from redmap.apps.redmapdb.models import Sighting, SpeciesAllocation, Species,\
    AdministratorAllocation
from redmap.apps.backend.models import SightingValidationRule, ValidationMessageTemplate,\
    SightingValidationCondition
from django.contrib.auth.models import User


class BackendTestBase(object):

    def setUp(self):
        super(BackendTestBase, self).setUp()
        load_cms_data()

class AnonymousUserTest(BackendTestBase, AnonymousUserTestCase):

    def setUp(self):
        super(AnonymousUserTest, self).setUp()

        load_test_sighting()

    def test_can_not_verify_signting(self):
        self.assertCanNotAccess(
            reverse(views.scientist_verify_wizard, args=[1]),
            'Anonymous user can not start sighting verification wizard')


class UserTest(BackendTestBase, UserTestCase):

    def setUp(self):
        super(UserTest, self).setUp()

        load_test_sighting()

    def test_can_not_verify_signting(self):
        self.assertCanNotAccess(
            reverse(views.scientist_verify_wizard, args=[1]),
            'User can not start sighting verification wizard')


class ScientistTest(BackendTestBase, ScientistTestCase):

    def setUp(self):
        super(ScientistTest, self).setUp()

        load_test_sighting()

    def test_can_verify_signting(self):
        self.assertCanAccess(
            reverse(views.scientist_verify_wizard, args=[1]),
            'Scientist can start sighting verification wizard')


class RegionalAdminTest(BackendTestBase, RegionalAdminTestCase):

    def setUp(self):
        super(RegionalAdminTest, self).setUp()

        load_test_sighting()

    def test_can_not_verify_signting(self):
        self.assertCanAccess(
            reverse(views.scientist_verify_wizard, args=[1]),
            'Regional admin can start sighting verification wizard')


class AdminTest(BackendTestBase, AdminTestCase):

    def setUp(self):
        super(AdminTest, self).setUp()

        load_test_sighting()

    def test_can_not_verify_signting(self):
        self.assertCanAccess(
            reverse(views.scientist_verify_wizard, args=[1]),
            'Admin can start sighting verification wizard')


class BackendTestCase(BackendTestBase, object):

    def setUp(self):
        super(BackendTestCase, self).setUp()

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
            is_photo_appropriate=True,
            photo_matches_species=True,
            photo_url=u'uploads/default.jpg',
            longitude=142.0,
            latitude=-42.0
        )

        SpeciesAllocation.objects.create(
            id = 1,
            species = Species.objects.get(pk=1),
            person = user

        )

        AdministratorAllocation.objects.create(
            id = 1,
            person = user,
        )

        SightingValidationCondition.objects.create(
            id = 1,
            name = 'Test condition',
            step = 1
        )

        ValidationMessageTemplate.objects.create(
            id = 1,
            name = 'Test template',
            template = 'This is the template.'
        )

        SightingValidationRule.objects.create(
            id = 1,
            name = 'Test rule',
            rank = 1,
            valid_photo = True,
            valid_sighting = True,
            validation_message_template =\
                ValidationMessageTemplate.objects.get(pk=1)
        )


class TestAnonymousUserAccess(GenericUrlTestCase, BackendTestCase,
    AnonymousUserTestCase):

    test_urls = [
        urlaccess('/panel/', False),
        urlaccess('/panel/verify/1/', False),
        urlaccess('/panel/sightings/', False),
        urlaccess('/panel/sightings/all/', False),
        urlaccess('/panel/sightings/edit/1/', False),
        urlaccess('/panel/sightings/delete/1/', False),
        urlaccess('/panel/sightings/reassign/1/', False),
        urlaccess('/panel/sightings/spam/1/', False),
        urlaccess('/panel/experts/assignments/', False),
        urlaccess('/panel/experts/assignments/add/', False),
        urlaccess('/panel/experts/assignments/edit/1/', False),
        urlaccess('/panel/experts/assignments/delete/1/', False),
        urlaccess('/panel/experts/allocations/', False),
        urlaccess('/panel/experts/allocations/add/', False),
        urlaccess('/panel/experts/allocations/edit/1/', False),
        urlaccess('/panel/experts/allocations/delete/1/', False),
        urlaccess('/panel/experts/rules/', False),
        urlaccess('/panel/experts/rules/add/', False),
        urlaccess('/panel/experts/rules/edit/1/', False),
        urlaccess('/panel/experts/rules/delete/1/', False),
        urlaccess('/panel/experts/templates/', False),
        urlaccess('/panel/experts/templates/add/', False),
        urlaccess('/panel/experts/templates/edit/1/', False),
        urlaccess('/panel/experts/templates/delete/1/', False),
        urlaccess('/panel/experts/conditions/', False),
        urlaccess('/panel/experts/conditions/add/', False),
        urlaccess('/panel/experts/conditions/edit/1/', False),
        urlaccess('/panel/experts/conditions/delete/1/', False),
        urlaccess('/panel/admin/members/', False),
        urlaccess('/panel/admin/members/add/', False),
        urlaccess('/panel/admin/members/edit/1/', False),
        urlaccess('/panel/admin/members/delete/1/', False),
        urlaccess('/panel/admin/members/resend-activation/1/', False),
        urlaccess('/panel/admin/scientists/', False),
        urlaccess('/panel/admin/scientists/add/', False),
        urlaccess('/panel/admin/scientists/delete/1/', False),
        urlaccess('/panel/admin/administrators/', False),
        urlaccess('/panel/admin/administrators/add/', False),
        urlaccess('/panel/admin/administrators/delete/1/', False),
        urlaccess('/panel/admin/organisations/', False),
        urlaccess('/panel/admin/organisations/add/', False),
        urlaccess('/panel/admin/organisations/edit/1/', False),
        urlaccess('/panel/admin/organisations/delete/1/', False),
        urlaccess('/panel/admin/beta/', False),
        urlaccess('/panel/admin/beta/send/1/', False),
    ]


class TestUserAccess(GenericUrlTestCase, BackendTestCase, UserTestCase):

    test_urls = [
        urlaccess('/panel/', False),
        urlaccess('/panel/verify/1/', False),
        urlaccess('/panel/sightings/', False),
        urlaccess('/panel/sightings/all/', False),
        urlaccess('/panel/sightings/edit/1/', False),
        urlaccess('/panel/sightings/delete/1/', False),
        urlaccess('/panel/sightings/reassign/1/', False),
        urlaccess('/panel/sightings/spam/1/', False),
        urlaccess('/panel/experts/assignments/', False),
        urlaccess('/panel/experts/assignments/add/', False),
        urlaccess('/panel/experts/assignments/edit/1/', False),
        urlaccess('/panel/experts/assignments/delete/1/', False),
        urlaccess('/panel/experts/allocations/', False),
        urlaccess('/panel/experts/allocations/add/', False),
        urlaccess('/panel/experts/allocations/edit/1/', False),
        urlaccess('/panel/experts/allocations/delete/1/', False),
        urlaccess('/panel/experts/rules/', False),
        urlaccess('/panel/experts/rules/add/', False),
        urlaccess('/panel/experts/rules/edit/1/', False),
        urlaccess('/panel/experts/rules/delete/1/', False),
        urlaccess('/panel/experts/templates/', False),
        urlaccess('/panel/experts/templates/add/', False),
        urlaccess('/panel/experts/templates/edit/1/', False),
        urlaccess('/panel/experts/templates/delete/1/', False),
        urlaccess('/panel/experts/conditions/', False),
        urlaccess('/panel/experts/conditions/add/', False),
        urlaccess('/panel/experts/conditions/edit/1/', False),
        urlaccess('/panel/experts/conditions/delete/1/', False),
        urlaccess('/panel/admin/members/', False),
        urlaccess('/panel/admin/members/add/', False),
        urlaccess('/panel/admin/members/edit/1/', False),
        urlaccess('/panel/admin/members/delete/1/', False),
        urlaccess('/panel/admin/members/resend-activation/1/', False),
        urlaccess('/panel/admin/scientists/', False),
        urlaccess('/panel/admin/scientists/add/', False),
        urlaccess('/panel/admin/scientists/delete/1/', False),
        urlaccess('/panel/admin/administrators/', False),
        urlaccess('/panel/admin/administrators/add/', False),
        urlaccess('/panel/admin/administrators/delete/1/', False),
        urlaccess('/panel/admin/organisations/', False),
        urlaccess('/panel/admin/organisations/add/', False),
        urlaccess('/panel/admin/organisations/edit/1/', False),
        urlaccess('/panel/admin/organisations/delete/1/', False),
        urlaccess('/panel/admin/beta/', False),
        urlaccess('/panel/admin/beta/send/1/', False),
    ]


class TestScientistAccess(GenericUrlTestCase, BackendTestCase, ScientistTestCase):
    test_urls = [
        urlaccess('/panel/', True),
        urlaccess('/panel/verify/1/', True),
        urlaccess('/panel/sightings/', True),
        urlaccess('/panel/sightings/all/', True),
        urlaccess('/panel/sightings/edit/1/', True),
        urlaccess('/panel/sightings/delete/1/', False),
        urlaccess('/panel/sightings/reassign/1/', True),
        urlaccess('/panel/sightings/spam/1/', True),
        urlaccess('/panel/experts/assignments/', False),
        urlaccess('/panel/experts/assignments/add/', False),
        urlaccess('/panel/experts/assignments/edit/1/', False),
        urlaccess('/panel/experts/assignments/delete/1/', False),
        urlaccess('/panel/experts/allocations/', False),
        urlaccess('/panel/experts/allocations/add/', False),
        urlaccess('/panel/experts/allocations/edit/1/', False),
        urlaccess('/panel/experts/allocations/delete/1/', False),
        urlaccess('/panel/experts/rules/', False),
        urlaccess('/panel/experts/rules/add/', False),
        urlaccess('/panel/experts/rules/edit/1/', False),
        urlaccess('/panel/experts/rules/delete/1/', False),
        urlaccess('/panel/experts/templates/', False),
        urlaccess('/panel/experts/templates/add/', False),
        urlaccess('/panel/experts/templates/edit/1/', False),
        urlaccess('/panel/experts/templates/delete/1/', False),
        urlaccess('/panel/experts/conditions/', False),
        urlaccess('/panel/experts/conditions/add/', False),
        urlaccess('/panel/experts/conditions/edit/1/', False),
        urlaccess('/panel/experts/conditions/delete/1/', False),
        urlaccess('/panel/admin/members/', False),
        urlaccess('/panel/admin/members/add/', False),
        urlaccess('/panel/admin/members/edit/1/', False),
        urlaccess('/panel/admin/members/delete/1/', False),
        urlaccess('/panel/admin/members/resend-activation/1/', False),
        urlaccess('/panel/admin/scientists/', False),
        urlaccess('/panel/admin/scientists/add/', False),
        urlaccess('/panel/admin/scientists/delete/1/', False),
        urlaccess('/panel/admin/administrators/', False),
        urlaccess('/panel/admin/administrators/add/', False),
        urlaccess('/panel/admin/administrators/delete/1/', False),
        urlaccess('/panel/admin/organisations/', False),
        urlaccess('/panel/admin/organisations/add/', False),
        urlaccess('/panel/admin/organisations/edit/1/', False),
        urlaccess('/panel/admin/organisations/delete/1/', False),
        urlaccess('/panel/admin/beta/', False),
        urlaccess('/panel/admin/beta/send/1/', False),
    ]


class TestRegionalAdminAccess(GenericUrlTestCase, BackendTestCase,
    RegionalAdminTestCase):

    test_urls = [
        urlaccess('/panel/', True),
        urlaccess('/panel/verify/1/', True),
        urlaccess('/panel/sightings/', True),
        urlaccess('/panel/sightings/all/', True),
        urlaccess('/panel/sightings/edit/1/', True),
        urlaccess('/panel/sightings/delete/1/', True),
        urlaccess('/panel/sightings/reassign/1/', True),
        urlaccess('/panel/sightings/spam/1/', True),
        urlaccess('/panel/experts/assignments/', True),
        urlaccess('/panel/experts/assignments/add/', True),
        urlaccess('/panel/experts/assignments/edit/1/', True),
        urlaccess('/panel/experts/assignments/delete/1/', True),
        urlaccess('/panel/experts/allocations/', False),
        urlaccess('/panel/experts/allocations/add/', False),
        urlaccess('/panel/experts/allocations/edit/1/', False),
        urlaccess('/panel/experts/allocations/delete/1/', False),
        urlaccess('/panel/experts/rules/', False),
        urlaccess('/panel/experts/rules/add/', False),
        urlaccess('/panel/experts/rules/edit/1/', False),
        urlaccess('/panel/experts/rules/delete/1/', False),
        urlaccess('/panel/experts/templates/', False),
        urlaccess('/panel/experts/templates/add/', False),
        urlaccess('/panel/experts/templates/edit/1/', False),
        urlaccess('/panel/experts/templates/delete/1/', False),
        urlaccess('/panel/experts/conditions/', False),
        urlaccess('/panel/experts/conditions/add/', False),
        urlaccess('/panel/experts/conditions/edit/1/', False),
        urlaccess('/panel/experts/conditions/delete/1/', False),
        urlaccess('/panel/admin/members/', True),
        urlaccess('/panel/admin/members/add/', True),
        urlaccess('/panel/admin/members/edit/1/', True),
        urlaccess('/panel/admin/members/delete/1/', True),
        urlaccess('/panel/admin/members/resend-activation/1/', True),
        urlaccess('/panel/admin/scientists/', True),
        urlaccess('/panel/admin/scientists/add/', True),
        urlaccess('/panel/admin/scientists/delete/1/', True),
        urlaccess('/panel/admin/administrators/', False),
        urlaccess('/panel/admin/administrators/add/', False),
        urlaccess('/panel/admin/administrators/delete/1/', False),
        urlaccess('/panel/admin/organisations/', False),
        urlaccess('/panel/admin/organisations/add/', False),
        urlaccess('/panel/admin/organisations/edit/1/', False),
        urlaccess('/panel/admin/organisations/delete/1/', False),
        urlaccess('/panel/admin/beta/', False),
        urlaccess('/panel/admin/beta/send/1/', False),
    ]


class TestAdminAccess(GenericUrlTestCase, BackendTestCase, AdminTestCase):
    test_urls = [
        urlaccess('/panel/', True),
        urlaccess('/panel/verify/1/', True),
        urlaccess('/panel/sightings/', True),
        urlaccess('/panel/sightings/all/', True),
        urlaccess('/panel/sightings/edit/1/', True),
        urlaccess('/panel/sightings/delete/1/', True),
        urlaccess('/panel/sightings/reassign/1/', True),
        urlaccess('/panel/sightings/spam/1/', True),
        urlaccess('/panel/experts/assignments/', True),
        urlaccess('/panel/experts/assignments/add/', True),
        urlaccess('/panel/experts/assignments/edit/1/', True),
        urlaccess('/panel/experts/assignments/delete/1/', True),
        urlaccess('/panel/experts/allocations/', True),
        urlaccess('/panel/experts/allocations/add/', True),
        urlaccess('/panel/experts/allocations/edit/1/', True),
        urlaccess('/panel/experts/allocations/delete/1/', True),
        urlaccess('/panel/experts/rules/', True),
        urlaccess('/panel/experts/rules/add/', True),
        urlaccess('/panel/experts/rules/edit/1/', True),
        urlaccess('/panel/experts/rules/delete/1/', True),
        urlaccess('/panel/experts/templates/', True),
        urlaccess('/panel/experts/templates/add/', True),
        urlaccess('/panel/experts/templates/edit/1/', True),
        urlaccess('/panel/experts/templates/delete/1/', True),
        urlaccess('/panel/experts/conditions/', True),
        urlaccess('/panel/experts/conditions/add/', True),
        urlaccess('/panel/experts/conditions/edit/1/', True),
        urlaccess('/panel/experts/conditions/delete/1/', True),
        urlaccess('/panel/admin/members/', True),
        urlaccess('/panel/admin/members/add/', True),
        urlaccess('/panel/admin/members/edit/1/', True),
        urlaccess('/panel/admin/members/delete/1/', True),
        urlaccess('/panel/admin/members/resend-activation/1/', True),
        urlaccess('/panel/admin/scientists/', True),
        urlaccess('/panel/admin/scientists/add/', True),
        urlaccess('/panel/admin/scientists/delete/1/', True),
        urlaccess('/panel/admin/administrators/', True),
        urlaccess('/panel/admin/administrators/add/', True),
        urlaccess('/panel/admin/administrators/delete/1/', True),
        urlaccess('/panel/admin/organisations/', True),
        urlaccess('/panel/admin/organisations/add/', True),
        urlaccess('/panel/admin/organisations/edit/1/', True),
        urlaccess('/panel/admin/organisations/delete/1/', True),
        urlaccess('/panel/admin/beta/', True),
        urlaccess('/panel/admin/beta/send/1/', True),
    ]
