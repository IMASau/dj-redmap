from django.conf.urls.defaults import *
from redmap.apps.frontend.views import *

urlpatterns = patterns(
    'redmap.apps.frontend',
    url(r'^$', GroupsList.as_view(), name='groups_list'),
    url(r'^view/(?P<pk>\d+)/$', GroupView, name='group_view'),
    url(r'^add/$', GroupEdit, name='group_add'),
    url(r'^edit/(?P<pk>\d+)/$', GroupEdit, name='group_edit'),
    url(r'^delete/(?P<pk>\d+)/$', GroupDelete, name='group_delete'),
)
