from .managers import RedmapModel, RedmapManager
from redmap.common.decorators import deprecated
from redmap.common.util import reverse_lazy
from redmap.common.sql import distinct_by_annotation
from datetime import datetime
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import SiteProfileNotAvailable, Group
from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, Min
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django_facebook.models import FacebookProfileModel, OpenGraphShare
from redmap.apps.redmapdb.emails import alert_assignee, thank_sighter, alert_reassignee
from registration.models import RegistrationProfile
from redmap.apps.redmapdb.emails import alert_assignee, thank_sighter
from django.utils.safestring import mark_safe

from registration.signals import user_activated
from tagging.fields import TagField
from tagging.models import Tag
from django.shortcuts import redirect
from django.contrib.auth.models import User


if not settings.REDMAP_MODELS_USE_MSSQL:
    from .utils import find_region


def login_on_activation(sender, user, request, **kwargs):
    """Logs in the user after activation"""
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    if not user.profile:
        get_or_create_profile(user)

# Registers the function with the django-registration user_activated signal
user_activated.connect(login_on_activation)


PHOTO_MATCHES_SPECIES_MAYBE = 2
PHOTO_MATCHES_SPECIES_YES = 1
PHOTO_MATCHES_SPECIES_NO = 0

PHOTO_MATCHES_SPECIES_CHOICES = (
    (PHOTO_MATCHES_SPECIES_YES, 'Yes'),
    (PHOTO_MATCHES_SPECIES_NO, 'No'),
    (PHOTO_MATCHES_SPECIES_MAYBE, 'Maybe'),
)


