from django.contrib import admin
from singleton_models.admin import SingletonModelAdmin
from redmap.apps.cms.models import *
from redmap.common.admin import make_published


class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'is_book']
    list_filter = ["status"]
    actions = [make_published]


admin.site.register(HomepageContent, SingletonModelAdmin)
admin.site.register(SitewideContent, SingletonModelAdmin)
admin.site.register(SightingContent, SingletonModelAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(RegionAboutPage)
admin.site.register(CopyBlock)
