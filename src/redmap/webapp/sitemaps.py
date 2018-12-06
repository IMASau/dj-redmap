
from redmap.apps.cms.sitemaps import PageSitemap, HomepageSitemap
from redmap.apps.news.sitemaps import EntrySitemap
from redmap.apps.redmapdb.sitemaps import SpeciesSitemap

sitemaps = {

    # cms
    'home': HomepageSitemap,
    'page': PageSitemap,

    # news
    'entry': EntrySitemap,

    # species
    'species': SpeciesSitemap

}