class SpeciesTaxonomicGroup(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    description = models.CharField(max_length=50, db_column=u'description')
    update_time = models.DateTimeField(
        db_column=u'update_time', null=True, auto_now_add=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'MB_SPECIES_TAXONOMIC_GROUP'

    def __unicode__(self):
        return u"%s" % self.description


class SpeciesReportGroup(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    description = models.CharField(max_length=50, db_column=u'description')
    update_time = models.DateTimeField(
        db_column=u'update_time', null=True, auto_now_add=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'MB_SPECIES_REPORT_GROUP'

    def __unicode__(self):
        return u"%s" % self.description


class SpeciesInOtherGroup(models.Model):
    """
    TODO: species_id should be foreign key
    TODO: species_other_group - what does this do?
    """
    id = models.AutoField(db_column=u'id', primary_key=True)
    species_id = models.IntegerField(db_column=u'mb_species_id')
    species_other_group = models.IntegerField(
        db_column=u'mb_species_other_group_id')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'MB_SPECIES_IN_OTHER_GROUP'


class SpeciesManager(models.Manager):

    def sighted_species(self, region=None):
        """List of sighted species"""
        sightings = Sighting.objects.get_public()
        if region:
            sightings = sightings.filter(region=region)
        return distinct_by_annotation(
            Species.objects.filter(sightings__in=sightings))

    def get_redmap(self, category=None, region=None):
        '''Note: This will filter out any species which do not belong to a
        category. This is due to get_absolute_url failing if a category is not
        found.'''
        species = self.filter(active=True, speciesincategory__isnull=False)

        if category:
            species = species.filter(speciesincategory__species_category=category)

        if region:
            species = species.filter(speciesallocation__region=region)

        return distinct_by_annotation(species)


class SpeciesInterest(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'ID')
    name = models.CharField(max_length=255, db_column=u'NAME')

    class Meta:
        ordering = ['name']
        db_table = u'RM_SPECIES_INTEREST'

    def __unicode__(self):
        return u"%s" % self.name


class Species(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    species_name = models.CharField(max_length=128, db_column=u'species_name')
    caab_code = models.CharField(
        max_length=10, db_column=u'caab_code', null=True, blank=True)
    common_name = models.CharField(
        max_length=255, db_column=u'common_name', null=True, blank=True)
    html_name = models.CharField(
        max_length=128, db_column=u'html_name', null=True, blank=True)
    ### From MySQL DB
    short_description = models.TextField(
        db_column=u'short_description', null=True, blank=True)
    description = models.TextField(
        db_column=u'description', null=True, blank=True)
    related = models.TextField(db_column=u'related', null=True, blank=True)
    active = models.BooleanField(
        db_column=u'active', default=False,
        verbose_name="is active",
        help_text="Indicates whether the species should be visible on website. "
                  "Set to false to hide false to archive old species or keep "
                  "new species hidden until it's ready for publishing.")
    picture_url = models.ImageField(
        upload_to="species", db_column=u'picture_url',
        null=True, blank=True, max_length=512)
    image_credit = models.CharField(
        blank=True, null=True, default="", max_length=100,
        help_text="The name of the person the photo is credited to.  Full name only.")
    habitat = models.TextField(
        db_column=u'habitat', null=True, blank=True)
    ###
    family = models.CharField(
        max_length=64, db_column=u'family', null=True, blank=True)
    order = models.CharField(
        max_length=64, db_column=u'order', null=True, blank=True)
    class_field = models.CharField(
        max_length=64, db_column=u'class', null=True, blank=True)
    phylum = models.CharField(
        max_length=64, db_column=u'phylum', null=True, blank=True)
    genus = models.CharField(
        max_length=64, db_column=u'genus', null=True, blank=True)
    species_epithet = models.CharField(
        max_length=128, db_column=u'species_epithet', null=True, blank=True)
    authority = models.CharField(
        max_length=128, db_column=u'authority', null=True, blank=True)
    reference = models.CharField(
        max_length=255, db_column=u'reference', null=True, blank=True)
    history = models.CharField(
        max_length=255, db_column=u'history', null=True, blank=True)
    species_taxonomic_group = models.ForeignKey(
        SpeciesTaxonomicGroup, db_column=u'mb_species_taxonomic_group_id',
        null=True)
    species_report_group = models.ForeignKey(
        SpeciesReportGroup, db_column=u'mb_species_report_group_id',
        null=True)
    distribution_latitude_south_limit = models.DecimalField(
        decimal_places=12, max_digits=18,
        db_column=u'distribution_latitude_south_limit',
        null=True, blank=True)
    notes = models.TextField(db_column=u'notes', null=True, blank=True,
        help_text='Shown on the species page, under the "Notes:" heading. '
                  'Should give more information about when to log sightings.')
    update_time = models.DateTimeField(
        db_column=u'update_time', null=True, auto_now_add=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    species_interests = models.ManyToManyField(SpeciesInterest, through=u'SpeciesSpeciesInterestRelation')

    objects = SpeciesManager()

    class Meta:
        db_table = u'MB_SPECIES'
        verbose_name = "species"
        verbose_name_plural = "species"
        ordering = ['species_name']

    def get_absolute_url(self):

        first_species_category = self.speciesincategory_set.all()[0]
        return reverse_lazy('species_detail', kwargs={
            'category': first_species_category.species_category_id,
            'pk': self.pk})

    @property
    def tag(self):
        slug = slugify(self.species_name)
        return Tag.objects.get_or_create(name=slug)

    def __unicode__(self):
        if self.common_name:
            species_name = "%s ( %s )" % (self.common_name, self.species_name)
        else:
            species_name = self.species_name
        return u"%s" % species_name


"""
class SpeciesDistributionGeo(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    reference_date = models.DateTimeField(
        db_column=u'reference_date', null=True)
    distribution = models.CharField(max_length=254, db_column=u'distribution')
    habitat = models.CharField(max_length=254, db_column=u'habitat', null=True)
    depth_min = models.DecimalField(
        decimal_places=6, max_digits=18, db_column=u'depth_min', null=True)
    depth_max = models.DecimalField(
        decimal_places=6, max_digits=18, db_column=u'depth_max', null=True)
    species = models.ForeignKey(Species, db_column=u'mb_species_id')
    #geog = models.CharField() # TODO: geog should be `geometry` type field
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'MB_SPECIES_DISTRIBUTION_GEO'
"""


class Accuracy(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=7, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_ACCURACY'
        verbose_name = "accuracy"
        verbose_name_plural = "accuracy"

    def __unicode__(self):
        return u"%s" % self.description


class Sex(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_SEX'
        verbose_name = "sex"
        verbose_name_plural = "sexes"

    class StoredProcedureMeta:
        pass

    def __unicode__(self):
        return u"%s" % self.description


class Count(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_COUNT'

    def __unicode__(self):
        return u"%s" % self.description


class WeightMethod(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_WEIGHT_METHOD'

    def __unicode__(self):
        return u"%s" % self.description


class SizeMethod(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_SIZE_METHOD'

    def __unicode__(self):
        return u"%s" % self.description


class Habitat(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_HABITAT'

    def __unicode__(self):
        return u"%s" % self.description


class Method(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_METHOD'

    def __unicode__(self):
        return u"%s" % self.description


class Activity(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_ACTIVITY'
        verbose_name = "activity"
        verbose_name_plural = "activities"

    def __unicode__(self):
        return u"%s" % self.description


class Time(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_TIME'

    def __unicode__(self):
        return u"%s" % self.description


class SightingManagerMixin:

    def get_sightings_for_user(self, user):
        """
        Return a queryset filtered for the sightings which the user has access to.

        Uses status_tracking to identify "was ever assigned".

        Regional administrators should also see everything in their region.
        """

        # Start with a filter for sightings where the user has a tracker for the sighting.
        filters = Q(sighting_tracking__person=user)

        # Add an OR query to the filters for sightings where the user is a regional admin of the sighting's region
        if user.get_profile().is_regional_admin:
            filters |= Q(region__administratorallocation__person=user)

        # This aggregate is our distinct bug around
        return distinct_by_annotation(self.filter(filters))

    def get_sightings_for_user_by_active_assignments(self, user):
        """
        Return a queryset of active assignments for a user.

        For Scientist:
        - all active assignments assigned

        For Regional Admin:
        - all active assignments assigned
        - all active assignments in region
        """
        qs = self.get_sightings_for_user(user)

        active_assignments = SightingTracking.active_assignments.all()

        if not user.get_profile().is_regional_admin:
            # If the user is not a regional admin, filter sightings for where the active assignment is owned by the user
            active_assignments.filter(person=user)

        return distinct_by_annotation(
            qs.filter(sighting_tracking__in=active_assignments))

    def get_valid_sightings_verified_by_scientist(self, user):
        """
        Return a queryset of active sightings which were verified by this scientist.

        For Scientist:
        - all valid sightings assignments assigned

        For Regional Admin:
        - all active assignments assigned
        - all active assignments in region
        """
        qs = self.get_sightings_for_user(user).filter(sighting_tracking__sighting_tracking_status__code=settings.VALID_SIGHTING)
        return distinct_by_annotation(qs)

    def get_public(self):
        '''
        Fetch a list of public-safe sightings. These may or may not be verified
        sightings, however, they should be checked by either a scientist or and
        admin and flagged as published.
        '''
        sightings_list = self.filter(is_published=True).order_by('-published_date')

        return sightings_list

    def get_verified_or_valid(self):
        '''
        Filter for verified or valid sightings, yes there's a different.
        '''
        return self.filter(is_valid_sighting=True).filter(Q(is_verified_by_scientist=True) | Q(is_checked_by_admin=True))

    def get_public_photo(self):
        sightings_list = self.get_public().filter(
            # TODO: check with peter.  include maybe?
            photo_matches_species=PHOTO_MATCHES_SPECIES_YES,
            photo_url__isnull=False,
        ).exclude(photo_url='')

        return sightings_list

    def get_recent(self, sighting=None):
        '''
        If a sample sighting is provided, filter the list
        returned to be the same species as the sample is.
        '''
        if sighting and sighting.species:
            sightings_list = self.get_public_photo(
            ).filter(species=sighting.species).exclude(pk=sighting.id)
        elif sighting and sighting.other_species:
            sightings_list = self.get_public_photo().filter(
                other_species=sighting.other_species).exclude(
                    pk=sighting.id)
        else:
            sightings_list = self.get_public_photo()

        return sightings_list[:3]

    def get_recent_sightings_in_area(self, sighting=None):
        '''Find a list of recent sightings in a given area'''
        if sighting and sighting.region:
            return self.get_public_photo().\
                filter(region=sighting.region).exclude(pk=sighting.id)[:3]
        else:
            return None

    def in_known_range(self, sighting):
        """
        TODO: This should be used when routing sightings for validation but
              currently isn't used anywhere in the codebase.
        """

        if not sighting.species:
            raise Species.DoesNotExist

        # Use workaround when MSSQL isn't available
        if not settings.REDMAP_MODELS_USE_MSSQL:
            return True

        return self.function_species_in_range(
            sighting.species.id, sighting.latitude, sighting.longitude)


class SightingManagerQuerySet(QuerySet, SightingManagerMixin):
    pass


class SightingManager(SightingManagerMixin, RedmapManager):

    def get_query_set(self):
        return SightingManagerQuerySet(self.model, using=self._db)

    def quick_log(self, *args, **kwargs):
        sighting = Sighting(**kwargs)
        sighting.sighting_date = datetime.now()
        for field, model in [('time', Time), ('user', User)]:
            if not hasattr(sighting, field):
                setattr(sighting, field, model.objects.all()[0])
        sighting.save()
        return sighting

    def log_with_data(self, user, sighting_data, from_mobile=False):

        # Create a fresh sighting instance
        sighting = Sighting()

        # Populate fields based on sighting_data
        fields = [f.name for f in Sighting._meta.fields]
        for field, value in sighting_data.iteritems():
            if field in fields:
                setattr(sighting, field, value)

        # Associate with sighter
        sighting.user = user

        # set the mobile flags
        sighting.from_mobile = from_mobile

        # save the sighting
        sighting.save()

        # assign the sighting
        self.assign_sighting(sighting)

        return sighting

    def assign_sighting(self, sighting):
        """
        Assign the sighting to an expert for validation
        """
        if not sighting.pk:
            raise self.model.DoesNotExist('The Sighting must be committed to the database before assignment.')

        # assign the sighting to an expert
        expert, comment = sighting.pick_expert_with_comment()
        sighting.assign(expert, comment)

        # Send a confirmation email to the sighter
        thank_sighter(sighting)

        return expert, comment


class Organisation(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    description = models.CharField(max_length=50, db_column=u'description')
    blurb = models.TextField(db_column=u'blurb', null=True, blank=True)
    url = models.CharField(db_column=u'url', max_length=255, null=True,
                           blank=True, verbose_name="URL")  # fields
    citation = models.CharField(max_length=128, db_column=u'citation')
    image_url = models.ImageField(
        upload_to="organisations", db_column=u'image_url', null=True,
        max_length=512, blank=True, verbose_name="Image URL")
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_ORGANISATION'

    def __unicode__(self):
        return u"%s" % self.description


class Jurisdiction(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    description = models.CharField(max_length=50, db_column=u'description')
    organisation = models.ForeignKey(
        Organisation, db_column=u'rm_organisation_id')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_JURISDICTION'

    def __unicode__(self):
        return "%s" % self.description


class RegionManager(RedmapManager):

    def get_by_coordinates(self, latitude, longitude):

        # Use workaround when MSSQL isn't available
        if not settings.REDMAP_MODELS_USE_MSSQL:
            name = find_region(float(latitude), float(longitude))
            try:
                return Region.objects.get(description=name)
            except Region.DoesNotExist:
                return Region.objects.get(description="Tasmania")

        region_id = self.function_get_sighting_region(latitude, longitude)
        return Region.objects.get(pk=region_id)


class Region(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    description = models.CharField(max_length=50, db_column=u'description')
    # Ie. Tasmanian, Victorian (Queensland remains Queensland)
    ownership =\
        models.CharField(max_length=50, db_column=u'ownership')
    slug = models.SlugField(max_length=50, db_column=u'slug')
    jurisdiction = models.ForeignKey(
        Jurisdiction, db_column=u'rm_jurisdiction_id')
    email = models.EmailField()
    #geog = models.CharField() #TODO: should be geometry type field
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    objects = RegionManager()

    def get_absolute_url(self):
        return reverse('region_landing_page',
                       kwargs={'region_slug': self.slug})

    @property
    def owner(self):
        """For regions like Tasmania, we want to diplay some links as on the
        site like "Tasmanian News". For regions like Queensland, the same link
        would look like "Queensland News". If a region has an "ownership"
        description set, display that - otherwise, display the description."""

        if self.ownership:
            return self.ownership
        else:
            return self.description

    @property
    def contact_email(self):
        if self.email:
            return self.email
        else:
            return settings.ENQUIRIES_EMAIL

    @property
    def scientists(self):
        return self.jurisdiction.organisation.person_set.all()

    @property
    def categories(self):
        return SpeciesCategory.objects.filter(
            speciesincategory__species__speciesallocation__region=self).distinct()

    class Meta:
        db_table = u'RM_REGION'

    def __unicode__(self):
        return "%s" % self.description


class Sighting(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    user = models.ForeignKey(User, db_column=u'registered_user_id', related_name="sightings")
    sighting_date = models.DateTimeField(db_column=u'sighting_date')
    published_date = models.DateTimeField(db_column=u'published_date', blank=True, null=True)

    is_verified_by_scientist = models.BooleanField(
        verbose_name="Verified by scientist",
        db_column=u'is_verified_by_scientist',
        default=False,
        help_text="Indicates whether the sighting has been verified by a scientist. "
                  "Used as a flag to stamp sightings 'verified by scientist' on website.")

    is_checked_by_admin = models.BooleanField(
        verbose_name="Checked by admin",
        help_text="Indicates whether the sighting was checked by an administrator. "
                  "Not used currently but could be used to flag public sightings which "
                  "have not undergone formal verification but are considered appropriate "
                  "for public display.",
        db_column=u'is_checked_by_admin',
        default=False)

    is_not_displayed = models.BooleanField(
        verbose_name="Don't display this sighting",
        db_column=u'is_not_displayed',
        default=False,
        editable=False,
        help_text="This flag has been deprecated - use IS_PUBLISHED. "
                  "Setting this flag blocks the sighting from being "
                  "displayed to public under any circumstances.  Used"
                  "hiding a sensitive sightings ignoring the verification "
                  "process. May be useful for scientifically useful photos "
                  "evicence which are not appropriate for public display.")

    is_published = models.BooleanField(
        verbose_name="Display on site",
        db_column=u'is_published',
        default=False,
        help_text="Setting this flag will display this sighting on the public "
                  "site. This includes un-verified sightings.")

    latitude = models.DecimalField(
        decimal_places=12, max_digits=18, db_column=u'latitude', null=True)
    longitude = models.DecimalField(
        decimal_places=12, max_digits=18, db_column=u'longitude', null=True)
    accuracy = models.ForeignKey(
        Accuracy, db_column=u'rm_accuracy_id', null=True)
    species = models.ForeignKey(Species, db_column=u'mb_species_id', null=True,
        related_name="sightings", blank=True)
    other_species = models.CharField(
        max_length=512, db_column=u'other_species', null=True, blank=True,
        help_text="Please use format 'Latin name (common name)'")
    count = models.ForeignKey(Count, db_column=u'rm_count_id', null=True)
    sex = models.ForeignKey(Sex, db_column=u'rm_sex_id', null=True)
    size = models.IntegerField(db_column=u'size', null=True, blank=True)
    weight = models.DecimalField(db_column=u'weight',
        max_digits=11, decimal_places=3, null=True, blank=True)
    size_method = models.ForeignKey(
        SizeMethod, db_column=u'rm_size_method_id', null=True, blank=True)
    weight_method = models.ForeignKey(
        WeightMethod, db_column=u'rm_weight_method_id', null=True, blank=True)
    habitat = models.ForeignKey(
        Habitat, db_column=u'rm_habitat_id', null=True, blank=True)
    depth = models.IntegerField(db_column=u'depth', null=True, blank=True)
    water_temperature = models.IntegerField(
        db_column=u'water_temperature', null=True, blank=True)
    method = models.ForeignKey(
        Method, db_column=u'rm_method_id', null=True, blank=True)
    activity = models.ForeignKey(
        Activity, db_column=u'rm_activity_id', default=0)
    activity_other = models.CharField(
        max_length=50, db_column=u'activity_other', null=True, blank=True)
    time = models.ForeignKey(Time, db_column=u'rm_time_id', null=True, blank=True)
    photo_url = models.ImageField(upload_to="pictures", db_column=u'photo_url',
                                  blank=True, null=True, max_length=512)
    photo_caption = models.TextField(
        db_column=u'photo_caption', blank=True, null=True)
    exif = models.TextField(null=True, blank=True)

    photo_matches_species = models.IntegerField(
        db_column=u'photo_matches_species',
        default=PHOTO_MATCHES_SPECIES_NO,
        choices=PHOTO_MATCHES_SPECIES_CHOICES)
    is_out_of_range = models.BooleanField(
        db_column=u'is_out_of_range',
        default=False,
        help_text="Records whether this sighting was found to be out of "
                  "range when the sighting was processed.  This is not used "
                  "for reporting.  This is not set for 'other_species' "
                  "sightings")

    is_valid_sighting = models.BooleanField(
        db_column=u'is_valid_sighting',
        default=False,
        help_text="This sighting has been checked by an administrator or "
                  "validated by a scientist, and is not SPAM. May or may not "
                  "be a verified sighting.")

    notes = models.TextField(db_column=u'notes', blank=True, null=True)
    logging_date = models.DateTimeField(
        db_column=u'logging_date', default=datetime.now,
        null=True, blank=True)
    organisation = models.ForeignKey(
        Organisation, db_column=u'rm_organisation_id', null=True, blank=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)
    update_time = models.DateTimeField(
        db_column=u'update_time', null=True, auto_now_add=True)
    region = models.ForeignKey(
        Region, db_column=u'rm_region_id', null=True, blank=True)

    from_mobile = models.NullBooleanField(default=None, db_column=u'from_mobile')

    sighting_interests = models.ManyToManyField(SpeciesInterest, through=u'SightingSpeciesInterestRelation')

    objects = SightingManager()

    @property
    def categories(self):
        if self.species:
            return SpeciesCategory.objects.filter(
                speciesincategory__species=self.species)

    @property
    def has_photo(self):
        if self.photo_url:
            return True
        return False

    @property
    def verification_date(self):
        """
        Date used for public listings.  This will become an additional model
        field updated automatically when a scientist completes the
        verification process for a sighting.

        TODO: using logging_date as a patch for now
        """
        return self.logging_date

    @property
    def is_verified_sighting(self):
        return self.is_valid_sighting and self.is_verified_by_scientist

    @property
    @deprecated
    def is_displayed(self):
        """is_not_displayed is a bad property name from the old
        data base, leads to bugs, so heres a positive form of the
        property"""
        return not self.is_not_displayed

    @is_displayed.setter
    @deprecated
    def is_displayed(self, value):
        self.is_not_displayed = not value

    @property
    def detected_as_mobile_upload(self):
        if self.from_mobile is not None:
            return self.from_mobile

        if not self.photo_url:
            return False
        return '/android_api_photo' in self.photo_url.path or '/Photo-1' in self.photo_url.path

    def pick_expert(self):
        """
        Backward compatible wrapper around new pick_expert_with_comment
        function.
        """
        expert, comment = self.pick_expert_with_comment()
        return expert

    def pick_expert_with_comment(self):

        comments = []

        def retval(expert, comments_array):
            "Helper which builds string from comments"
            return (expert, "\n".join(comments_array))

        prior_experts = User.objects.filter(sightingtracking__sighting=self).distinct()

        if prior_experts:
            comments.append("People previously assigned the sighting:")
            for p in prior_experts:
                comments.append(" - {0}".format(p.__unicode__()))

        is_expert_sighting = SpeciesAllocation.objects.is_species_expert(
            self.species, self.user)

        is_other_species = self.species is None

        # Never send to a scientist unless there is a photo
        # Expert sightings should be verified by an administrator
        # "Other species" sightings should be verified by an administrator
        if self.photo_url and not is_expert_sighting and not is_other_species:

            comments.append("Looking for scientist with species allocation:")

            comments.append(" - Species is: {0}.".format(self.species))

            comments.append(" - Region is: {0}.".format(self.region))

            if self.is_out_of_range:
                comments.append(" - Sighting is outside known distribution.")
            else:
                comments.append(" - Sighting is within known distribution.")

            is_user_trusted = self.user.profile.is_trusted

            all_experts = SpeciesAllocation.objects.find_experts(
                self.species, self.region, self.is_out_of_range,
                is_user_trusted).exclude(person__in=prior_experts)

            if all_experts.exists():
                comments.append("Shortlisted scientists:")
                for expert_assignment in all_experts:
                    comments.append(" - {0}".format(expert_assignment.person.__unicode__()))
            else:
                comments.append("No matching experts found.")

            regional_experts = all_experts.exclude(region=None)

            if regional_experts.exists():
                comments.append("Picked scientist with regional assignment.")
                return retval(regional_experts.pick_expert(), comments)

            global_experts = all_experts.filter(region=None)

            if global_experts.exists():
                comments.append("Picked scientist with global assignment.")
                return retval(global_experts.pick_expert(), comments)

            comments.append("No expert match found.")

        else:

            comments.append("Didn't look for a scientist because:")

            if not self.photo_url:
                comments.append(" - no photo was provided")

            if is_expert_sighting:
                comments.append(" - sigher was an assigned species expert")

            if is_other_species:
                comments.append(" - other species sighting")

        # Assumption is that regional admins don't get to slack off.
        regional_admins = AdministratorAllocation.objects.find_regional_admins(
            self.region)

        if regional_admins:
            comments.append("Picked regional admin.")
            return retval(regional_admins.pick_regional_admin(), comments)
        else:
            comments.append("No regional admins found.")

        global_admins = Group.objects.get(name="Administrators").user_set.all()

        # TODO: no sophistication to manage many global admins yet
        # BUG: passing a user not a person
        comments.append("Picked global admin.")
        return retval(global_admins[0], comments)

    @property
    def tracker(self):
        "Fetch active tracker if there is one"
        return SightingTracking.objects.get_active_tracker(self)

    @property
    def latest_tracker(self):
        "Fetch latest tracker (any state)"
        return SightingTracking.objects.get_latest_tracker(self)

    @property
    def is_assigned(self):
        return self.tracker is not None

    def reassign(self, by_user, to_user, comment=None):
        SightingTracking.objects.reassign(self, to_user, comment or "No comment")
        alert_reassignee(self, by_user, to_user, comment)

    def assign(self, user, comment=None):
        SightingTracking.objects.assign(self, user, comment or "No comment")
        alert_assignee(self.tracker, comment)

    def _update_status_flags(self, is_valid, is_published):
        is_species_expert = self.latest_tracker.is_species_expert()
        is_verifiable = is_species_expert and self.has_photo
        if not self.published_date and is_published:
            self.published_date = datetime.now()
        self.is_valid_sighting = is_valid
        self.is_published = is_published
        self.is_verified_by_scientist = is_valid and is_verifiable
        self.is_checked_by_admin = is_valid and not is_verifiable

    def report_valid_without_photo(self, comment, is_displayed_on_site,
        is_published):
            SightingTracking.objects.report(
                self, True, comment=comment,
                is_displayed_on_site=is_displayed_on_site)
            self._update_status_flags(True, is_published)
            self.save()

    def report_valid_with_photo(self, photo_matches_species, comment,
        is_displayed_on_site, is_published):
        SightingTracking.objects.report(
            self, True, comment=comment,
            is_displayed_on_site=is_displayed_on_site)
        # TODO: if NO then there's something wrong
        self.photo_matches_species = photo_matches_species
        self._update_status_flags(True, is_published)
        self.save()

    def report_invalid(self, comment, is_published):
        SightingTracking.objects.report(
            self, False, comment=comment,
            is_displayed_on_site=False)
        self._update_status_flags(False, is_published)
        self.save()

    def report_spam(self, comment):
        SightingTracking.objects.report_spam(
            self, comment=comment, is_displayed_on_site=False)
        self.is_published = False
        self._update_status_flags(False, False)
        self.save()

    def save(self, *args, **kwargs):

        # Cached values for region / is_out_of_range when adding
        if self.pk is None:
            self.region = Region.objects.get_by_coordinates(
                self.latitude, self.longitude)
            # Out of range only makes sense if it's a known species (not other species)
            if self.species:
                self.is_out_of_range = not Sighting.objects.in_known_range(self)

        # Perform save
        return super(Sighting, self).save(*args, **kwargs)

    @property
    def species_name(self):
        '''This will display either the species scientific name, or the
        other_species field'''
        return self.species.species_name if self.species else self.other_species

    @property
    def common_name(self):
        '''Used in conjunction with the `species_name` above, this will display
        either the species common_name or "Other Species" when appropriate'''
        return self.species.common_name if self.species else 'Other species'

    @property
    def short_name(self):
        '''This is for templates where we just want to display the
        `common_name`, but also need to support `other_species` - such as the
        activity list on the homepage'''
        return self.species.common_name if self.species else self.other_species

    def get_sighting_status(self):
        """
        Descriptive status of the sighting for text (including description).
        Sightings are either just "sightings" or "verified sightings".
        Note: could be extended to other status if useful.
        """
        if self.latest_tracker.sighting_tracking_status.code == settings.VALID_SIGHTING:
            return "Verified sighting"
        return "sighting"

    def description(self):
        '''Descriptive text for use on website'''
        if self.latest_tracker.sighting_tracking_status.code == settings.VALID_SIGHTING:
            message = "Verified {0} sighting in {1} by {2}"
        else:
            message = "{0} sighting in {1} by {2}"
        return message.format(self.short_name, self.region, self.user.profile)

    def get_facebook_action_domain(self):
        args = [
            settings.FACBOOK_REDMAP_NAMESPACE,
            settings.FACBOOK_REDMAP_SIGHTING_ACTION,
        ]
        return u'{0}:{1}'.format(*args)

    def get_facebook_object_domain(self):
        args = [
            settings.FACBOOK_REDMAP_NAMESPACE,
            settings.FACBOOK_REDMAP_SIGHTING_OBJECT,
        ]
        return u'{0}:{1}'.format(*args)

    def post_to_facebook(self, request=None):
        share = OpenGraphShare.objects.create(user=self.user, action_domain=self.get_facebook_action_domain(), content_object=self)

        if request is None:
            # manually build the object url
            sighting_url = 'http://{0}{1}'.format(Site.objects.get_current().domain, self.get_absolute_url())
        else:
            sighting_url = request.build_absolute_uri(self.get_absolute_url())

        kwargs = {
            settings.FACBOOK_REDMAP_SIGHTING_OBJECT: sighting_url
        }
        share.set_share_dict(kwargs)
        share.save()
        share.send()

        return

        # send the share as a task
        #from redmap.apps.redmapdb.tasks import send_facebook_opengraphshare
        #send_facebook_opengraphshare(share.id)

    class Meta:
        db_table = u'RM_SIGHTING'
        ordering = ["-logging_date"]
        get_latest_by = "logging_date"

    def __unicode__(self):
        return "Sighting #%d" % (self.id)

    def get_absolute_url(self):
        return reverse('sighting_detail', args=[self.id])


class SightingTrackingStatus(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    code = models.CharField(max_length=3, db_column=u'code')
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_SIGHTING_TRACKING_STATUS'
        verbose_name = "sighting tracking status"
        verbose_name_plural = "sighting tracking statuses"

    def __unicode__(self):
        return self.description


class Person(FacebookProfileModel):
    id = models.AutoField(db_column=u'id', primary_key=True)
    user = models.OneToOneField(
            User, db_column=u'registered_user_id', null=True)
    postcode = models.CharField(max_length=4, db_column=u'postcode', default='', null=True, blank=True)
    phone = models.CharField(max_length=20, db_column=u'phone', default='', null=True, blank=True)
    mobile = models.CharField(max_length=20, db_column=u'mobile', default='', null=True, blank=True)
    organisation = models.ForeignKey(
        Organisation, db_column=u'cm_organisation_id', null=True, blank=True)
    image_url = models.ImageField(
        upload_to="avatars", db_column=u'image_url', null=True, blank=True,
        max_length=512, verbose_name="Profile image")
    trust_level = models.IntegerField(
        db_column=u'trust_level', default=0, null=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)
    is_available = models.BooleanField(db_column=u'is_available', default=True)

    occupation_interest = models.CharField(
        max_length=255, null=True, blank=True)

    # TODO: refactor to be Boolean
    joined_mailing_list_on_signup = models.IntegerField(null=True, blank=True)

    region = models.ForeignKey(Region, db_column=u'rm_region_id', null=True, blank=True)

    # extra scientist only fields
    website = models.URLField(null=True, blank=True)  # website_url would clash with with the facebook parent class
    facebook_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)

    tag_list = TagField()

    @property
    def is_trusted(self):
        """
        Is this someone who we trust sightings from?
        """
        return (self.is_regional_admin or
                self.is_scientist or
                self.trust_level > 0)

    @property
    def is_regional_admin(self):
        """
        Test if the person is identified as a regional administrator.
        """
        if hasattr(self, 'user'):
            if self.user.groups.filter(
                name="Regional Administrators").exists():
                return True
        return False

    @is_regional_admin.setter
    def is_regional_admin(self, value):
        group = Group.objects.get(name="Regional Administrators")
        if value:
            self.user.groups.add(group)
        else:
            self.user.groups.remove(group)

    @property
    def is_scientist(self):
        """
        Test if the person has the role of a scientist.
        These people are available for scientific validation assignments.
        """
        if hasattr(self, 'user'):
            if self.is_regional_admin or self.user.groups.filter(
                name='Scientists').exists():
                return True
        return False

    @is_scientist.setter
    def is_scientist(self, value):
        group = Group.objects.get(name="Scientists")
        if value:
            self.user.groups.add(group)
        else:
            self.user.groups.remove(group)

    @property
    @deprecated
    def is_site_admin(self):
        """
        Test if the person is a member of staff.  These people have low
        level access to database data using the raw Django admin interface.
        """
        if self.user.is_staff:
            return True
        return False

    @is_site_admin.setter
    @deprecated
    def is_site_admin(self, value):
        user = self.user
        user.is_staff = value
        user.save()

    @property
    def is_global_admin(self):
        """
        Test if the person has the role of a scientist.  These people are
        available for scientific validation assignments.
        """
        if hasattr(self, 'user'):
            if self.user.groups.filter(name='Administrators').exists():
                return True
        return False

    @is_global_admin.setter
    def is_global_admin(self, value):
        group = Group.objects.get(name="Administrators")
        if value:
            self.user.groups.add(group)
        else:
            self.user.groups.remove(group)

    def get_pending_activation(self):
        """
        Returns a queryset with a single RegistrationProfile results
        or an empty queryset
        """
        query_filter = ~Q(activation_key=RegistrationProfile.ACTIVATED) & Q(
            activation_key__isnull=False)
        return self.user.registrationprofile_set.filter(query_filter)[:1]

    def has_facebook_account(self):
        if self.facebook_id is not None:
            return True
        return False

    def post_facebook_registration(self, request):
        '''
        Behaviour after registering with facebook
        '''
        from django_facebook.utils import next_redirect
        response = next_redirect(request, default=settings.FACEBOOK_REGISTRATION_REDIRECT,
                                 next_key=['register_next', 'next'])
        response.set_cookie('fresh_registration', self.user_id)

        return response

    @property
    def pending_activation(self):
        """Returns the pending RegistrationProfile object"""
        try:
            return self.get_pending_activation()[0]
        except IndexError:
            return None

    @property
    def is_pending_activation(self):
        """Returns a boolean determining whether the member's user is
        pending activation"""
        if self.get_pending_activation().count():
            return True
        return False

    @property
    def display_name(self):
        '''
        User-friendly name for front-end application;

        Prefer:
         1) First Last
         2) First
         3) username

        To display profile name: {{ user.profile }}
        To display link to profile: {{ user.profile.get_link }}

        '''
        if self.user is None:
            return u"Person #{0}".format(self.pk)

        if self.user.first_name:
            return u"{0} {1}".format(self.user.first_name, self.user.last_name)
        else:
            return u'{0}'.format(self.user.username)

    @property
    def full_name(self):
        '''
        Scientist/admin-friendly name for back-end (panel);

        Prefer:
         1) First Last ( username )
         2) First ( username )
         3) username

        '''
        if self.user is None:
            return u"Person #{0}".format(self.pk)

        if self.user.first_name:
            return u'{0} {1} ( {2} )'.format(
                self.user.first_name,
                self.user.last_name,
                self.user.username
            )
        else:
            return u'{0}'.format(self.user.username)

    class Meta:
        db_table = u'CM_PERSON'
        verbose_name = "person"
        verbose_name_plural = "people"
        ordering = ['user__last_name']
        permissions = (
            ('can_access_dashboard', 'Can access dashboard'),
            ('can_manage_experts', 'Can manage experts'),
            ('can_manage_content', 'Can manage content'),
            ('can_manage_sightings', 'Can manage sightings'),
            ('can_export_sightings', 'Can export sightings'),
            ('can_export_all_sightings', 'Can export all sightings'),
        )

    def __unicode__(self):
        """
        This is the publically displayed handle.

        Note: Currently we use username but this may change to fullname as
        included in profile.
        """
        return self.display_name

    def get_link(self):
        return mark_safe("<a href='{0}'>{1}</a>".format(
            self.get_public_url(), self.display_name))

    def get_public_url(self):
        return reverse('view_profile', args=[self.user.username])

    def get_absolute_url(self):
        return reverse('profiles_profile_detail', (), {
            'username': self.user.username})


def get_or_create_profile(user):
    # TODO: Seems like a hack.  Look for a recommended approach.
    try:
        person, created = Person.objects.get_or_create(user=user)
        # TODO: save person if created?
        return person
    except MultipleObjectsReturned:
        return Person.objects.filter(user=user)[0]

User.profile = property(get_or_create_profile)


def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        Person.objects.get_or_create(user=instance)


"""
Oliver: check this isn't duplicating the functionality of
https://github.com/tschellenbach/Django-facebook/blob/master/django_facebook/models.py#L186\

Thomas: No it doesn't duplicate, djano_facebook checks if the profile models is django_facebook.FacebookProfile, it isn't
as we have our profile model inherits.

Oliver: This line breaks the loaddata management command.
"""
post_save.connect(create_facebook_profile, sender=User)


class SightingTrackingManager(models.Manager):

    def __init__(self, code=None):
        super(SightingTrackingManager, self).__init__()
        self.code = code

    def get_query_set(self):
        """
        Our manager can be setup with status code filtering.
        """
        qs = super(SightingTrackingManager, self).get_query_set()
        if self.code is None:
            return qs
        return qs.filter(sighting_tracking_status__code=self.code)

    def get_latest_tracker(self, sighting):
        """
        Fetch the most recent tracker associated with a sighting.  Useful
        for checking the latest status or details of a completed report.
        """
        try:
            return self.filter(sighting=sighting).order_by('-tracking_date')[0]
        except (SightingTracking.DoesNotExist, IndexError):
            return None

    def get_active_tracker(self, sighting):
        try:
            return self.get(sighting=sighting,
                sighting_tracking_status__code=settings.REQUIRES_VALIDATION)
        except SightingTracking.MultipleObjectsReturned:
            # TODO: report misconfiguration.
            # TODO: clear out stale trackers?
            return self.filter(sighting=sighting,
                sighting_tracking_status__code=settings.REQUIRES_VALIDATION)[0]
        except SightingTracking.DoesNotExist:
            return None

    def assign(self, sighting, user, comment):
        """
        Create a fresh sighting tracking instance for a sighting and assign
        it to a user.

        This is the one place SightingTracking objects are created.
        """

        if sighting.is_assigned:
            raise Exception("Already assigned")

        new_allocation = SightingTracking()
        new_allocation.sighting_tracking_status = \
            SightingTrackingStatus.objects.get(
                code=settings.REQUIRES_VALIDATION)
        new_allocation.sighting = sighting
        new_allocation.tracking_date = datetime.now()
        new_allocation.person = user
        new_allocation.comment = comment
        new_allocation.save()

    def reassign(self, sighting, user, comment):

        if not sighting.is_assigned:
            raise ObjectDoesNotExist("Can't reassign unassigned sighting")

        self._update(sighting, settings.REASSIGNED, comment=comment)
        self.assign(sighting, user, comment)

    def report_spam(self, sighting, **kwargs):
        return self._update(sighting, settings.SPAM_SIGHTING, **kwargs)

    def report(self, sighting, is_valid, **kwargs):
        """
        Submit a report about a sighting.
        """
        if is_valid:
            code = settings.VALID_SIGHTING
        else:
            code = settings.INVALID_SIGHTING

        return self._update(sighting, code, **kwargs)

    def _update(self, sighting, code, **kwargs):
        """
        Update a report with the details provided.

        Inputs:
        - sighting
        - code
        - comment (optional)
        - is_displayed_on_site (optional)

        Intended as a internal helper only.
        """
        if not sighting.is_assigned:
            raise ObjectDoesNotExist("Can't report on an unassigned sighting")

        allocation = sighting.tracker
        allocation.sighting_tracking_status = \
            SightingTrackingStatus.objects.get(code=code)
        if 'comment' in kwargs:
            allocation.comment = kwargs['comment']
        if 'is_displayed_on_site' in kwargs:
            allocation.is_displayed_on_site = kwargs['is_displayed_on_site']
        allocation.save()


class SightingTracking(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    sighting = models.ForeignKey(Sighting, db_column=u'rm_sighting_id',
                                 related_name="sighting_tracking")
    sighting_tracking_status = models.ForeignKey(
        SightingTrackingStatus, db_column=u'rm_sighting_tracking_status_id')
    tracking_date = models.DateTimeField(
        db_column=u'tracking_datetime', null=True)
    person = models.ForeignKey(User, db_column=u'cm_person_id')
    comment = models.TextField(db_column=u'comment', null=True, blank=True)
    is_displayed_on_site = models.BooleanField(
        db_column=u'is_displayed_on_site', default=False)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    objects = SightingTrackingManager()
    active_assignments = SightingTrackingManager(settings.REQUIRES_VALIDATION)
    valid_sightings = SightingTrackingManager(settings.VALID_SIGHTING)
    invalid_sightings = SightingTrackingManager(settings.INVALID_SIGHTING)
    spam_sightings = SightingTrackingManager(settings.SPAM_SIGHTING)

    def is_species_expert(self):
        return SpeciesAllocation.objects.is_species_expert(
            self.sighting.species, self.person)

    def description(self):
        '''Descriptive text for use on website'''
        status_code = self.sighting_tracking_status.code
        if status_code == settings.REQUIRES_VALIDATION:
            assessment_template = "Awaiting validation by {0}"
        elif status_code == settings.INVALID_SIGHTING:
            assessment_template =  "Reported as invalid by {0}"
        elif status_code == settings.VALID_SIGHTING:
            assessment_template = "Validated by {0}"
        else:
            assessment_template = "Status `{1}` assigned to {0}"

        assessment = assessment_template.format(self.person.profile, self.sighting_tracking_status)

        if self.is_displayed_on_site:
            assessment = assessment+": "+self.comment

        return assessment

    class Meta:
        db_table = u'RM_SIGHTING_TRACKING'
        ordering = ['-tracking_date']

    def __unicode__(self):
        return u"Sighting tracking #{0}".format(self.id)


class SpeciesCategory(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    description = models.CharField(max_length=50, db_column=u'description')
    ### From MySQL DB
    long_description = models.TextField(
        db_column=u'long_description', null=True, blank=True)
    picture_url = models.ImageField(
        upload_to="species_categories", db_column=u'picture_url', null=True,
        blank=True, max_length=512)
    ###
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_SPECIES_CATEGORY'
        verbose_name = "species category"
        verbose_name_plural = "species categories"

    def __unicode__(self):
        return "%s" % self.description


class SpeciesInCategory(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    species_category = models.ForeignKey(
        SpeciesCategory, db_column=u'rm_species_category_id')
    species = models.ForeignKey(Species, db_column=u'mb_species_id')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_SPECIES_IN_CATEGORY'
        verbose_name = "Species in Category"
        verbose_name_plural = "Species in Categories"


class FBGroupManager(models.Manager):

    def count_members(self, group):
        return PersonInGroup.objects.filter(group=group).count()


class FBGroup(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    image_url = models.ImageField(
        upload_to="FBGroup", db_column=u'image_url', null=True,
        blank=True, max_length=512, verbose_name="Group image")
    description = models.CharField(max_length=50, db_column=u'description')
    facebook_group = models.IntegerField(
        db_column=u'facebook_group', null=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)
    owner = models.ForeignKey(
        User, db_column=u'cm_person_id', null=True, blank=True)

    objects = FBGroupManager()

    class Meta:
        db_table = u'RM_GROUP'
        verbose_name = u'Group'
        verbose_name_plural = u'Groups'

    def __unicode__(self):
        return self.description


class PersonInGroup(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    group = models.ForeignKey(FBGroup, db_column=u'rm_group_id')
    person = models.ForeignKey(User, db_column=u'cm_person_id')
    status = models.IntegerField(db_column=u'status', null=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_PERSON_IN_GROUP'


class AdministratorAllocationMixin(object):


    def top_ranked_admins(self):
        """
        Sort by rank and return all of the admins with equal top rank.
        """
        min_rank = self.aggregate(Min('rank'))['rank__min']
        return self.filter(rank=min_rank)


    def pick_regional_admin(self):
        """
        Given a list of admin allocations, using rules:
        - Filter on top rank
        - Pick least busy
        """
        least_busy_admin = None
        count = None;

        for allocation in self.top_ranked_admins():

            current_jobs = SightingTracking.objects.filter(
                person=allocation.person,
                sighting_tracking_status__code=settings.REQUIRES_VALIDATION).\
                count()

            if count is None or current_jobs < count:
                count = current_jobs
                least_busy_admin = allocation.person

        if least_busy_admin is None:
            raise Exception('No suitable admin was found')
        else:
            return least_busy_admin


    def find_regional_admins(self, region):
        return self.filter(region=region).exclude(
            person__person__is_available=False).order_by('rank')


class AdministratorAllocationQuerySet(QuerySet, AdministratorAllocationMixin):
    pass


class AdministratorAllocationManager(
    models.Manager, AdministratorAllocationMixin):

    def get_query_set(self):
        return AdministratorAllocationQuerySet(self.model, using=self._db)


class AdministratorAllocation(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    region = models.ForeignKey(Region, db_column=u'rm_region_id', null=True)
    person = models.ForeignKey(User, db_column=u'cm_person_id')
    rank = models.IntegerField(db_column=u'rank', null=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    objects = AdministratorAllocationManager()

    class Meta:
        db_table = u'RM_ADMINISTRATOR_ALLOCATION'

    def __unicode__(self):
        return self.region.description


class Badge(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    image_url = models.ImageField(
        upload_to="badges", db_column=u'image_url', max_length=512)
    description = models.CharField(max_length=50, db_column=u'description')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_BADGE'

    def __unicode__(self):
        return "%s" % self.description


class BadgeInPerson(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    badge = models.ForeignKey(Badge, db_column=u'rm_badge_id')
    person = models.ForeignKey(User, db_column=u'cm_person_id')
    date_awarded = models.DateTimeField(db_column=u'date_awarded')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_BADGE_IN_PERSON'


class EmailResponse(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    description = models.CharField(max_length=50, db_column=u'description')
    details = models.TextField(db_column=u'details')
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    class Meta:
        db_table = u'RM_EMAIL_RESPONSE'

    def __unicode__(self):
        return "%s" % self.description


class SpeciesAllocationMixin(object):

    def is_available(self):
        """
        Filter to show only active assignments
        """
        return self.filter(person__person__is_available=True)

    def species_match(self, species):
        """
        Filter to show allocations for one species
        """
        return self.filter(species=species)

    def exact_region_match(self, region):
        """
        Find allocations specifically associated with one particular region.
        """
        return self.filter(region=region)

    def region_match(self, region):
        """
        Filter to only allocations considered for a region.
        """
        return self.filter(Q(region=None) | Q(region=region))

    def range_filter(self, is_out_of_range):
        """
        Filter expert allocations if sighting is not out of range
        and the expert doesn't want to see in range sightings
        """
        if not is_out_of_range:
            return self.filter(contact_in_range=True)
        return self

    def trusted_filter(self, is_trusted):
        """
        Filter expert allocations if sighting is not out of range
        and the expert doesn't want to see in range sightings
        """
        if is_trusted:
            return self.filter(contact_if_trusted=True)
        return self

    def find_experts(self, species, range, is_out_of_range, is_user_trusted):
        """
        Filter for expert allocations matching sighting details.
        Order by rank.
        """
        # TODO: should this use exact region match?
        return self.is_available().species_match(species).region_match(
            range).range_filter(is_out_of_range).trusted_filter(
            is_user_trusted).order_by('rank')

    def top_ranked_experts(self):
        """
        Sort by rank and return all of the experts with equal top rank.
        """
        min_rank = self.aggregate(Min('rank'))['rank__min']
        return self.filter(rank=min_rank)

    def pick_expert(self):
        """
        Given a list of expert allocations, using rules:
        - Filter on top rank
        - Pick least busy
        """
        least_busy_scientist = None
        count = None;

        for allocation in self.top_ranked_experts():

            current_jobs = SightingTracking.objects.filter(
                person=allocation.person,
                sighting_tracking_status__code=settings.REQUIRES_VALIDATION).\
                count()

            if count is None or current_jobs < count:
                count = current_jobs
                least_busy_scientist = allocation.person

        if least_busy_scientist is None:
            raise Exception('No suitable scientist was found')
        else:
            return least_busy_scientist


class SpeciesAllocationQuerySet(QuerySet, SpeciesAllocationMixin):
    """
    # Design note: Using a Mixin to allow DRY queryset chaining.
    # http://hunterford.me/django-custom-model-manager-chaining/
    """
    pass


class SpeciesAllocationManager(models.Manager, SpeciesAllocationMixin):

    def is_species_expert(self, species, person):
        return self.filter(person=person, species=species).exists()

    def get_query_set(self):
        return SpeciesAllocationQuerySet(self.model, using=self._db)


class SpeciesAllocation(models.Model):
    id = models.AutoField(db_column=u'id', primary_key=True)
    species = models.ForeignKey(
        Species, db_column=u'mb_species_id', null=False)
    region = models.ForeignKey(
        Region, db_column=u'rm_region_id', null=True, blank=True)
    person = models.ForeignKey(User, db_column=u'cm_person_id', null=False)
    rank = models.IntegerField(db_column=u'rank', null=True)
    contact_in_range = models.BooleanField(
        db_column=u'contact_in_range', default=True)
    contact_if_trusted = models.BooleanField(
        db_column=u'contact_if_trusted', default=True)
    update_number = models.IntegerField(db_column=u'update_number', default=1,
        editable=False)

    objects = SpeciesAllocationManager()

    class Meta:
        db_table = u'RM_SPECIES_ALLOCATION'

    def __unicode__(self):
        if self.region:
            region = self.region.description
        else:
            region = "All"
        return "Species Allocation (%s - %s) rank #%d - %s" % (
            self.species.common_name, region, self.rank, self.person)


class SightingSpeciesInterestRelation(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'ID')
    sighting = models.ForeignKey(Sighting, db_column=u'RM_SIGHTING_ID')
    species_interest = models.ForeignKey(SpeciesInterest, db_column=u'RM_SPECIES_INTEREST_ID')

    class Meta:
        db_table = u'RM_SIGHTING_SIGHTING_INTERESTS'
        auto_created = True


class SpeciesSpeciesInterestRelation(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'ID')
    species = models.ForeignKey(Species, db_column=u'MB_SPECIES_ID')
    species_interest = models.ForeignKey(SpeciesInterest, db_column=u'RM_SPECIES_INTEREST_ID')

    class Meta:
        db_table = u'MB_SPECIES_SPECIES_INTERESTS'
        auto_created = True
