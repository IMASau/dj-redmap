from PIL import Image
from StringIO import StringIO
from redmap.common.urls import fqdn
from redmap.common.wms import get_distribution_url
from django.contrib.auth.models import User
from django.core import serializers as django_serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from redmap.apps.redmapdb.models import Sighting, Species, SpeciesCategory, Region, Person, \
    SpeciesAllocation, SpeciesCategory, Region, Person, Accuracy, Count, Sex, \
    SizeMethod, WeightMethod, Habitat, Method, Activity, Time, Organisation
from rest_framework import serializers, fields, status
from rest_framework.fields import ImageField
from rest_framework.response import Response
from rest_framework.reverse import reverse
from redmap.apps.restapi.extensions.serializers import PostModelSerializer
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.helpers import ThumbnailError
import base64
import magic


class FilterRelated(serializers.Field):
    """
    Helper class for generating links to filtered list views.
    """

    def __init__(self, view_name, filter_name, *args, **kwargs):
        self.view_name = view_name
        self.filter_name = filter_name
        super(FilterRelated, self).__init__(*args, **kwargs)

    def field_to_native(self, obj, field_name):
        url = reverse(self.view_name)
        return fqdn("{0}?{1}={2}".format(url, self.filter_name, obj.pk))


class ManyHyperlinkedRelatedMethodField(serializers.ManyHyperlinkedRelatedField):
    """
    Helper class for generating lists of related links not directly associated
    through a *-to-many model fields.
    """

    def __init__(self, method_name, *args, **kwargs):
        self.method_name = method_name
        kwargs['read_only']=True
        super(ManyHyperlinkedRelatedMethodField, self).__init__(*args, **kwargs)

    def field_to_native(self, obj, field_name):
        values = getattr(self.parent, self.method_name)(obj)
        if values:
            return map(self.to_native, values)


class ManyIdRelatedMethodField(serializers.ManyRelatedField):
    """
    Helper class for generating id lists of related objects not directly associated
    through a *-to-many model fields.
    """

    def __init__(self, method_name, field_name=None, *args, **kwargs):
        self.method_name = method_name
        self.field_name = field_name
        kwargs['read_only'] = True
        super(ManyIdRelatedMethodField, self).__init__(*args, **kwargs)

    def field_to_native(self, obj, field_name):
        field_name = self.field_name or field_name
        values = getattr(self.parent, self.method_name)(obj)
        if values:
            return map(lambda v: getattr(v, field_name), values)


class SightingSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    category_list = ManyHyperlinkedRelatedMethodField(
        'get_category_list', view_name="speciescategory-detail")

    class Meta:
        model = Sighting
        fields = (
            'id', 'url', 'species', 'other_species', 'is_published',
            'region', 'update_time', 'category_list'
        )

    def get_category_list(self, obj):
        return obj.categories


class UserSightingSerializer(SightingSerializer):
    accuracy = serializers.PrimaryKeyRelatedField()
    photo_url = serializers.SerializerMethodField('get_photo_url')
    species_id = serializers.SerializerMethodField('get_species_id', )
    region_id = serializers.SerializerMethodField('get_region_id')
    time = serializers.PrimaryKeyRelatedField()

    def get_photo_url(self, obj):
        if obj.photo_url == None:
            return None
        try:
            thumb = get_thumbnail(obj.photo_url, '1136x1136', quality=99)
            return fqdn(thumb.url)
        except (IOError, ThumbnailError):
            return None

    def get_species_id(self, obj):
        if obj.species != None:
            return obj.species.pk
        return None

    def get_region_id(self, obj):
        if obj.region != None:
            return obj.region.pk
        return None

    class Meta:
        model = Sighting
        fields = (
            'id', 'url', 'species', 'species_id', 'other_species', 'is_published',
            'region', 'region_id', 'update_time', 'category_list', 'latitude', 'longitude', 'accuracy', 'logging_date', 'is_valid_sighting', 'photo_url', 'sighting_date', 'time'
        )


