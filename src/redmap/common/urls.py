from django.contrib.sites.models import Site


def fqdn(url, protocol="http"):
    """Resolve a fully-qualified domain name for url using sites package
       Make sure url starts with a /
    """

    if not url.startswith("/"):
        raise Exception("Unable to create FQDN from {0}".format(fqdn))

    site = Site.objects.get_current()
    return "{0}://{1}{2}".format(protocol, site.domain, url)
    