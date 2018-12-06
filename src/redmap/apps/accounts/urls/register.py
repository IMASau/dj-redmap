'''
Created on 28/06/2013

@author: thomas
'''
from redmap.apps.accounts.forms import RedmapRegistrationForm
from django.conf.urls.defaults import patterns, url
from registration.views import register

urlpatterns = patterns(
    'redmap.apps.accounts',
    url(r'^register/$',
        register,
        {
            'backend': 'apps.accounts.backends.RedmapBackend',
            "form_class": RedmapRegistrationForm
        },
        name='registration_register'
    ),
)
