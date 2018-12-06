'''
Created on 05/09/2012

@author: thomas
'''

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.test.client import Client, RequestFactory
from redmap.apps.redmapdb.data import load_redmapdb_data
from redmap.apps.redmapdb.models import Organisation
from redmap.apps.backend.views import DeleteScientist


class FrontendViewsTests(TestCase):
    def setUp(self):
        load_redmapdb_data()
        self.factory = RequestFactory()
        self.password = 'password'

        group_names = ['Administrators', 'Scientists']
        self.groups = [Group.objects.get_or_create(name=name)[0] for name in group_names]

    def create_administrator(self):
        u = User.objects.create_user('new_administrator', 'thomas+new_administrator@ionata.com.au', self.password)
        u.is_staff = True
        u.groups.add(self.groups[0])
        u.groups.add(self.groups[1])
        u.save()

        return u

    def create_scientist(self):
        u = User.objects.create_user('new_scientist', 'thomas+new_scientist@ionata.com.au', self.password)
        u.is_staff = True
        u.groups.add(self.groups[1])
        u.save()

        return u

    def create_new_user(self, commit=True):
        u = User.objects.create_user('new_user', 'thomas+new_user@ionata.com.au', self.password)
        return u

    def test_add_scientist(self):
        """
        Determines whether a user can be set as a scientist through the view
        """

        admin_user = self.create_administrator()  # to login as
        new_user = self.create_new_user()  # to set as a scientist
        organisation = Organisation.objects.get(description="IMAS")

        c = Client()
        c.login(username=admin_user.username, password=self.password)

        response = c.post('/panel/admin/scientists/add/', {
            'username': new_user.pk,
            'organisation': organisation.pk,
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        gs = Group.objects.get(name='Scientists')
        new_user = User.objects.get(username=new_user.username)

        self.assertEqual(gs in list(new_user.groups.all()), True)

    def test_delete_scientist(self):
        """
        Determines whether a user can be return to a normal user from a scientist
        """

        admin_user = self.create_administrator()  # to login as
        new_scientist = self.create_scientist()  # to remove as a scientist

        request = self.factory.post("/panel/admin/scientists/delete/%d/" % (new_scientist.pk), {'pk': new_scientist.pk})

        # mock session
        request.user = admin_user
        request.session = {}

        response = DeleteScientist(request, new_scientist.pk)

        sg = Group.objects.get(name='Scientists')
        self.assertEqual(sg not in list(new_scientist.groups.all()), True)
