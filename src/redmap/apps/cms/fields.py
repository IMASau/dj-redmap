"""
Patch FilePathField so it stores relative paths.
"""

from django.db import models
from django.forms import fields
import os


# form field
class RelativeFilePathFormField(fields.FilePathField):
    def __init__(self, path, *args, **kwargs):
        super(RelativeFilePathFormField, self).__init__(path, *args, **kwargs)
        choices = []
        for choice in self.choices:
            choices.append((os.path.relpath(choice[0], path), choice[1]))
        self.choices = choices


# model field
class RelativeFilePathField(models.FilePathField):
    
    def formfield(self, **kwargs):
        defaults = {
            'form_class': RelativeFilePathFormField,
        }
        defaults.update(kwargs)
        return super(RelativeFilePathField, self).formfield(**defaults)