from django.conf.urls.defaults import *
from redmap.apps.frontend.backend_views import *

urlpatterns = patterns(
    'redmap.apps.frontend',
    url(r'^$', FaqIndex, name='faq_index'),
    url(r'^add/$', FaqEdit, name='faq_add'),
    url(r'^edit/(?P<pk>\d+)/$', FaqEdit, name='faq_edit'),
    url(r'^delete/(?P<pk>\d+)/$', FaqDelete, name='faq_delete'),
)
