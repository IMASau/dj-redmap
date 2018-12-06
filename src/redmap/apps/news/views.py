from redmap.common.generic_views import AuthMixin
from django.conf import settings as global_settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404, QueryDict
from django.shortcuts import HttpResponseRedirect, get_object_or_404, render,\
    redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic.dates import DateDetailView
from redmap.apps.news.forms import *
from redmap.apps.redmapdb.models import Region, Sighting
from tagging.models import Tag, TaggedItem
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from zinnia.models import Entry
from zinnia.settings import ALLOW_FUTURE
from django.db.models import Q

from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateResponseMixin
from redmap.common.tags import get_redmap_tag


class RegionContextMixin(TemplateResponseMixin):

    def get_context_data(self, **kwargs):
        context = super(RegionContextMixin, self).get_context_data(**kwargs)

        region_slug = self.kwargs.get('region_slug')

        if region_slug:
            region = Region.objects.get(slug=region_slug)
            context['region'] = region

        return context


class FrontendNews(ListView, RegionContextMixin):

    template_name = 'zinnia/entry_list.html'
    paginate_by = 10

    def get_queryset(self):

        region_slug = self.kwargs.get('region_slug')

        if region_slug:

            region = Region.objects.get(slug=region_slug)
            region_tag = list(Tag.objects.get_for_object(region))

            if region_tag:
                return TaggedItem.objects.get_by_model(Entry.published, region_tag[0]).\
                    filter(categories__slug="news", status=PUBLISHED)

        else:
            return TaggedItem.objects.get_by_model(Entry.published, get_redmap_tag()).\
                filter(categories__slug="news", status=PUBLISHED)

        return Entry.published.filter(categories__slug="news",status=PUBLISHED)


class NewsDetail(DateDetailView, RegionContextMixin):

    date_field = 'creation_date'
    allow_future = ALLOW_FUTURE
    queryset = Entry.published.on_site()
    month_format = '%m'

    def get_object(self, queryset=None):
        object = super(NewsDetail, self).get_object(queryset)

        if object.status == DRAFT:
            '''Only regional admins or global admins should be able to view
            draft content on the site'''
            if self.request.user.is_authenticated():
                user = self.request.user.profile

                if not user.is_regional_admin and not user.is_global_admin:
                    raise Http404
            else:
                raise Http404

        return object

    def get_context_data(self, **kwargs):
        context = super(NewsDetail, self).get_context_data(**kwargs)

        news = context.get('entry')

        latest_news = Entry.published.filter(
            categories__slug="news",status=PUBLISHED)

        context.update({
            'is_draft': news.status == DRAFT,
            'latest_news': latest_news,
        })

        # Set template to render
        self.template_name = self.object.template

        return context


class EntriesList(AuthMixin, ListView):

    context_object_name = "entries"
    template_name = "news/entries_list.html"

    required_permissions = [
        'zinnia.can_view_all',
    ]

    paginate_by = 10

    def get_queryset(self):
        qs = Entry.objects.filter(categories__slug="news")
        filter = self.request.GET.get('filter', None)
        if filter:
            qs = qs.filter(Q(title__icontains=filter) | Q(authors__first_name__icontains=filter))
        return qs

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(EntriesList, self).get_context_data(**kwargs)

        # Add in the publisher
        context['STATUS_CHOICES'] = {
            DRAFT: _('draft'),
            HIDDEN: _('hidden'),
            PUBLISHED: _('published')
        }
        get_args = self.request.GET.copy()
        get_args.pop('page', None)

        context.update({
            'filter_url_args': "&{0}".format(get_args.urlencode()),
        })
        return context

    def dispatch(self, *args, **kwargs):
        return super(EntriesList, self).dispatch(*args, **kwargs)


@login_required
@permission_required('zinnia.change_entry')
def EntryAddView(request, pk=None, template_name="news/entry_add.html"):

    if pk:
        news = get_object_or_404(Entry, pk=pk)
        initial = {}

    else:
        news = Entry()
        initial = {'author': request.user}

    if request.method == 'POST':

        form = EntryAddForm(
            data=request.POST,
            files=request.FILES,
            instance=news,
            user=request.user
        )

        if form.is_valid():
            form.save()

            if request.POST.get('save_and_preview') or request.POST.get('save_and_view'):
                return redirect(news.get_absolute_url())
            elif request.POST.get('save_and_continue'):
                return redirect(news.get_edit_url())
            else:
                return redirect(reverse('news_entries_list'))

    else:
        form = EntryAddForm(instance=news, initial=initial)

    is_draft = news.status == DRAFT

    context = {
        'form': form,
        'pk': pk,
        'is_draft': is_draft,
    }

    return render(request, template_name, context)


