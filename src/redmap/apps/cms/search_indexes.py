from haystack.indexes import *
from haystack import site
from models import Page


class PageIndex(SearchIndex):

    title = CharField(model_attr='title', boost=1.125)
    slug = CharField(model_attr='slug', boost=1.125)
    tag_list = CharField(model_attr='tag_list', boost=1.125)
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        return Page.objects.get_published_pages()


site.register(Page, PageIndex)
