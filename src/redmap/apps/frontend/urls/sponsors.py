from django.conf.urls.defaults import *
from redmap.apps.frontend.backend_views import *

urlpatterns = patterns(
    'redmap.apps.frontend',
    url(r'^$', SponsorIndex, name="sponsor_index"),
    url(r'^add/$', SponsorAdd, name="sponsor_add"),
    url(r'^edit/(?P<pk>\d+)/$', SponsorAdd, name="sponsor_edit"),
    url(r'^delete/(?P<pk>\d+)/$', SponsorDelete, name="sponsor_delete"),
)
