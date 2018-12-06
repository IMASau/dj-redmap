from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    SightingList, SightingDetail, UserSightingDetail,
    SpeciesList, SpeciesDetail,
    SpeciesCategoryList, SpeciesCategoryDetail,
    RegionList, RegionDetail,
    UserDetail, Register,
    SightingCreate, PersonDetail, SightingAttributeOptionsSerializerDetail,
    RegisterFacebookUser, UserSightingList
)

urlpatterns = patterns('redmap.apps.restapi.views',
    url(r'^$', 'api_root'),
    url(r'^sighting/$', SightingList.as_view(), name='sighting-list'),
    url(r'^sighting/create/$', SightingCreate.as_view(), name='sighting-create'),
    url(r'^sighting/options/$', SightingAttributeOptionsSerializerDetail.as_view(), name='sighting-options'),
    url(r'^sighting/(?P<pk>\d+)/$', SightingDetail.as_view(), name='sighting-detail'),
    url(r'^species/$', SpeciesList.as_view(), name='species-list'),
    url(r'^species/(?P<pk>\d+)/$', SpeciesDetail.as_view(), name='species-detail'),
    url(r'^category/$', SpeciesCategoryList.as_view(), name='speciescategory-list'),
    url(r'^category/(?P<pk>\d+)/$', SpeciesCategoryDetail.as_view(), name='speciescategory-detail'),
    url(r'^region/$', RegionList.as_view(), name='region-list'),
    url(r'^region/(?P<pk>\d+)/$', RegionDetail.as_view(), name='region-detail'),
    url(r'^user/profile/$', PersonDetail.as_view(), name='user-profile'),
    url(r'^user/detail/$', UserDetail.as_view(), name='user-detail'),
    url(r'^user/register-facebook/$', RegisterFacebookUser.as_view(), name='user-register-facebook'),
    url(r'^user/register/$', Register.as_view(), name='user-register'),
    url(r'^user/api-token-auth/', obtain_auth_token),
    url(r'^user/sighting/(?P<pk>\d+)/$', UserSightingDetail.as_view(), name='user-sighting-detail'),
    url(r'^user/sightings/$', UserSightingList.as_view(), name='sighting-list'),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
