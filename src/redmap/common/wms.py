
from django.conf import settings
from urllib import urlencode


def get_distribution_url(species_id, **kwargs):
    # Fetch defaults
    url = settings.WMS_BASE_URL
    params = settings.WMS_DISTRIBUTION_PARAMS.copy()
    # Update based on any kwargs
    params.update(kwargs)
    # Filter on species ID
    params['CQL_FILTER'] = "(ID={0})".format(species_id)
    # Build URL
    return settings.WMS_BASE_URL+"?"+urlencode(params)
