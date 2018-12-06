'''
Created on 06/09/2012

@author: thomas
'''

from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.test import TestCase
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users
from redmap.apps.cms.data import load_cms_data


class CMSTests(TestCase):

    def setUp(self):
        load_cms_data()

    def test_cms_has_homepage(self):
        from redmap.apps.cms.models import HomepageContent
        hc = HomepageContent.objects.get(pk=1)
        self.assertEqual(hc.title, 'Redmap', )
