from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext, loader

from filemanager import views as filemanager_views


def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context:
        MEDIA_URL
            Path of static media (e.g. "media.example.org")
    """
    t = loader.get_template(template_name)
    try:
        c = RequestContext(request, {'STATIC_URL': settings.STATIC_URL, 'MEDIA_URL': settings.MEDIA_URL})
    except Exception, e:
        raise e
        return HttpResponse('error 500')
    r = t.render(c)
    return HttpResponseServerError(r)


# TODO Set some permissions around this
wrapped_handler = login_required(filemanager_views.handler)
