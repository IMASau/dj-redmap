from redmap.apps.backend.models import ConditionSection, SightingValidationCondition, \
    ValidationMessageTemplate, SightingValidationRule, RuleConditionTest
from redmap.common.tags import get_redmap_tag
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from random import choice, randint
from redmap.apps.redmapdb.models import Habitat, Activity, Species, Count, Region, \
    Jurisdiction, Organisation, Sighting, SightingTrackingStatus, SpeciesCategory, \
    SpeciesInCategory, Accuracy, SpeciesTaxonomicGroup, SpeciesReportGroup, Time, \
    Accuracy, Sex, WeightMethod, SizeMethod
from tagging.models import TaggedItem, Tag


TEST_USERS = (
    ('user1', 'User', 'One', 'u1@example.com', 'u1'),
    ('user2', 'User', 'Two', 'u2@example.com', 'u2'),
    ('user3', 'User', 'Three', 'u3@example.com', 'u3'),
    ('scientist1', 'Scientist', 'One', 's1@example.com', 's1'),
    ('scientist2', 'Scientist', 'Two', 's2@example.com', 's2'),
    ('scientist3', 'Scientist', 'Three', 's3@example.com', 's3'),
    ('regionaladmin1', 'Regional Admin', 'One', 'ra1@example.com', 'ra1'),
    ('regionaladmin2', 'Regional Admin', 'Two', 'ra2@example.com', 'ra2'),
    ('regionaladmin3', 'Regional Admin', 'Three', 'ra3@example.com', 'ra3'),
    ('siteadmin1', 'Site Admin', 'One', 'sa1@example.com', 'sa1'),
    ('admin1', 'Admin', 'One', 'a1@example.com', 'a1'),

    ('whatfineprint', 'Francis', 'Heath', 'fh@example.com', 'ff'),
    ('einszweiundeux', 'Matthew', 'Helm', 'mh@example.com', 'mh'),
    ('contract_star', 'Steven', 'Hooker', 'sh@example.com', 'sh'),
    ('nochemo', 'Kym', 'Howe', 'kh@example.com', 'kh'),
    ('duology', 'Damian', 'Istria', 'di@example.com', 'di'),
    ('valdame', 'Joshua', 'Jefferis', 'jj@example.com', 'jj'),
    ('delael', 'Leisel', 'Jones', 'lj@example.com', 'lj'),
    ('d6sense', 'Brad', 'Kahlefeldt', 'bk@example.com', 'bk'),
)


def load_test_users():
    """
    Load a set of known users with various roles for testing and bootstrapping.

    Notes:
    - Will throw errors if called repeatedly.
    - Not included in load_redmapdb_data.  Call separately.
    """

    def make_test_user(details):
        # Unpack args
        username, first_name, last_name, email, password = details

        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user

    users = dict((u.username, u) for u in map(make_test_user, TEST_USERS))

    users['scientist1'].profile.is_scientist = True
    users['scientist2'].profile.is_scientist = True
    users['scientist3'].profile.is_scientist = True
    users['regionaladmin1'].profile.is_regional_admin = True
    users['regionaladmin2'].profile.is_regional_admin = True
    users['regionaladmin3'].profile.is_regional_admin = True
    users['siteadmin1'].profile.is_staff = True
    users['admin1'].profile.is_global_admin = True

    users['superuser'] = User.objects.create_superuser(
        "superuser", "superuser@example.com", "su")


