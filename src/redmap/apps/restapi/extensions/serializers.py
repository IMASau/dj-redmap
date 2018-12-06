'''
Created on 19/06/2013

@author: thomas
'''

from rest_framework.serializers import ModelSerializer, ModelSerializerOptions
from django.core.exceptions import ValidationError


class PostModelSerializerOptions(ModelSerializerOptions):
    """
   Options for PostModelSerializer
   """

    def __init__(self, meta):
        super(PostModelSerializerOptions, self).__init__(meta)
        self.postonly_fields = getattr(meta, 'postonly_fields', ())


class PostModelSerializer(ModelSerializer):
    """
    Allows non-model extra fields to be posted and available, default rest-api
    behaviour is to attempt to save them against the model :/
    """
    _options_class = PostModelSerializerOptions

    def __init__(self, *args, **kwargs):
        super(PostModelSerializer, self).__init__(*args, **kwargs)
        self.cleaned_data = None
        self.non_model_fields = {}
        self.set_non_model_fields()

    def set_non_model_fields(self):
        model_attr_names = [field.attname for field in self.Meta.model._meta.fields]
        for field_name, field in self.fields.items():
            if field_name not in model_attr_names:
                self.non_model_fields[field_name] = field

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self.fields.items():
            if field_name in self.non_model_fields.keys() or field_name in self.opts.postonly_fields:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field

        # todo include non model field data
        return ret

    def restore_object(self, attrs, instance=None):
        model_attrs = {}
        non_model_attrs = {}
        post_attrs = {}
        self.cleaned_data = {}
        model_attr_names = [field.attname for field in self.Meta.model._meta.fields]
        for field, value in attrs.iteritems():
            if field in model_attr_names:
                model_attrs[field] = value
            elif field in self.opts.postonly_fields:
                post_attrs[field] = value
            else:
                non_model_attrs[field] = value

            self.cleaned_data[field] = value
        obj = super(PostModelSerializer, self).restore_object(model_attrs, instance)
        obj = self.process_postonly_fields(obj, post_attrs)
        obj = self.restore_non_model_attrs(obj, non_model_attrs)
        return obj

    def restore_non_model_attrs(self, obj, non_model_attrs):
        """
        Placeholder method for processing data sent in POST.
        """
        return obj

    def process_postonly_fields(self, obj, post_attrs):
        """
        Placeholder method for processing data sent in POST.
        """
        return obj

