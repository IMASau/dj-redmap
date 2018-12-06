from redmap.apps.redmapdb.models import Region
from django.conf import settings
from redmap.apps.frontend.models import Sponsor


def testing_flag(request):
    return {
        'TESTING': settings.TESTING
    }


def site_base(request):
    return {
        'national_sponsors': Sponsor.objects.national(),
        'facebook_redmap_namespace': settings.FACBOOK_REDMAP_NAMESPACE,
        'facebook_redmap_sighting_object': settings.FACBOOK_REDMAP_SIGHTING_OBJECT,
        'facebook_redmap_app_id': settings.FACEBOOK_APP_ID,
        'facebook_redmap_app_scope': ','.join(settings.FACEBOOK_DEFAULT_SCOPE),
    }
