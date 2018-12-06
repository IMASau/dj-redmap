'''
Created on 18/06/2013

@author: thomas
'''
from django.core.management.base import BaseCommand
from redmap.apps.redmapdb.data import load_test_sightings
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class Command(BaseCommand):
    args = ''
    help = 'Regenerates all api tokens for all users'

    def handle(self, *args, **options):
        i = 0
        for user in User.objects.filter(auth_token=None):
            Token.objects.get_or_create(user=user)
            i += 1

        self.stdout.write('Complete, created %s tokens\n' % i)
