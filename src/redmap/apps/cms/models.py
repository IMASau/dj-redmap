import datetime

from ckeditor.fields import RichTextField
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from singleton_models.models import SingletonModel
from tagging.fields import TagField
from fields import RelativeFilePathField
from django.conf import settings
from redmap.apps.redmapdb.models import Region
from mptt.managers import TreeManager
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from django.core.urlresolvers import reverse

from redmap.apps.cms.utils import cached_copy


class HomepageContent(SingletonModel):
    "Copy used on the homepage"

    title = models.CharField(blank=True, max_length=255)
    subtitle = models.CharField(blank=True, max_length=255)
    teaser = models.CharField(blank=True, max_length=255)
    find_out_more = models.CharField(blank=True, null=True, max_length=255)

    about_book = models.ForeignKey('cms.Page', on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "homepage content"


cached_copy.register(HomepageContent, 'home')


class SitewideContent(SingletonModel):
    "Sitewide copy, meta data and the like"

    site_title = models.CharField(blank=True, null=True, max_length=255)
    copyright = models.CharField(blank=True, null=True, max_length=255, default="&copy; Copyright REDMAP")
    meta_description = models.TextField(blank=True, null=True)
    imas_logo = models.ImageField(blank=True, null=True, upload_to='sitewide_images')
    facebook_logo = models.ImageField(blank=True, null=True, upload_to=u'facebook_images')
    ga_tracking_code = models.CharField("Google Analytics tracking code",
        default="UA-XXXXXXXX-1", max_length=16)
    facebook_registration_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "sitewide content"


cached_copy.register(SitewideContent, 'site')


class SightingContent(SingletonModel):
    "Copy for 'Log a Sighting' pages"

    sighting_intro = models.TextField(
        verbose_name = "Step 1 introduction text",
        help_text = "This text will appear above step 1",
    )

    sighting_photo_help_text = models.TextField(
        verbose_name = "Photo help text",
    )

    sighting_photo_permission_text = models.TextField(
        verbose_name = "Photo permission label",
    )

    sighting_accuracy_label = models.TextField(
        verbose_name = "Sighting accuracy label",
        help_text = "",
        default = "Click on map to place a marker indicating the location of the sighting. Alternatively enter the sighting coordinates manually below.\n\nExact locations are private. We will only show sightings in half a degree square.",
    )

    sighting_details_intro = models.TextField(
        verbose_name = "Step 3 introduction text",
        help_text = "This text will appear above step 3",
    )

    sighting_confirmation_intro = models.TextField(
        verbose_name = "Confirmation introduction text",
        help_text = "This text will appear above the sighting confirmation page",
    )

    sighting_count_help_text = models.TextField(help_text = "")

    sighting_weight_help_text = models.TextField(help_text = "")

    sighting_size_help_text = models.TextField(help_text = "")

    sighting_sex_help_text = models.TextField(help_text = "")

    sighting_depth_help_text = models.TextField(help_text = "")

    sighting_habitat_help_text = models.TextField(help_text = "")

    sighting_temperature_help_text = models.TextField(help_text = "")

cached_copy.register(SightingContent, 'sighting')


class PageManager(TreeManager):

    def get_published_pages(self):
        """Return all pages (not root nodes) which are public"""
        return self.filter(status=PUBLISHED, parent__isnull=False)

    def published(self):
        """Return published pages"""
        return self.filter(status=PUBLISHED)


class Page(MPTTModel):
    """ Static pages """
    STATUS_CHOICES = ((DRAFT, 'draft'),
                      (HIDDEN, 'hidden'),
                      (PUBLISHED, 'published'))

    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    content = RichTextField(config_name='full_toolbar', null=True, blank=True)
    caption = RichTextField(config_name='full_toolbar', null=True, blank=True)
    tag_list = TagField()
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True,
        default=datetime.date.today)
    modified = models.DateTimeField(auto_now=True, blank=True,
        default=datetime.date.today)
    template = RelativeFilePathField(
        path=settings.CMS_PAGE_TEMPLATE_PATH + "/",
        match=settings.CMS_PAGE_TEMPLATE_MATCH,
        default=settings.CMS_PAGE_TEMPLATE_DEFAULT,
        recursive=True
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    thumbnail = models.ImageField(null=True, blank=True, upload_to='pages_thumbnail_images')

    objects = PageManager()

    @property
    def index_page(self):
        "Find index page for this book"
        if not self.book.get_children().exists():
            return None
        return self.book.get_children()[0]

    @property
    def is_book(self):
        return self.parent is None

    @property
    def is_draft(self):
        return self.status == DRAFT

    @property
    def is_published(self):
        return self.status == PUBLISHED

    @property
    def is_hidden(self):
        return self.status == HIDDEN

    @property
    def book(self):
        """Find book associated with page"""
        if self.is_root_node():
            return self
        else:
            return self.get_root()

    @property
    def in_imas_book(self):
        """Find the book with the 'imas' slug"""
        return self.book.slug == 'imas'

    @property
    def in_resource_book(self):
        """Find the book with the 'resources' slug"""
        return self.book.slug == 'resources'

    @property
    def in_about_book(self):
        """Is this page in an about section?"""
        return hasattr(self.book, 'regionaboutpage')

    @property
    def region(self):
        """Return the region this page is associated with.  Specifically
        relevant for regional about pages."""
        try:
            return self.book.regionaboutpage.region
        except RegionAboutPage.DoesNotExist:
            return None

    @property
    def is_about_book(self):
        return self.is_book and (self == cached_copy['home'].about_book)

    @property
    def is_about_page(self):
        return not self.is_book and (self.book == cached_copy['home'].about_book)

    @property
    def is_region_about_book(self):
        return self.is_book and hasattr(self, 'regionaboutpage')

    @property
    def is_region_about_page(self):
        return not self.is_book and self.in_about_book

    class MPTTMeta:
        order_insertion_by = ['title']

    def get_edit_url(self):
        if self.is_book:
            return reverse('cms_book_edit', args=[self.id])
        else:
            return reverse('cms_page_edit', args=[self.book.id, self.id])

    def get_path(self):
        return '.'.join(map(lambda l: l.slug, self.get_ancestors()) + [self.slug])

    @models.permalink
    def get_public_url(self, region=None):
        if self.in_resource_book:
            if region:
                return ("region_cms_page", [region.slug, self.slug])
            else:
                return ("cms_page", [self.slug])
        elif self.is_about_book:
            return ("cms_about", [])
        elif self.is_about_page:
            return ("cms_about_page", [self.slug])
        elif self.is_region_about_book:
            return ("cms_region_about", [self.region.slug])
        elif self.is_region_about_page:
            return ("cms_region_about_page", [self.region.slug, self.slug])
        elif self.is_book:
            return ("cms_book", [self.book.slug])
        else:
            return ("cms_book_page", [self.book.slug, self.slug])

    @models.permalink
    def get_absolute_url(self):
        if self.is_root_node():
            return ("cms_book_detail", [self.pk])
        else:
            return ("cms_edit", [self.pk])

    class Meta:
        permissions = (
            ('add_book', 'Can add book'),
            ('change_book', 'Can change book'),
            ('delete_book', 'Can delete book'))

    def __unicode__(self):
        return self.title


class RegionAboutPage(models.Model):
    "Sitewide copy, meta data and the like"

    region = models.OneToOneField(Region)
    page = models.OneToOneField(Page)

    def __unicode__(self):
        return "{0} <-> {1}".format(self.region.description, self.page.title)


class CopyBlock(models.Model):

    slug = models.CharField(max_length=255, unique=True)
    text = RichTextField(config_name='full_toolbar', blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ("cms_copyblock_index", None)

    def __unicode__(self):
        return self.slug
