import re
import reversion

from redmap.common.util import reverse_lazy
from redmap.common.generic_views import AuthMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404,\
    redirect
from tagging.models import Tag
from redmap.apps.cms.forms import AddPageForm, UpdateHomepageForm
from redmap.apps.cms.models import Page, HomepageContent
from redmap.apps.cms.utils import cached_copy
from reversion.models import Version
from redmap.apps.redmapdb.models import Region
from django.conf import settings
from django.http import Http404
from django.contrib import messages
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from redmap.apps.cms.forms import BookForm, CopyBlockForm
from redmap.apps.cms.models import CopyBlock
from django.core.urlresolvers import reverse
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from redmap.apps.surveys.models import Survey


login_url = reverse_lazy('auth_login')


class BookCreateView(AuthMixin, CreateView):

    model = Page
    form_class = BookForm
    template_name = "cms/book_form.html"

    required_permissions = [
        'cms.add_book',
    ]


class BookUpdateView(AuthMixin, UpdateView):

    model = Page
    form_class = BookForm
    context_object_name = "book"
    template_name = "cms/book_form.html"

    required_permissions = [
        'cms.change_book',
    ]


class BookDeleteView(AuthMixin, DeleteView):
    model = Page

    required_permissions = [
        'cms.delete_book',
    ]


class BookListView(AuthMixin, ListView):

    model = Page
    queryset = Page.objects.root_nodes()
    context_object_name = "book"
    template_name = "cms/book_list.html"

    required_permissions = [
        'cms.change_page',
        'cms.add_page',
    ]


class BookDetailView(AuthMixin, DetailView):

    model = Page
    queryset = Page.objects.root_nodes()
    context_object_name = "book"
    template_name = "cms/book_detail.html"

    required_permissions = [
        'cms.change_page',
        'cms.add_page',
    ]

    def get_context_data(self, object):
        context = super(BookDetailView, self).get_context_data()
        context['pages'] = object.get_descendants()
        return context


def decode_positions_string(positions_str):
    """
    Decode the data passed back from jquery.ui.nestedSortable
    """
    rePosition = r"list\[(\d+)\]=(null|(\d+))"
    for (id, null, parent_id) in re.findall(rePosition, positions_str):
        yield (id, parent_id or None)


@login_required
@permission_required('cms.change_page')
def ReorderPages(request, pk):
    """
    Reorder pages in a book.

    This doesn't have a django form, it's using a jquery plugin to build a
    string.
    """
    book = get_object_or_404(Page, pk=pk, parent=None)
    pages = book.get_descendants()

    if request.POST:

        positions = list(decode_positions_string(request.POST['positions']))

        for (id, parent_id) in positions:
            page = pages.get(pk=id)
            if parent_id is None:
                book = page.get_root()
                page.move_to(book, 'last-child')
            else:
                parent = pages.get(pk=parent_id)
                page.move_to(parent, 'last-child')

        messages.success(request, 'Page order updated.')

    return redirect('cms_book_detail', pk=book.pk)


def page_view(request, slug, region_slug=None, is_region_page=None,
    about_page=False):
    """Generic page view handler"""

    page = get_object_or_404(Page, slug=slug)

    if page.is_draft:
        '''Only regional admins or global admins should be able to view draft
        content on the site'''
        if request.user.is_authenticated():
            user = request.user.profile
            if not user.is_regional_admin and not user.is_global_admin:
                raise Http404
        else:
            raise Http404

    ancestors = page.get_ancestors()
    descendants = page.get_descendants()

    payload = {
        'page': page,
        'ancestors': ancestors,
        'descendants': descendants,
        'level': page.get_level() + 1,
        'about_page': about_page,
    }

    if region_slug:
        region = get_object_or_404(Region, slug=region_slug)
        region_tag = Tag.objects.get_for_object(region)[0]

        payload['region'] = region

    return render(request, page.template, payload)


def about_view(request):
    """Display main about section landing page"""
    page = cached_copy['home'].about_book.index_page
    return page_view(request, page.slug, about_page=True)


def about_page_view(request, page_slug):
    """Display page in main about section"""
    try:
        page = cached_copy['home'].about_book.get_descendants().get(slug=page_slug)
        return page_view(request, page.slug, about_page=True)
    except:
        return redirect("cms_about")


def region_about_view(request, region_slug):
    region = get_object_or_404(Region, slug=region_slug)
    page = region.regionaboutpage.page.index_page
    return page_view(request, page.slug, region.slug, is_region_page=True, about_page=True)


def region_about_page_view(request, region_slug, page_slug):
    region = get_object_or_404(Region, slug=region_slug)
    page = region.regionaboutpage.page.get_descendants().get(slug=page_slug)
    return page_view(request, page.slug, region.slug, is_region_page=True, about_page=True)


