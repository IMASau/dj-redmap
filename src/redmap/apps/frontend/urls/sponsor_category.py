from django.conf.urls.defaults import *
from redmap.apps.frontend.backend_views import *

urlpatterns = patterns(
    'redmap.apps.frontend',
    url(r'^$', SponsorCategoryIndex, name="sponsor_category_index"),
    url(r'^add/$', SponsorCategoryEdit, name="sponsor_category_add"),
    url(r'^edit/(?P<pk>\d+)/$', SponsorCategoryEdit, name="sponsor_category_edit"),
    url(r'^delete/(?P<pk>\d+)/$', SponsorCategoryDelete, name="sponsor_category_delete"),
)
