from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.simple import redirect_to
from redmap.webapp.views import server_error
from redmap.webapp.sitemaps import sitemaps

admin.autodiscover()

urlpatterns = patterns(
    "",

    # Redirects
    url(r"^news/posts/view/\d+/", redirect_to, {"url": "/news/"}),
    url(r"^sightings/details/(?P<id>\d+)/", redirect_to, {"url": "/sightings/"}),
    url(r"^sightings/listing/", redirect_to, {"url": "/region/tas/sightings/"}),
    url(r"^locations/view/", redirect_to, {"url": "/region/tas/sightings/"}),
    url(r"^species/browse/(?P<id>\d+)/", redirect_to, {"url": "/species/%(id)s/"}),
    url(r"^members/view/(?P<id>\d+)/(?P<username>.*)/$", redirect_to, {"url": "/my-redmap/view/%(username)s/"}),

    # CMS
    url(r"^", include("redmap.apps.cms.urls")),
    url(r"^", include("redmap.apps.frontend.urls.public")),

    # Database
    url(r"^search/", include('haystack.urls')),
    url(r"^facebook/", include("django_facebook.urls")),
    url(r"^news/", include("redmap.apps.news.zinnia_urls")),
    url(r"^news/", include("zinnia.urls")),
    url(r"^article/", include("redmap.apps.news.frontend_articles")),
    url(r"^accounts/", include("redmap.apps.accounts.urls.register")),
    url(r"^accounts/", include("registration.backends.default.urls")),
    url(r"^my-redmap/", include("redmap.apps.accounts.urls.my_redmap")),
    url(r"^groups/", include("redmap.apps.frontend.urls.groups")),
    url(r"^panel/", include("redmap.apps.backend.urls")),
    url(r"^panel/content/", include("redmap.apps.cms.content_urls")),
    url(r"^panel/content/news/", include("redmap.apps.news.urls")),
    url(r"^panel/content/books/", include("redmap.apps.cms.backend_urls")),
    url(r"^panel/content/articles/", include("redmap.apps.news.article_urls")),
    url(r"^panel/content/faq/", include("redmap.apps.frontend.urls.faq")),
    url(r"^panel/admin/sponsors/", include("redmap.apps.frontend.urls.sponsors")),
    url(r"^panel/admin/surveys/", include("redmap.apps.surveys.urls")),
    url(r"^panel/admin/sponsor_categories/", include("redmap.apps.frontend.urls.sponsor_category")),
    url(r"^panel/admin/tags/", include("redmap.apps.news.tags_urls")),
    url(r"^ckeditor/", include("ckeditor.urls")),
    url(r"^filemanager/$", "redmap.webapp.views.wrapped_handler", name='filemanager'),
    url(r"^comments/", include("django.contrib.comments.urls")),
    url(r"^admin/doc/", include('django.contrib.admindocs.urls')),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^invite/", include("privatebeta.urls")),
    url(r"^sitemap\.xml$", 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    # API
    url(r"^api/", include('redmap.apps.restapi.urls')),
    url(r"^api/", include('rest_framework.urls', namespace='rest_framework')),

)

handler500 = server_error

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$',
        'django.views.static.serve',
        {
            'document_root': settings.STATIC_ROOT,
        }),
    )
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {
            'document_root': settings.MEDIA_ROOT,
        }),
    )