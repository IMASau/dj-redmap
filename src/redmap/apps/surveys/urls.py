try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from .views import SurveryList, SurveyUpdate

urlpatterns = patterns(
    'backend/panel/admin/surveys',
    url(r'^list/$', SurveryList.as_view(), name="survey_list"),
    url(r'^edit/(?P<pk>\d+)/$', SurveyUpdate.as_view(), name="survey_update"),
)
