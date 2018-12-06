from django.conf.urls.defaults import *
from redmap.apps.cms.views import *

urlpatterns = patterns(
    'redmap.apps.cms',

    # Browse list of books
    url(r'^$', BookListView.as_view(), name="cms_index"),

    # Create new book
    url(r'^add/$', BookCreateView.as_view(), name="cms_book_add"),

    # Viewing and updating books
    url(r'^(?P<pk>\d+)/$', BookDetailView.as_view(), name="cms_book_detail"),
    url(r'^(?P<pk>\d+)/edit/$', BookUpdateView.as_view(), name="cms_book_edit"),
    url(r'^(?P<pk>\d+)/delete/$', BookDeleteView.as_view(), name="cms_book_delete"),
    url(r'^(?P<pk>\d+)/reorder/$', ReorderPages, name="cms_book_reorder"),

    # Modifying books
    url(r'^(?P<book_id>\d+)/add/$', page_add_edit, name="cms_page_add"),
    url(r'^(?P<book_id>\d+)/edit/(?P<pk>\d+)/$', page_add_edit, name="cms_page_edit"),
    url(r'^(?P<book_id>\d+)/delete/(?P<pk>\d+)/$', page_delete, name="cms_page_delete"),
    url(r'^(?P<book_id>\d+)/revert/(?P<pk>\d+)/$', page_revert_revision, name="cms_page_revert_revision"),
)
