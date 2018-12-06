from .serializers import SightingSerializer, SpeciesSerializer, RegionSerializer, \
    UserSerializer, RegisterSerializer, CategorySerializer, UserSightingSerializer
from redmap.apps.restapi.serializers import serializers, FacebookSerializer
from django.contrib.auth.models import User
from django.core import serializers as django_serializers
from redmap.apps.redmapdb.models import Sighting, Species, SpeciesCategory, Region, Person, \
    Accuracy, Count, Sex, SizeMethod, WeightMethod, Habitat, Method, Activity, Time, \
    Organisation
from rest_framework import generics, renderers, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from redmap.apps.restapi.serializers import CreateSightingSerializer, PersonSerializer
import django_filters
from rest_framework.renderers import BrowsableAPIRenderer
import json
from django.utils.safestring import mark_safe
from django.http.multipartparser import parse_header
from django_facebook.registration_backends import FacebookRegistrationBackend
from django_facebook.utils import get_registration_backend, to_bool
from django_facebook.api import get_facebook_graph, FacebookUserConverter
from django_facebook.connect import CONNECT_ACTIONS, _login_user, _register_user,\
    connect_user
from django_facebook import exceptions as facebook_exceptions, \
    settings as facebook_settings, signals
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_facebook.views import _connect
from open_facebook.exceptions import OAuthException


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'sighting': reverse('sighting-list', request=request),
        'sighting_options': reverse('sighting-options', request=request),
        'sighting_create': reverse('sighting-create', request=request),
        'species': reverse('species-list', request=request),
        'category': reverse('speciescategory-list', request=request),
        'region': reverse('region-list', request=request),
        'user': reverse('user-detail', request=request),
        'register': reverse('user-register', request=request),
        'register_facebook': reverse('user-register-facebook', request=request),
    })


class Register(generics.CreateAPIView):
    """User registration through the API"""

    model = User
    serializer_class = RegisterSerializer

    def get_serializer(self, **kwargs):
        if not hasattr(self, '_cached_serializer'):
            self._cached_serializer = super(Register, self).get_serializer(**kwargs)
        return self._cached_serializer


class RegisterFacebookUser(generics.CreateAPIView):
    """User registration through facebook"""

    serializer_class = FacebookSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(RegisterFacebookUser, self).dispatch(*args, **kwargs)

    def create(self, request, **kwargs):
        user = None
        access_token = request.DATA.get('access_token', None)
        graph = get_facebook_graph(request, access_token)
        facebook = FacebookUserConverter(graph)
        try:
            assert facebook.is_authenticated()
        except OAuthException, ex:
            return Response({"error": ex.message}, status=status.HTTP_401_UNAUTHORIZED)

        facebook_data = facebook.facebook_profile_data()
        force_registration = True

        email = facebook_data.get('email', False)
        email_verified = facebook_data.get('verified', False)
        kwargs = {}

        if email and email_verified:
            kwargs = {'facebook_email': email}

        if email and not email_verified:
            """Error for edge case when the user account already exists for the FB email address but it is unverified"""
            if User.objects.filter(email=email).exists():
                return Response({'error': "Unverified facebook email address conflicts with an existing Redmap account"}, status=status.HTTP_401_UNAUTHORIZED)

        auth_user = authenticate(facebook_id=facebook_data['id'], **kwargs)
        action = None
        if auth_user and not force_registration:
            """
            Login and update only
            """
            action = CONNECT_ACTIONS.LOGIN

            # Has the user registered without Facebook, using the verified FB
            # email address?
            # It is after all quite common to use email addresses for usernames
            update = getattr(auth_user, 'fb_update_required', False)
            if not auth_user.get_profile().facebook_id:
                update = True
            #login the user
            user = _login_user(request, facebook, auth_user, update=update)
        else:
            """
            Create user
            """
            action = CONNECT_ACTIONS.REGISTER
            # when force registration is active we should remove the old profile
            try:
                action, user = connect_user(request, access_token)
            except facebook_exceptions.AlreadyRegistered:
                #in Multithreaded environments it's possible someone beats us to
                #the punch, in that case just login
                auth_user = authenticate(facebook_id=facebook_data['id'], **kwargs)
                action = CONNECT_ACTIONS.LOGIN
                user = _login_user(request, facebook, auth_user, update=False)

        response = super(RegisterFacebookUser, self).create(request, **kwargs)
        if user and user.id:
            response.data['id'] = user.id
            token, created = Token.objects.get_or_create(user=user)
            response.data['auth_token'] = token.key

        if action and action == CONNECT_ACTIONS.LOGIN:
            response.status_code = 200
        return response


class SightingFilter(django_filters.FilterSet):

    updated_at_min = django_filters.DateTimeFilter(
        name='update_time', lookup_type='gte')

    class Meta:
        model = Sighting
        filter_fields = ("region", "species")


class SightingList(generics.ListAPIView):
    """
    API endpoint that represents a list of sightings.

    Filters: region, species, updated_at_min
    """
    model = Sighting
    serializer_class = SightingSerializer
    filter_class = SightingFilter

    def get_queryset(self):
        return Sighting.objects.get_public()


class SightingDetail(generics.RetrieveAPIView):
    """
    API endpoint that represents a single sighting.
    """
    model = Sighting
    serializer_class = SightingSerializer

    def get_queryset(self):
        return Sighting.objects.get_public()


