from redmap.apps.cms.models import Page, CopyBlock
from redmap.apps.cms.utils import cached_copy
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED


class CopyBlockLookup():
    """Access copyblock content by slug in templates """

    def __getitem__(self, slug):
        instance, created = CopyBlock.objects.get_or_create(slug=slug)
        return instance.text


def copy(request):

    try:
        resources = Page.objects.get(parent=None, slug='resources')
    except Page.MultipleObjectsReturned:
        resources = Page.objects.filter(parent=None, slug='resources')[0]
    except Page.DoesNotExist:
        resources = None

    return {
        'copy': cached_copy,
        'copyblock': CopyBlockLookup(),
        'books': Page.objects.root_nodes(),
        'resources': resources,
        'DRAFT': DRAFT,
        'HIDDEN': HIDDEN,
        'PUBLISHED': PUBLISHED,
    }