def book_view(request, book_slug):
    book = Page.objects.get(slug=book_slug, parent__isnull=True)
    page = book.index_page
    return page_view(request, page.slug, about_page=False, is_region_page=False)


def book_page_view(request, book_slug, page_slug):
    book = Page.objects.get(slug=book_slug, parent__isnull=True)
    try:
        page = book.get_descendants().get(slug=page_slug)
    except Page.DoesNotExist:
        raise Http404
    return page_view(request, page.slug, about_page=False, is_region_page=False)


@login_required
@permission_required('cms.change_page')
def page_add_edit(request, book_id, pk=None):

    book = get_object_or_404(Page, pk=book_id)

    if pk:
        page = get_object_or_404(Page, pk=pk)
        version_list = reversion.get_for_object(page)

        # Make sure template can select tags
        page.tag_list = page.tag_list.split(',')
    else:
        page = None
        version_list = {}

    if request.POST:
        form = AddPageForm(request.POST, request.FILES, instance=page, book=book)
        if form.is_valid():
            instance = form.save()

            if request.POST.get('save_and_preview') or request.POST.get('save_and_view'):
                return redirect(instance.get_public_url())
            elif request.POST.get('save_and_continue'):
                return redirect(instance.get_edit_url())
            else:
                return redirect(reverse('cms_book_detail', kwargs={'pk': book.pk}))
    else:
        form = AddPageForm(instance=page, book=book)

    context = {
        'form': form,
        'pk': pk,
        'page': page,
        'book': book,
        'version_list': version_list,
    }

    return render(request, 'cms/page_add_edit.html', context)


@login_required
@permission_required('cms.delete_page')
def page_delete(request, book_id, pk):

    book = get_object_or_404(Page, pk=book_id)
    page = get_object_or_404(Page, pk=pk)

    if pk and request.POST:
        page.delete()
        return HttpResponseRedirect(reverse_lazy('cms_index'))

    return render(
        request,
        "cms/page_delete.html",
        {'page': page, 'book': book}
    )


@login_required
@permission_required('cms.change_page')
def page_revert_revision(request, book_id, pk):

    version = get_object_or_404(Version, pk=pk)

    if pk and request.POST:
        version.revision.revert()
        return redirect(reverse('cms_edit', args=[version.object_id]))

    return render(
        request,
        "cms/revert_revision.html",
        {'version': version}
    )


@login_required
@permission_required('cms.change_homepagecontent')
def update_homepage(request, pk=1):

    homepage, created = HomepageContent.objects.get_or_create(pk=pk)
    version_list = reversion.get_for_object(homepage)

    if request.POST:
        form = UpdateHomepageForm(request.POST, instance=homepage)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content blocks saved')
            return redirect(reverse('cms_homepage'))
    else:
        form = UpdateHomepageForm(instance=homepage)

    return render(
        request,
        "cms/update_homepage.html",
        {'form': form, 'version_list': version_list}
    )


class CopyBlockListView(AuthMixin, ListView):

    model = CopyBlock
    queryset = CopyBlock.objects.all()
    template_name = "cms/copyblock_list.html"

    required_permissions = [
        'cms.change_copyblock',
    ]


class CopyBlockCreateView(AuthMixin, CreateView):

    model = CopyBlock
    form_class = CopyBlockForm
    template_name = "cms/copyblock_form.html"

    required_permissions = [
        'cms.add_copyblock',
    ]


class CopyBlockUpdateView(AuthMixin, UpdateView):

    model = CopyBlock
    form_class = CopyBlockForm
    template_name = "cms/copyblock_form.html"

    required_permissions = [
        'cms.change_copyblock',
    ]


class CopyBlockDeleteView(AuthMixin, DeleteView):
    model = CopyBlock

    required_permissions = [
        'cms.delete_copyblock',
    ]

    def get_success_url(self):
        return reverse('cms_copyblock_index')


# New resources templates
class ResourcesList(ListView):
    model = Page
    template_name = 'cms/page/resources/list.html'

    def get_context_data(self, **kwargs):
        context = super(ResourcesList, self).get_context_data(**kwargs)
        try:
            context.update({'survey': Survey.objects.get(slug='resources')})
        except Survey.DoesNotExist:
            pass
        return context

    def get_queryset(self):
        qs = super(ResourcesList, self).get_queryset().filter(parent__slug='resources')
        return qs


def ResourcesCategory(request):
    context = {}
    return render(request, 'frontend/resource-listing.html', context)


def ResourcesSubcategory(request):
    context = {}
    return render(request, 'frontend/resources_subcategory.html', context)


def ResourcesArticle(request):
    context = {}
    return render(request, 'frontend/resources_article.html', context)