def load_validation_data():
    """
    TODO: move these models to redmapdb app
    """
    photo_checkboxes = ConditionSection.objects.create(
        name=settings.PHOTO_CHECKBOXES_SECTION)
    photo_radiogroup = ConditionSection.objects.create(
        name=settings.PHOTO_RADIOGROUP_SECTION)
    location_checkboxes = ConditionSection.objects.create(
        name=settings.LOCATION_CHECKBOXES_SECTION)
    characteristics_checkboxes = ConditionSection.objects.create(
        name=settings.CHARACTERISTICS_CHECKBOXES_SECTION)

    reported_correctly = SightingValidationCondition.objects.create(
        name="Reported characteristics match those expected",
        section=characteristics_checkboxes)

    photo_conditions = {}
    Q = settings.PHOTO_MATCHES_SPECIES_QUESTION
    for A in settings.PHOTO_MATCHES_SPECIES_ANSWERS:
        photo_conditions[A] = SightingValidationCondition.objects.create(
            name="%s - %s" % (Q, A),
            section=photo_radiogroup)

    valid_template = ValidationMessageTemplate.objects.create(
        name="Valid in-range sighting w/ photo",
        template="""
Thanks {sighter}

We were able to verify your photo sighting of a {species}
based on the details you provided.

Your sighting is now on the Redmap website here:
{sighting_url}

-- Redmap Team
        """)

    invalid_template = ValidationMessageTemplate.objects.create(
        name="Invalid sighting",
        template="""
            Hi {sighter}

            Thanks for taking the time to log a sighting on Redmap.

            Unfortunately we were unable to confirm it as a valid {species}
            sighting based on the details provided.

            Please do continue to contribute.  As a reminder, photos
            with accurate sighting details are important to the scientific
            process.

            -- Redmap Team
        """)

    valid_rule = SightingValidationRule.objects.create(
        name="Valid sighting",
        valid_photo=True,
        valid_sighting=True,
        validation_message_template=valid_template)
    valid_rule.condition_tests.create(
        condition=reported_correctly,
        test="Y")
    valid_rule.condition_tests.create(
        condition=photo_conditions["Yes"],
        test="Y")

    invalid_sighting_with_photo_rule = SightingValidationRule.objects.create(
        name="Invalid sighting with photo",
        valid_photo=True,
        valid_sighting=False,
        validation_message_template=invalid_template)

    invalid_sighting_no_photo_rule = SightingValidationRule.objects.create(
        name="Invalid sighting with out photo",
        valid_photo=False,
        valid_sighting=False,
        validation_message_template=invalid_template)


def load_test_sighting(**kwargs):
    """
    Create a dummy sighting using dummy data unless provided.
    Useful for test scripts.
    """
    sighting_data = {
        'user': User.objects.all()[0],
        'latitude': -42.1278,
        'longitude': 148.0761,
        'region': Region.objects.all()[0],
        'species': Species.objects.all()[0],
        'logging_date': datetime.now(),
        'sighting_date': datetime.now(),
        'time': Time.objects.all()[0],
        'photo_caption': '',
        "other_species": "",
        "accuracy": Accuracy.objects.get_or_create(code="10000", description="Within 10 kilometres")[0],
        "count": Count.objects.get_or_create(code="1", description="1")[0],
        "notes": "",
    }

    sighting_data.update(kwargs)

    return Sighting.objects.create(**sighting_data)


def load_test_sightings():
    regions = list(Region.objects.all())
    species = list(Species.objects.all())
    users = list(User.objects.filter(first_name='User'))

    pictures_you_may_not_have = [
        'pictures/south maori wrasse_1.jpg',
        'pictures/t100327_nursary steps_redspot-TD.jpg',
        'pictures/t100327_jervisbay_wrasseTD_1.jpg',
        'pictures/Surgeon copy.jpg',
        'pictures/Threadfin_Bfly__Swansea.JPG',
    ]

    for i in range(20):
        for user in users:
            load_test_sighting(
                user=user,
                region=choice(regions),
                species=choice(species),
                logging_date=datetime.now() - timedelta(days=randint(2, 50)),
                sighting_date=datetime.now() - timedelta(days=randint(2, 50)),
                photo_url=choice(pictures_you_may_not_have),
                is_published=True,
                is_checked_by_admin=True,
                is_valid_sighting=True
            )


def load_sighting_tracking_status_data():

    SightingTrackingStatus.objects.get_or_create(
        code=settings.VALID_SIGHTING)

    SightingTrackingStatus.objects.get_or_create(
        code=settings.INVALID_SIGHTING)

    SightingTrackingStatus.objects.get_or_create(
        code=settings.REQUIRES_VALIDATION)

    SightingTrackingStatus.objects.get_or_create(
        code=settings.REASSIGNED)

    SightingTrackingStatus.objects.get_or_create(
        code=settings.SPAM_SIGHTING)


REGION_DATA = (
    ("Tasmania", "tas", "IMAS"),
    ("Victoria", "vic", "Vic Test Organisation"),
    ("New South Wales", "nsw", "NSW Test Organisation"),
    ("Queensland", "qld", "QLD Test Organisation"),
    ("Western Australia", "wa", "WA Test Organisation"),
    ("South Australia", "sa", "SA Test Organisation"),)


def load_region_data():

    redmap_tag = get_redmap_tag()
    region_ct = ContentType.objects.get_for_model(Region)

    for (state, slug, orgname) in REGION_DATA:

        region_tag = Tag.objects.create(name=slug)

        org, onew = Organisation.objects.get_or_create(
            description=orgname)

        jur, jnew = Jurisdiction.objects.get_or_create(
            description="%s Jurisdiction" % state,
            organisation=org)

        region, created = Region.objects.get_or_create(
            description=state,
            slug=slug,
            jurisdiction=jur)

        TaggedItem.objects.get_or_create(
            tag=region_tag,
            content_type=region_ct,
            object_id=region.id)


