import hashlib

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.datastructures import SortedDict
from django.utils.crypto import constant_time_compare
from django.utils.translation import ugettext_noop as _


class RedmapTasSHA1PasswordHasher(BasePasswordHasher):
    """
    The Redmap Tas version of SHA1 password hashing algorithm
    
    The difference is that we put the salt after the password before hashing
    """
    algorithm = "redmaptas_sha1"

    def encode(self, password, salt):
        assert password
        assert salt and '$' not in salt
        hash = hashlib.sha1(password + salt).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])


