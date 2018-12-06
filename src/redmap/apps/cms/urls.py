from django.conf.urls.defaults import patterns, url
from .views import (
    about_view,
    about_page_view,
    region_about_view,
    region_about_page_view,
    book_view,
    book_page_view,
)
from redmap.apps.cms.views import ResourcesList, ResourcesCategory, ResourcesSubcategory,\
    ResourcesArticle


urlpatterns = patterns(
    '',

    url(r'^about/$',
        about_view,
        name="cms_about"),

    url(r'^about/(?P<page_slug>[-\w]*)/$',
        about_page_view,
        name="cms_about_page"),

    url(r'^region/(?P<region_slug>[-\w]*)/about/$',
        region_about_view,
        name="cms_region_about"),

    url(r'^region/(?P<region_slug>[-\w]*)/about/(?P<page_slug>[-\w]*)/$',
        region_about_page_view,
        name="cms_region_about_page"),

    url(r'^misc/(?P<book_slug>[-\w]*)/$',
            book_view,
            name="cms_book"),

    url(r'^misc/(?P<book_slug>[-\w]*)/(?P<page_slug>[-\w]*)/$',
            book_page_view,
            name="cms_book_page"),

    url(r'^resources/$',
            ResourcesList.as_view(),
            name="cms_resources_list"),


    #url(r'^resources/(?P<book_slug>[-\w]*)/$',
    #        ResourcesSubPage.as_view(),
    #        name="cms_resources_subpage"),

    # for testing:
    url(r'^resources/category/$', ResourcesCategory, name="resources_category"),
    url(r'^resources/category/subcategory/$', ResourcesSubcategory, name="resources_subcategory"),
    url(r'^resources/category/subcategory/article/$', ResourcesArticle, name="resources_article"),
)
