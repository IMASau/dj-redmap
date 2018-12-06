from django.conf.urls.defaults import *
from redmap.apps.cms.views import *

urlpatterns = patterns(
    'redmap.apps.cms',

    # Homepage content blocks
    url(r'^homepage/$', update_homepage, name="cms_homepage"),

    # Copy blocks
    url(r'^blocks/$', CopyBlockListView.as_view(), name="cms_copyblock_index"),
    url(r'^blocks/add/$', CopyBlockCreateView.as_view(), name="cms_copyblock_add"),
    url(r'^blocks/edit/(?P<pk>\d+)/$', CopyBlockUpdateView.as_view(), name="cms_copyblock_edit"),
    url(r'^blocks/delete/(?P<pk>\d+)/$', CopyBlockDeleteView.as_view(), name="cms_copyblock_delete"),
)
