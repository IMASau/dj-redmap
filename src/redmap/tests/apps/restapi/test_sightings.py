'''
Created on 18/06/2013

@author: thomas
'''
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory, Client
from redmap.apps.redmapdb.data import load_all_data
from rest_framework.authtoken.models import Token
from redmap.apps.restapi.views import SightingCreate
from rest_framework.authtoken.views import obtain_auth_token
from redmap.apps.restapi.views import UserDetail
from django.middleware import csrf
from redmap.apps.redmapdb.models import Sighting
import json
import os
import base64


class SightingTests(TestCase):
    def setUp(self):
        load_all_data()
        self.user = User.objects.get(username="user1")
        self.user_token = Token.objects.get_or_create(user=self.user)[0]
        self.user_token_header = "Token {0}".format(self.user_token.key)
        self.factory = RequestFactory()

    def get_sighting_photo_data(self, path=None):
        if not path:
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_files', 'shark_1.jpg')
        image_file = open(path)
        return image_file

    def get_sighting_kwargs(self):
        payload = {
          "habitat": None,
          "is_checked_by_admin": True,
          "sex": 1,
          "update_number": 1,
          "species": 15,
          "size": None,
          "is_out_of_range": False,
          "weight": None,
          "photo_caption": "",
          "organisation": None,
          "logging_date": "2013-07-01T16:07:49.221",
          "is_valid_sighting": True,
          "other_species": "",
          "time": 1,
          "latitude": "-42.991789841387",
          "water_temperature": None,
          "method": None,
          "accuracy": 1,
          "update_time": "2013-07-01T16:07:49.231",
          "size_method": None,
          "activity": 4,
          "activity_other": None,
          "user": 21,
          "count": 1,
          "is_not_displayed": False,
          "exif": None,
          "sighting_date": "2013-07-01T00:00:00",
          "notes": "",
          "longitude": "147.914061250009",
          #"depth": None,
          "photo_matches_species": 1,
          "published_date": "2013-07-01T16:08:24.101",
          "is_verified_by_scientist": False,
          "is_published": True,
          "region": 1,
          "weight_method": None,
          "photo_url": self.get_sighting_photo_data(),
        }
        return payload

    def test_require_api_token(self):
        """
        Ensure post without api token hits a wall
        """
        request = self.factory.post("/api/sighting/create/", {})
        view = SightingCreate.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data.get('detail', None), u"Authentication credentials were not provided.")

    def test_sighting_required_fields_match_payload(self):
        """
        Ensure all the required fields from the model definition and used in test data
        """
        payload = self.get_sighting_kwargs()
        fields = filter(lambda field: not field.null and not field.name == "id", Sighting._meta.fields)
        for field in fields:
            self.assertTrue(field.name in payload, "%s field required by model but not in payload" % field.name)

    def test_can_create_valid_sighting_by_json(self):
        """
        Create a valid sighting
        """
        payload = self.get_sighting_kwargs()
        payload['photo_url'] = base64.b64encode(payload['photo_url'].read())
        payload['photo_url_name'] = "/home/my-random/path/1.1._jetty-and-sunrise_3.jpg"
        request = self.factory.post("/api/sighting/create/", content_type='application/json', data=json.dumps(payload), HTTP_AUTHORIZATION=self.user_token_header)

        view = SightingCreate.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 201)

        sighting = Sighting.objects.get(pk=response.data.get('pk'))

        # ensure the photo got up successfully.
        self.assertEqual(bool(sighting.photo_url), True, "Image data was not present on the sighting")
        self.assertGreater(sighting.photo_url.size, 0)

    def test_can_create_valid_sighting_by_post(self):
        """
        Create a valid sighting
        """
        payload = self.get_sighting_kwargs()

        """
        Remove None value keys/val pairs from the payload as django interprets a 
        posted key as a field having a value
        """

        payload = dict(filter(lambda payload_iter: payload_iter[1] is not None, payload.iteritems()))
        request = self.factory.post("/api/sighting/create/", data=payload, HTTP_AUTHORIZATION=self.user_token_header)

        count = Sighting.objects.count()
        view = SightingCreate.as_view()
        response = view(request)
        count2 = Sighting.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(count + 1, count2)

        pk = response.renderer_context.get('view').object.id
        sighting = Sighting.objects.get(pk=pk)

        # ensure the photo got up successfully.
        self.assertEqual(bool(sighting.photo_url), True, "Image data was not present on the sighting")
        self.assertGreater(sighting.photo_url.size, 0, "Image data was not greater than 0 bytes")
"""
    def test_invalid_file_size_upload(self):
        """"""
        Post sighting data with a in valid photo file size
        """"""
        payload = self.get_sighting_kwargs()
        too_large_test_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_files', 'shark_1_gt_512KB.jpg')
        payload['photo_url'] = self.get_sighting_photo_data(too_large_test_file_path)
        request = self.factory.post("/api/sighting/create/", data=json.dumps(payload), content_type='application/json', HTTP_AUTHORIZATION=self.user_token_header)

        view = SightingCreate.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 201)
"""
