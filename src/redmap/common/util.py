import unicodedata

from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.utils.functional import lazy


def reverse_lazy(urlstring, *args, **kwargs):
    return lazy(reverse, str)(urlstring, *args, **kwargs)


def dms2dd(degrees, minutes, seconds):
    '''
    Converts degress, minutes and seconds to their equivalent
    number of decimal degrees
    '''

    decimal = 0.0
    if (degrees >= 0):
        decimal = degrees + (float(minutes) / 60) + (float(seconds) / 3600)
    else:
        decimal = degrees - (float(minutes) / 60) - (float(seconds) / 3600)

    return decimal


class ASCIIFileSystemStorage(FileSystemStorage):
    """
    Linux safe filename handler for uploads
    http://source.mihelac.org/2011/02/6/rename-uploaded-files-ascii-character-set-django/
    Convert unicode characters in name to ASCII characters.
    """
    def get_valid_name(self, name):
        name = unicodedata.normalize('NFKD', unicode(name)).encode('ascii', 'ignore')
        return super(ASCIIFileSystemStorage, self).get_valid_name(name)
