from django.contrib.sitemaps import Sitemap
from models import Page, HomepageContent


class PageSitemap(Sitemap):

    items = Page.objects.get_published_pages

    def location(self, page):
        return page.get_public_url()

    def lastmod(self, page):
        return page.modified


class HomepageSitemap(Sitemap):

    items = HomepageContent.objects.all

    location = "/"

