from django.conf.urls.defaults import *
from redmap.apps.news.views import ArticleList, ArticleEdit, ArticleDelete

urlpatterns = patterns(
    'redmap.apps.news',
    url(r'^$', ArticleList.as_view(), name='article_index'),
    url(r'^add/$', ArticleEdit, name='article_add'),
    url(r'^edit/(?P<pk>\d+)/$', ArticleEdit, name='article_edit'),
    url(r'^delete/(?P<pk>\d+)/$', ArticleDelete, name='article_delete'),
)
