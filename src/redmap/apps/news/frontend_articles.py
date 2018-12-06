from django.conf.urls.defaults import *
from redmap.apps.news.views import ArticleView

urlpatterns = patterns(
    'redmap.apps.frontend',
    url(r'^(?P<slug>.*)/$', ArticleView, name='article_view'),
)
