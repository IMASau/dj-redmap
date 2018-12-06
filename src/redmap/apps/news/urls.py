from django.conf.urls.defaults import *
from redmap.apps.news.views import EntriesList, EntryAddView, EntryDeleteView

urlpatterns = patterns(
    'redmap.apps.news',
    url(r'^$', EntriesList.as_view(), name='news_entries_list'),
    url(r'^add/$', EntryAddView, name='news_entry_add'),
    url(r'^edit/(?P<pk>\d+)/$', EntryAddView, name='news_entry_edit'),
    url(r'^delete/(?P<pk>\d+)/$', EntryDeleteView, name='news_entry_delete'),
)