def load_count_data():
    # TODO: Dummy data.  Update with real data.
    Count.objects.get_or_create(code="1", description="1")
    Count.objects.get_or_create(code="10", description="10")
    Count.objects.get_or_create(code="100", description="100")


SPECIES_DATA = {
    'Fish': [
        ('Blue morwong', 'Nemadactylus valenciennesi'),
        ('Crimsonband Wrasse', 'Notolabrus gymnogenis'),
        ('Dusky Morwong', 'Dactylophora nigricans')],
        # ...
    'Invertebrates': [
        ('Eastern King Prawn', 'Melicertus plebejus'),
        ('Eastern rock lobster', 'Sagmariasus verreauxi'),
        ('Firebrick Seastar', 'Asterodiscides truncatus'),
        ('Gloomy Octopus', 'Octopus tetricus'),
        ('Longspine sea urchin', 'Centrostephanus rodgersii')],
    'Sharks & Rays': [
        ('Australian angel shark', 'Squatina australis'),
        ('Eastern Fiddler Ray', 'Trygonorrhina fasciata'),
        ('Southern Fiddler Ray', 'Trygonorrhina dumerilii'),
        ('Tiger Shark', 'Galeocerdo cuvier')],
    'Algae and Marine Plants': [
        ('Red tide', 'Noctiluca scintillans')],
    'Turtles': [
        ('Green turtles', 'Chelonia mydas'),
        ('Hawksbill Turtle', 'Eretmochelys imbricata'),
        ('Leathery turtle', 'Dermochelys coriacea'),
        ('Loggerhead Turtle', 'Caretta caretta')]}


def load_species_data():

    for category_name, species_list in SPECIES_DATA.items():

        category = \
            SpeciesCategory.objects.get_or_create(description=category_name)[0]

        for species_data in species_list:

            species, new_species = Species.objects.get_or_create(
                species_name=species_data[1], common_name=species_data[0],
                active=True)

            SpeciesInCategory.objects.get_or_create(
                species=species, species_category=category)

            # This is a get-or-create property, so accesing it is enough to
            # create the tag
            species_tag = species.tag


GROUP_PERMISSIONS = {
    'Administrators': [
        'auth.change_user',
        'backend.add_sightingvalidationcondition',
        'backend.add_sightingvalidationrule',
        'backend.add_validationmessagetemplate',
        'backend.change_sightingvalidationcondition',
        'backend.change_sightingvalidationrule',
        'backend.change_validationmessagetemplate',
        'backend.delete_sightingvalidationcondition',
        'backend.delete_sightingvalidationrule',
        'backend.delete_validationmessagetemplate',
        'cms.add_book',
        'cms.change_book',
        'cms.delete_book',
        'cms.add_page',
        'cms.change_page',
        'cms.delete_page',
        'cms.add_copyblock',
        'cms.change_copyblock',
        'cms.delete_copyblock',
        'cms.add_homepagecontent',
        'cms.change_homepagecontent',
        'cms.delete_homepagecontent',
        'frontend.change_faq',
        'frontend.change_sponsor',
        'frontend.change_sponsorcategory',
        'frontend.delete_faq',
        'frontend.delete_sponsor',
        'frontend.delete_sponsorcategory',
        'privatebeta.change_inviterequest',
        'redmapdb.can_access_dashboard',
        'redmapdb.can_manage_content',
        'redmapdb.can_manage_experts',
        'redmapdb.change_administratorallocation',
        'redmapdb.change_organisation',
        'redmapdb.can_manage_sightings',
        'redmapdb.change_sighting',
        'redmapdb.change_sightingtracking',
        'redmapdb.change_speciesallocation',
        'redmapdb.delete_administratorallocation',
        'redmapdb.delete_organisation',
        'redmapdb.delete_sighting',
        'redmapdb.delete_speciesallocation',
        'tagging.change_tag',
        'zinnia.can_view_all',
        'zinnia.change_entry',
        'zinnia.delete_entry',
    ],
    'Regional Administrators': [
        'auth.change_user',
        'cms.add_page',
        'cms.change_page',
        'cms.delete_page',
        'redmapdb.can_access_dashboard',
        'redmapdb.can_manage_content',
        'redmapdb.can_manage_experts',
        'redmapdb.can_manage_sightings',
        'redmapdb.change_sighting',
        'redmapdb.change_sightingtracking',
        'redmapdb.change_speciesallocation',
        'redmapdb.delete_sighting',
        'redmapdb.delete_speciesallocation',
        'zinnia.can_view_all',
        'zinnia.change_entry',
        'zinnia.delete_entry',
    ],
    'Scientists': [
        'redmapdb.can_access_dashboard',
        'redmapdb.change_sighting',
        'redmapdb.change_sightingtracking',
    ]
}


