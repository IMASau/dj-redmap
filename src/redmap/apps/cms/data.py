from redmap.apps.cms.models import HomepageContent, SitewideContent
from redmap.apps.cms.models import SightingContent, RegionAboutPage, Page
from redmap.apps.redmapdb.models import Region
from zinnia.models import Category
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from tagging.models import Tag


def load_homepage_data():
    home_about_book, created = Page.objects.get_or_create(title="About Redmap (Book)",
        slug="home", status=PUBLISHED)

    home_about_page = Page.objects.create(title="About Redmap", slug="about-redmap",
        content="This is where we describe the Redmap project in the National context",
        status=PUBLISHED, parent=home_about_book)

    HomepageContent.objects.get_or_create(pk=1, defaults={
        'title': "Redmap",
        'subtitle': "Spot. Log. Map.",
        'about_book': home_about_book,
        'teaser':
            "Redmap, a new and interactive website, invites the Australian "
            "community to spot, log and map marine species that are uncommon "
            "in Australia, or along particular parts of our coast.",
        })


def load_singletons_data():
    SitewideContent.objects.get_or_create(pk=1, defaults={
        'site_title': "Redmap - Spot. Log. Map",
        'meta_description':
            "Redmap, a new and interactive website, invites the Australian "
            "community to spot, log and map marine species that are uncommon "
            "in Australia, or along particular parts of our coast."})

    SightingContent.objects.get_or_create(pk=1, defaults={
        'sighting_intro': (
            "Fill out this form with as many details as you have. "
            "Sightings are divided into two categories: "
            "those with photos and those without. "
            "If you attach a photo to your data form, "
            "REDMAP can classify the data as 'verified' "
            "and the data is considered more robust. "
            "\n\n "
            "If you don't have a photo please log your sighting anyway "
            "as it is still useful information! "
            "\n\n "
            "If you are unsure about what you have seen "
            "then please do not log your sighting. "
            "It is important to maintain the integrity of our database. "
            "You can still help REDMAP by telling "
            "other fishers and divers about the website!"),

        'sighting_photo_help_text': (
            "Please add a photo to your sighting so it can be verified by a "
            "scientist"),

        'sighting_photo_permission_text': (
            "I own all rights to this photo, and give permission for Redmap "
            "Australia to display it on their site"),

        'sighting_accuracy_label': (
            "Click on map to place a marker indicating the location of the sighting."
            "Alternatively enter the sighting coordinates manually below."
            "\n\nExact locations are private. We will only show sightings in half a degree square."),

        'sighting_details_intro': (
            "Thank you, we've saved those details. Now it's time for a little "
            "science&hellip;"
            "\n"
            "Please fill in any additional details you can provide relating "
            "to the sighting."),
        'sighting_confirmation_intro': (
            "Please confirm that the details below are correct then click "
            "submit"),

        'sighting_count_help_text': "Approximately how many did you see?",
        'sighting_weight_help_text': "What did your specimen weigh (in kg)?",
        'sighting_size_help_text': "How long was the specimen (in cm)?",
        'sighting_sex_help_text': "What gender was it?",
        'sighting_depth_help_text': "At what depth was the sighting made?",
        'sighting_habitat_help_text': "What habitat as the specimen in?",
        'sighting_temperature_help_text':
            "What was the water temperature (in degrees celcius)?"})


def load_regional_about_page_data():
    for region in Region.objects.all():
        rap = RegionAboutPage.objects.create(
            region=region,
            page=Page.objects.create(
                title="About Redmap %s (Book)" % (region.description,),
                slug=region.slug, status=PUBLISHED))
        page1 = Page.objects.create(
            title="About Redmap %s" % (region.description,),
            slug="about-%s" % region.slug, status=PUBLISHED,
            content="Find out about Redmap in %s here." % region.description,
            parent=rap.page)


def load_footer_page_data():
    footer_book = Page.objects.create(title='Footer links',
        slug='footer-links', status=PUBLISHED,
        parent=None)

    Page.objects.create(title='About Redmap (book)', slug='about',
        parent=footer_book, status=PUBLISHED)
    Page.objects.create(title='Sitemap', slug='sitemap',
        parent=footer_book, status=PUBLISHED)
    Page.objects.create(title='Copyright and Disclaimer',
        slug='legals', parent=footer_book, status=PUBLISHED)


def load_resources_data():
    article_category = Category.objects.create(
        title='Articles', slug='articles')

    resources_book = Page.objects.create(
        title='Resources', slug='resources', status=PUBLISHED)

    resources = [
        ('Marine Ecology', 'marine-ecology',),
        ('Climate change', 'climate-change',),
        ('Diving', 'diving',),
        ('Fishing', 'fishing',),
        ('Science', 'science',),
        ('Redmap Newsletter', 'redmap-newsletter',),
    ]

    for title, slug in resources:
        Page.objects.create(
            title=title, slug=slug, parent=resources_book,
            template='resource-listing.html', status=PUBLISHED)
        Tag.objects.create(name=slug)
    
    # Create the resource category listing page
    Page.objects.create(
        title="All resources",
        parent=resources_book,
        template="resource-page-listing.html",
        status=PUBLISHED)


def load_cms_data():
    """
    Populate the CMS with some basic data.  Only works once .

    Note: Make sure RedmapDB is populated first so regions are defined.
    """
    load_homepage_data()
    load_singletons_data()
    load_regional_about_page_data()
    load_footer_page_data()
    load_resources_data()
