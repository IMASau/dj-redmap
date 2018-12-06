from django.views.generic import ListView
from django.views.generic.edit import UpdateView

from .forms import SurveyUpdateForm
from .models import Survey


class SurveryList(ListView):
    model = Survey

class SurveyUpdate(UpdateView):
    model = Survey
    form_class = SurveyUpdateForm
    success_url = '../../list'