def load_group_data():

    # Create the groups
    Group.objects.get_or_create(name="Administrators")
    Group.objects.get_or_create(name="Regional Administrators")
    Group.objects.get_or_create(name="Scientists")

    # Apply group permissions
    for group_name, permission_uids in GROUP_PERMISSIONS.items():
        group = Group.objects.get(name=group_name)
        for permission_uid in permission_uids:
            app_label, codename = permission_uid.split(".")
            permission = Permission.objects.get(
                codename=codename, content_type__app_label=app_label)
            group.permissions.add(permission)


def load_activity_data():
    Activity.objects.get_or_create(code="F", description="Fishing")
    Activity.objects.get_or_create(code="D", description="Diving")
    Activity.objects.get_or_create(code="S", description="Swimming")
    Activity.objects.get_or_create(code="B", description="Boating")
    Activity.objects.get_or_create(code="C", description="Beach combing")


def load_habitat_data():
    Habitat.objects.get_or_create(code="RE", description="Reef")
    Habitat.objects.get_or_create(code="SA", description="Sand")
    Habitat.objects.get_or_create(code="SE", description="Seagrass")


def load_size_method_data():
    SizeMethod.objects.get_or_create(code="M", description="Measured")
    SizeMethod.objects.get_or_create(code="E", description="Estimated")


def load_weight_method_data():
    WeightMethod.objects.get_or_create(code="M", description="Measured")
    WeightMethod.objects.get_or_create(code="E", description="Estimated")


def load_sex_data():
    Sex.objects.get_or_create(code="U", description="Unknown")
    Sex.objects.get_or_create(code="M", description="Male")
    Sex.objects.get_or_create(code="F", description="Female")
    Sex.objects.get_or_create(code="J", description="Juvenile")


def load_accuracy_data():
    Accuracy.objects.get_or_create(code="10", description="Within 10 metres")
    Accuracy.objects.get_or_create(code="100", description="Within 100 metres")
    Accuracy.objects.get_or_create(
        code="1000",
        description="Within 1 kilometre")
    Accuracy.objects.get_or_create(
        code="10000",
        description="Within 10 kilometres")


def load_time_data():
    Time.objects.get_or_create(code="00", description="00:00 am (Midnight)")
    Time.objects.get_or_create(code="01", description="01:00 am")
    Time.objects.get_or_create(code="02", description="02:00 am")
    Time.objects.get_or_create(code="03", description="03:00 am")
    Time.objects.get_or_create(code="04", description="04:00 am")
    Time.objects.get_or_create(code="05", description="05:00 am")
    Time.objects.get_or_create(code="06", description="06:00 am")
    Time.objects.get_or_create(code="07", description="07:00 am")
    Time.objects.get_or_create(code="08", description="08:00 am")
    Time.objects.get_or_create(code="09", description="09:00 am")
    Time.objects.get_or_create(code="10", description="10:00 am")
    Time.objects.get_or_create(code="11", description="11:00 am")
    Time.objects.get_or_create(code="12", description="12:00 pm (Noon)")
    Time.objects.get_or_create(code="13", description="01:00 pm")
    Time.objects.get_or_create(code="14", description="02:00 pm")
    Time.objects.get_or_create(code="15", description="03:00 pm")
    Time.objects.get_or_create(code="16", description="04:00 pm")
    Time.objects.get_or_create(code="17", description="05:00 pm")
    Time.objects.get_or_create(code="18", description="06:00 pm")
    Time.objects.get_or_create(code="19", description="07:00 pm")
    Time.objects.get_or_create(code="20", description="08:00 pm")
    Time.objects.get_or_create(code="21", description="09:00 pm")
    Time.objects.get_or_create(code="22", description="10:00 pm")
    Time.objects.get_or_create(code="23", description="11:00 pm")


def load_redmapdb_data():
    load_sighting_tracking_status_data()
    load_region_data()
    load_count_data()
    load_species_data()
    load_group_data()
    load_activity_data()
    load_habitat_data()
    load_size_method_data()
    load_weight_method_data()
    load_sex_data()
    load_accuracy_data()
    load_time_data()
    load_validation_data()


def load_all_data():
    load_redmapdb_data()
    load_test_users()
    load_test_sightings()
