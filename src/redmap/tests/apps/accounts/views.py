'''
Created on 05/09/2012

@author: thomas
'''

from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from redmap.apps.redmapdb.data import load_redmapdb_data


class AccountViewsTests(TestCase):

    def setUp(self):
        load_redmapdb_data()
        user = User(username='test_user', email='thomas+test@ionata.com.au', first_name='thomas', last_name='randle')
        user.raw_password = 'test_password'
        user.set_password(user.raw_password)
        self.user = user

    def test_can_create_user(self):
        c = Client()
        response = c.post(
            '/accounts/register/',
            {'username': self.user.username,
             'email': self.user.email,
             'password1': self.user.raw_password,
             'password2': self.user.raw_password,
             'first_name': 'thomas',
             'last_name': 'randle',
             }, follow=True)

        print response.content

        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username=self.user.username)
        self.assertEqual(user.email, self.user.email)

    def test_user_can_login(self):
        c = Client()
        self.user.save()

        response = c.post(
            '/accounts/login/',
            {'username': self.user.username,
             'password': self.user.raw_password,
             }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._request.user, self.user)