@login_required
@permission_required('zinnia.delete_entry')
def EntryDeleteView(request, pk=None, template_name="news/entry_delete.html"):

    if pk and request.POST:

        news = Entry.objects.get(pk=pk)
        news.delete()

        return redirect(reverse('news_entries_list'))

    entry = Entry.objects.get(pk=pk)

    return render(
        request,
        template_name,
        {
            'entry': entry
        }
    )

@login_required
@permission_required('tagging.change_tag')
def TagsView(request, template_name="news/tags_list.html"):

    if request.method == 'POST':

        for field in request.POST:

            region_field = field.split('_')
            tag_name = request.POST[field]

            if region_field[0] == 'tag' and tag_name != 'None':

                # What region are we dealing with?
                if region_field[1] == '0':
                    region = None # 0 = All
                else:
                    region = Region.objects.get(id=region_field[1])

                # Get region tag if available
                if region is not None:
                    tag = list(Tag.objects.get_for_object(region))
                else:
                    tag = [get_redmap_tag(),]

                if not tag:

                    # create tag if not exists
                    tag = Tag()
                    tag.name = tag_name
                    tag.save()

                elif tag[0].name != tag_name:

                    # update tag if different
                    tag[0].name = tag_name
                    tag[0].save()

                    # TODO: If we update a tag, we will need to update zinnia
                    #       entries with updated tags because the app stores
                    #       tags in a plain-text string rather than by model
                    #       association

                if region is not None:
                    # attach tag to region
                    Tag.objects.update_tags(region, tag_name + ',')

        return HttpResponseRedirect(reverse('news_tags_list'))

    return render(
        request,
        template_name
    )


class ArticleList(AuthMixin, ListView):

    context_object_name = "articles"
    template_name = "news/article_list.html"

    required_permissions = [
        'zinnia.can_view_all',
    ]

    paginate_by = 10

    def get_queryset(self):
        qs = Entry.objects.filter(categories__slug="articles")
        filter = self.request.GET.get('filter', None)
        if filter:
            qs = qs.filter(Q(title__icontains=filter) | Q(authors__first_name__icontains=filter))
        return qs

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(ArticleList, self).get_context_data(**kwargs)

        # Add in the publisher
        context['STATUS_CHOICES'] = {
            DRAFT: _('draft'),
            HIDDEN: _('hidden'),
            PUBLISHED: _('published')
        }

        get_args = self.request.GET.copy()
        get_args.pop('page', None)

        context.update({
            'filter_url_args': "&{0}".format(get_args.urlencode()),
        })

        return context

@login_required
@permission_required('zinnia.change_entry')
def ArticleEdit(request, pk=None, template_name="news/article_edit.html"):

    if pk:
        article = get_object_or_404(Entry, pk=pk)
        initial = {}

    else:
        article = Entry()
        initial = {'author': request.user}

    if request.method == 'POST':

        form = ArticleAddForm(
            data = request.POST,
            files = request.FILES,
            instance = article,
            user = request.user
        )

        if form.is_valid():
            instance = form.save()
            if request.POST.get('save_and_preview') or request.POST.get('save_and_view') :
                return redirect(instance.get_public_url())
            elif request.POST.get('save_and_continue'):
                return redirect(instance.get_edit_url())
            else:
                return redirect(reverse('article_index'))

    else:
        form = ArticleAddForm(instance=article, initial=initial)

    is_draft = article.status == DRAFT

    return render(
        request,
        template_name,
        {
            'form': form,
            'pk': pk,
            'is_draft': is_draft,
        }
    )


@login_required
@permission_required('zinnia.delete_entry')
def ArticleDelete(request, pk=None, template_name="news/article_delete.html"):

    if pk and request.POST:

        article = Entry.objects.get(pk=pk)
        article.delete()

        return HttpResponseRedirect(reverse('article_index'))

    article = Entry.objects.get(pk=pk)

    return render(
        request,
        template_name,
        {
            'article': article,
        }
    )


def ArticleView(request, slug=None, template_name=None):

    article = get_object_or_404(Entry, categories__slug="articles", slug=slug)

    is_draft = article.status == DRAFT

    if is_draft:
        if request.user.is_authenticated():
            user = request.user.profile

            if not user.is_regional_admin and not user.is_global_admin:
                raise Http404
        else:
            raise Http404

    elif article.template:
        template_name = article.template.replace('zinnia/', 'resources/')
    elif article.template is None and template_name is None:
        template_name = 'resources/entry_detail.html'

    return render(
        request,
        template_name,
        {
            'object': article,
            'is_draft': is_draft,
            'is_resource_page': True,
        }
    )
