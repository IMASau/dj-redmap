from django.conf.urls.defaults import *
from redmap.apps.news.views import TagsView

urlpatterns = patterns(
    'redmap.apps.news',
    url(r'^$', TagsView, name='news_tags_list'),
)
