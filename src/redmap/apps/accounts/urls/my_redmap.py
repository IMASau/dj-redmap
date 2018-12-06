from redmap.apps.accounts.forms import RedmapRegistrationForm
from redmap.apps.accounts.views import Profile, EditProfile, ViewProfile, MyGroups
from django.conf.urls.defaults import patterns, url
from registration.views import register

urlpatterns = patterns(
    'redmap.apps.accounts',
    url(r'^$', Profile, name='acct_profile'),
    url(r'^edit/$', EditProfile, name='acct_edit_profile'),
    url(r'^view/(?P<username>.+)/$', ViewProfile, name='view_profile'),
    url(r'^groups/$', MyGroups.as_view(), name='my_groups'),
    url(r'^register/$',
        register,
        {
            'backend': 'apps.accounts.backends.RedmapBackend',
            "form_class": RedmapRegistrationForm
        },
        name='registration_register'
    ),
)