class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    picture_url = serializers.SerializerMethodField('get_picture_url')
    sightings_url = FilterRelated('sighting-list', 'species')
    distribution_url = serializers.SerializerMethodField('get_distribution_url')
    category_list = ManyHyperlinkedRelatedMethodField(
        'get_category_list', view_name="speciescategory-detail")
    category_id_list = ManyIdRelatedMethodField(method_name="get_category_list", field_name="id")
    region_id_list = ManyIdRelatedMethodField(method_name="get_region_list", field_name="id")

    class Meta:
        model = Species
        fields = (
            'id', 'url', 'species_name', 'common_name', 'update_time',
            'short_description', 'description', 'image_credit',
            'picture_url', 'sightings_url', 'distribution_url',
            'category_list', 'category_id_list', 'region_id_list', 'notes'
        )

    def get_picture_url(self, species):
        try:
            thumb = get_thumbnail(species.picture_url, '640x640', quality=99)
            return fqdn(thumb.url)
        except (IOError, ThumbnailError):
            return None

    def get_distribution_url(self, species):
        return get_distribution_url(species.pk, width=200, height=200)

    def get_category_list(self, obj):
        return SpeciesCategory.objects.filter(speciesincategory__species=obj)

    def get_region_list(self, obj):
        return Region.objects.filter(speciesallocation__species=obj).distinct()


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    picture_url = serializers.SerializerMethodField('get_picture_url')

    def get_picture_url(self, obj):
        try:
            thumb = get_thumbnail(obj.picture_url, '200x200', quality=99)
            return fqdn(thumb.url)
        except (IOError, ThumbnailError):
            return None

    class Meta:
        model = SpeciesCategory
        fields = ('id', 'url', 'description', 'long_description', 'picture_url')


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    sightings_url = FilterRelated('sighting-list', 'region')
    category_list = ManyHyperlinkedRelatedMethodField(
        'get_category_list', view_name="speciescategory-detail")

    class Meta:
        model = Region
        fields = ('id', 'url', 'slug', 'description', 'sightings_url', 'category_list')

    def get_category_list(self, region):
        return region.categories


class UserSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    sightings = serializers.ManyPrimaryKeyRelatedField(
        read_only=True)

    region = serializers.SerializerMethodField('get_region_id')

    def get_region_id(self, obj):
        profile = obj.get_profile()
        if not profile or not profile.region:
            return None
        return profile.region.id

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'sightings',
            'region',
        )


class PersonSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    class Meta:
        model = Person
        fields = (
            'id',
            'joined_mailing_list_on_signup',
            'region',
        )


class RegisterSerializer(PostModelSerializer):

    join_mailing_list = fields.BooleanField(required=False)
    region = fields.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        self.base_fields['region'].choices = tuple([(None, '--None--')] + [(r.description, r.description) for r in Region.objects.all()])
        super(RegisterSerializer, self).__init__(*args, **kwargs)

    def validate_email(self, data, field_name):
        """
        Validate that the email is not already
        in use.
        """
        existing = User.objects.filter(email__iexact=data['email'])
        if existing.exists():
            raise fields.ValidationError("A user with that email already exists.")
        else:
            return data

    def to_native(self, obj):
        ret = super(RegisterSerializer, self).to_native(obj)
        ret['join_mailing_list'] = obj.get_profile().joined_mailing_list_on_signup
        ret['region'] = obj.get_profile().region.description
        return ret

    def save(self, **kwargs):
        user = super(RegisterSerializer, self).save(**kwargs)
        user.set_password(user.password)
        user.save()
        profile = user.get_profile()

        try:
            profile.region = Region.objects.get(description=self.cleaned_data['region'])
        except Region.DoesNotExist:
            profile.region = None
        profile.joined_mailing_list_on_signup = self.cleaned_data['join_mailing_list']
        profile.save()
        return user

    class Meta:
        model = User
        postonly_fields = ('password',)
        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'join_mailing_list',
            'region',
        )


class JsonBase64ImageFileField(ImageField):
    def field_from_native(self, data, files, field_name, reverted_data):
        if 'photo_url' not in files and 'photo_url' in data and 'photo_url_name' in data:
            decoded_image_data = base64.b64decode(data.get('photo_url'))

            # grab the mime type for the django file handler
            content_type_data = StringIO(decoded_image_data[:1024])
            content_type = magic.from_buffer(content_type_data.read(1024), mime=True)

            # grab file stream data
            uploaded_file = StringIO(decoded_image_data)

            kwargs = {
                'file': uploaded_file,
                'field_name': 'photo_url',
                'name': data.get('photo_url_name'),
                'content_type': content_type,
                'size': uploaded_file.len,
                'charset': None,
            }
            uploaded_file = InMemoryUploadedFile(**kwargs)
            files['photo_url'] = uploaded_file
            data.pop('photo_url')
            return super(JsonBase64ImageFileField, self).field_from_native(data, files, field_name, reverted_data)

        return super(JsonBase64ImageFileField, self).field_from_native(data, files, field_name, reverted_data)

    def to_native(self, value):
        return value.name


class CreateSightingSerializer(serializers.ModelSerializer):

    id = fields.IntegerField(read_only=True)
    pk = fields.IntegerField(read_only=True)
    photo_url = JsonBase64ImageFileField(required=False, max_length=512)

    class Meta:
        model = Sighting
        fields = (
            'pk',
            'id',
            'accuracy',
            'activity',
            'count',
            'depth',
            'habitat',
            'latitude',
            'longitude',
            'notes',
            'other_species',
            'photo_caption',
            'photo_url',
            'sex',
            'sighting_date',
            'size',
            'size_method',
            'species',
            'time',
            'water_temperature',
            'weight',
            'weight_method',
        )


class FacebookSerializer(serializers.Serializer):
    id = fields.IntegerField(read_only=True)
    access_token = fields.CharField(max_length=255)
    auth_token = fields.CharField(max_length=255, read_only=True)

    def save(self, **kwargs):
        pass