class UserSightingDetail(generics.RetrieveAPIView):
    """
    API endpoint that represents a single sighting for current user
    """
    model = Sighting
    serializer_class = UserSightingSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Sighting.objects.none()
        return Sighting.objects.filter(user=self.request.user)


class UserSightingList(generics.ListAPIView):
    """
    API endpoint that represents a list of sightings.

    Filters: region, species, updated_at_min
    """
    model = Sighting
    serializer_class = UserSightingSerializer
    filter_class = SightingFilter
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Sighting.objects.filter(user=self.request.user)


class SightingCreate(generics.CreateAPIView):
    """
    API endpoint to create represents a single sighting.
    """
    model = Sighting
    serializer_class = CreateSightingSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        """
        This method is overriden to correct user attributes on the Sighting model, most if
        this method comes from the stock CreateModelMixin.create method
        """
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            serializer.object.from_mobile = True
            serializer.object.user = request.user  # add the authed user as the creator
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            Sighting.objects.assign_sighting(self.object)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            if hasattr(self.object, 'pk'):
                serializer.data['pk'] = self.object.pk
                serializer.data['id'] = self.object.pk
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer(self, **kwargs):
        if not hasattr(self, '_cached_serializer'):
            self._cached_serializer = super(SightingCreate, self).get_serializer(**kwargs)
        return self._cached_serializer


class SpeciesFilter(django_filters.FilterSet):
    updated_at_min = django_filters.DateTimeFilter(
        name='update_time', lookup_type='gte')

    class Meta:
        model = Species


class SpeciesList(generics.ListAPIView):
    """
    API endpoint that represents a list of species.

    Filters: updated_at_min
    """
    model = Species
    queryset = Species.objects.get_redmap()
    serializer_class = SpeciesSerializer
    filter_class = SpeciesFilter


class SpeciesDetail(generics.RetrieveAPIView):
    """
    API endpoint that represents a single species.
    """
    model = Species
    queryset = Species.objects.get_redmap()
    serializer_class = SpeciesSerializer


class SpeciesCategoryDetail(generics.RetrieveAPIView):
    """
    API endpoint representing a species category details.
    """
    model = SpeciesCategory
    serializer_class = CategorySerializer


class SpeciesCategoryList(generics.ListAPIView):
    """
    API endpoint representing a species category list.
    """
    model = SpeciesCategory
    serializer_class = CategorySerializer


class RegionList(generics.ListAPIView):
    """
    API endpoint that represents a list of regions.
    """
    model = Region
    serializer_class = RegionSerializer


class RegionDetail(generics.RetrieveAPIView):
    """
    API endpoint that represents a single region.
    """
    model = Region
    serializer_class = RegionSerializer


class UserDetail(generics.RetrieveAPIView):
    """
    API endpoint that represents the user's profile.

    You must be authenticated to access your user profile.
    """
    model = User
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return self.request.user


class PersonDetail(generics.RetrieveAPIView):
    """
    API endpoint that represents the user's profile.

    You must be authenticated to access your user profile.
    """
    model = Person
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        return self.request.user.get_profile()


class PlainJsonRenderer(renderers.JSONRenderer):
    media_type = 'application/json'
    format = 'json'
    indent = 2

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            return u''

        renderer_context = renderer_context or {}
        indent = renderer_context.get('indent', self.indent)

        if accepted_media_type:
            base_media_type, params = parse_header(accepted_media_type.encode('ascii'))
            indent = params.get('indent', indent)
            try:
                indent = max(min(int(indent), 8), 0)
            except (ValueError, TypeError):
                indent = None

        json_response = json.dumps(dict(map(lambda key: (key, u"{0}_marker".format(key)), data.keys())), cls=self.encoder_class, indent=indent, ensure_ascii=self.ensure_ascii)

        for key in data.keys():
            objects = data.get(key, {}).get('objects', [])
            fields = data.get(key, {}).get('fields', None)
            serialized_objects = django_serializers.serialize('json', objects, fields=fields, indent=indent)
            json_response = json_response.replace(u'"{0}_marker"'.format(key), serialized_objects)

        return json_response


class SightingAttributeOptionsSerializerDetail(generics.GenericAPIView):
    """
    API endpoint that represents a single region.
    """
    #serializer_class = SightingAttributeOptionsSerializer
    serializer_class = serializers.Serializer
    renderer_classes = (PlainJsonRenderer, BrowsableAPIRenderer)

    def get(self, request, format=None):
        options = {
            'accuracy': {
                'objects': Accuracy.objects.all(),
            },
            'count': {
                'objects': Count.objects.all(),
            },
            'sex': {
                'objects': Sex.objects.all(),
            },
            'size_method': {
                'objects': SizeMethod.objects.all(),
            },
            'weight_method': {
                'objects': WeightMethod.objects.all(),
            },
            'habitat': {
                'objects': Habitat.objects.all(),
            },
            'method': {
                'objects': Method.objects.all(),
            },
            'activity': {
                'objects': Activity.objects.all(),
            },
            'time': {
                'objects': Time.objects.all(),
            },
            'organisation': {
                'objects': Organisation.objects.all(),
                'fields': ['description'],
            },
            'region': {
                'objects': Region.objects.all(),
                'fields': ['description', 'jurisdiction', 'slug'],
            },
        }

        return Response(options)
