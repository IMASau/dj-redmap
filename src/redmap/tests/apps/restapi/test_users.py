'''
Created on 18/06/2013

@author: thomas
'''
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory, Client
from redmap.apps.redmapdb.data import load_redmapdb_data
from rest_framework.authtoken.models import Token
from redmap.apps.restapi.views import Register
from rest_framework.authtoken.views import obtain_auth_token
from redmap.apps.restapi.views import UserDetail


class UserTests(TestCase):
    def setUp(self):
        self.test_username = self.get_random_username()
        self.factory = RequestFactory()
        load_redmapdb_data()

    def tearDown(self):
        try:
            u = User.objects.get(username=self.test_username)
            u.delete()
        except User.DoesNotExist:
            pass

    def get_random_username(self):
        return "test_" + str(uuid.uuid1())[:25]

    def get_user_kwargs(self):
        return {
            'username': self.test_username,
            'password': 'password',
            'email': 'thomas+{0}@ionata.com.au'.format(self.test_username),
            'first_name': 'thomas',
            'last_name': 'randle',
        }

    def test_can_register_user(self):
        payload = self.get_user_kwargs()
        payload.update({
            'region': "Tasmania",
            'join_mailing_list': True,
        })

        request = self.factory.post("/api/user/register/", payload)
        view = Register.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 201)

    def test_can_register_user_validate_region(self):
        payload = self.get_user_kwargs()
        payload.update({
            'join_mailing_list': True,
        })
        request = self.factory.post("/api/user/register/", payload)
        view = Register.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual('region' in response.data.keys(), True)

    def test_can_register_user_validate_incorrect_region(self):
        payload = self.get_user_kwargs()
        payload.update({
            'region': 'asdfasdfsd7a8f678sdaf67=8asdf76asdf78',
            'join_mailing_list': True,
        })
        request = self.factory.post("/api/user/register/", payload)
        view = Register.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertTrue('region' in response.data.keys())

    def test_can_get_auth_token(self):
        payload = {
            'username': self.test_username,
            'password': 'password',
        }

        user = User(**self.get_user_kwargs())
        user.set_password(user.password)
        user.save()

        request = self.factory.post("/api/user/api-token-auth/", payload)
        response = obtain_auth_token(request)

        token = Token.objects.get(user=user)  # must be after the request, the token will be created if it doesn't exist by the view

        self.assertEqual(token.key, response.data.get('token'))

    def test_unique_email_address(self):
        user = User(**self.get_user_kwargs())
        user.set_password(user.password)
        user.save()

        payload = self.get_user_kwargs()
        payload.update({
            'username': "{0}2".format(payload.get('username')[:29]),
            'region': "Tasmania",
            'join_mailing_list': True,
        })

        request = self.factory.post("/api/user/register/", payload)
        view = Register.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertTrue('email' in response.data.keys())

    def test_can_confirm_user_details_via_token(self):
        user = User(**self.get_user_kwargs())
        user.set_password(user.password)
        user.save()
        token, created = Token.objects.get_or_create(user=user)

        request = self.factory.get(path="/api/user/profile/", data={}, content_type='application/json', HTTP_AUTHORIZATION="Token {0}".format(token.key))
        view = UserDetail.as_view()
        response = view(request)

        attrs = self.get_user_kwargs()
        del attrs['password']
        attrs = attrs.keys()

        for attr in attrs:
            self.assertEqual(getattr(user, attr), response.data.get(attr))
