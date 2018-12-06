# Create your views here.
from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import importlib, simplejson
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseServerError
import time
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.http import urlquote
import StringIO
import csv

progress_param = 'progress_uuid'


class ProgressBarUploadHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request=None):
        super(ProgressBarUploadHandler, self).__init__(request)
        self.progress_uuid = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        self.progress_uuid = self.request.GET.get(progress_param, None)

        # check a list of uuids for this session is availble, and that this post request is valid
        if 'progress_uuids' in self.request.session and self.progress_uuid in self.request.session['progress_uuids']:
            cache.set(self.progress_uuid, {
                'length': self.content_length,
                'uploaded': 0,
                'percentage': 0,
                'slower': 5,
            })

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        if self.progress_uuid:
            data = cache.get(self.progress_uuid)
            data['uploaded'] += self.chunk_size
            data['percentage'] = int(round(float(data['uploaded']) / float(self.content_length) * 100, 0))

            # slows upload for debug
            if settings.DEBUG and data['percentage'] > data['slower']:
                data['slower'] += 5
                time.sleep(1)

            cache.set(self.progress_uuid, data)

        return raw_data

    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        if self.progress_uuid:
            cache.delete(self.progress_uuid)


class UploadHandlerMixin(object):
    upload_handler = None

    def dispatch(self, request, *args, **kwargs):
        if not self.upload_handler is None:
            request.upload_handlers.insert(0, UploadHandlerMixin._instantiate_upload_handler(self.upload_handler, request))
        return _uploadhandler_dispatch(request, self, *args, **kwargs)

    @staticmethod
    def _instantiate_upload_handler(path, *args, **kwargs):
        i = path.rfind('.')
        module, attr = path[:i], path[i + 1:]
        try:
            mod = importlib.import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing upload handler module %s: "%s"' % (module, e))
        except ValueError, e:
            raise ImproperlyConfigured('Error importing upload handler module. Is FILE_UPLOAD_HANDLERS a correctly defined list or tuple?')
        try:
            cls = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "%s" upload handler backend' % (module, attr))
        return cls(*args, **kwargs)


@csrf_protect
def _uploadhandler_dispatch(request, view, *args, **kwargs):
    return super(UploadHandlerMixin, view).dispatch(request, *args, **kwargs)


def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_uuid = request.GET.get(progress_param, None)

    if progress_uuid and progress_uuid in request.session['progress_uuids']:
        data = cache.get(progress_uuid)
        return HttpResponse(simplejson.dumps(data))

    return HttpResponseServerError('Server Error: bad request')


class BaseCsvExportMixin(object):
    attachment_name = "csv-export"

    def get_attachment_header(self):
        filename = self.get_attachement_name() + '.csv'
        filename = unicode(filename)
        header = u'attachment; filename="{safe}"; filename*=UTF-8\'\'{fancy}'.format(
            safe=slugify(filename),
            fancy=urlquote(filename))
        return header

    def get_attachement_name(self):
        return self.attachment_name

    def make_csv_response(self, request, data, *args, **kwargs):
        response = HttpResponse(self.data_to_csv(data))
        response.content_type = 'text/csv'
        response['Content-Disposition'] = self.get_attachment_header()
        return response

    def data_to_csv(self, data):
        stream = StringIO.StringIO()
        cw = csv.writer(stream)
        for row in data:
            try:
                cw.writerow(row)
            except UnicodeEncodeError:
                import logging
                logger = logging.getLogger("django.request")
                logger.exception('Error Processing Sightings Export: \n' + str(row))
                continue
        return stream.getvalue()
