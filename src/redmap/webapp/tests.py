"""
This test suite uses selenium to run thought some interface tests.

It uses the webapp URLs and a "Page Object" style to run through user workflows.

Notes: 
 - requires external local selenium server to provide browser
 - requires static files be inaccessable to avoid JS / CSS problems (intended to work with HTML only) 
"""

from redmap.apps.cms.data import load_cms_data
from django.test import LiveServerTestCase
from selenium import webdriver
from django.core import mail
from redmap.apps.redmapdb.data import load_redmapdb_data, load_test_users
import re
import unittest
from redmap.apps.redmapdb.models import Sighting    
from os import path
from urlparse import urlparse


HOME_PAGE_TITLE                     = "Welcome"
LOGIN_PAGE_TITLE                    = "Sign in"
LOG_SIGHTING_COMPLETE_PAGE_TITLE    = "Log a sighting" # TODO: sensible title
LOG_SIGHTING_PAGE1_TITLE            = "Add Sighting"   # TODO: unique title
LOG_SIGHTING_PAGE2_TITLE            = "Add Sighting"   # TODO: unique title
LOG_SIGHTING_PAGE3_TITLE            = "Add Sighting"   # TODO: unique title
PANEL_DASHBOARD_PAGE_TITLE          = "Scientist Panel"
PANEL_SIGHTINGS_PAGE_TITLE          = "Scientist Panel" # TODO: unique title
PANEL_EXPERTS_PAGE_TITLE            = "Scientist Panel" # TODO: unique title
PANEL_EXPERTS_ASSINGMENT_PAGE_TITLE = "Scientist Panel" # TODO: unique title
PANEL_CONTENT_PAGE_TITLE            = "Scientist Panel" # TODO: unique title
PANEL_ADMINISTRATION_PAGE_TITLE     = "Scientist Panel" # TODO: unique title
PROFILE_PAGE_TITLE                  = "My REDMAP"
REGISTER_ACTIVATED_PAGE_TITLE       = "Activation complete"
REGISTER_COMPLETE_PAGE_TITLE        = "Activation email sent"
REGISTER_FORM_PAGE_TITLE            = "Create an account"


class PanelPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/')
        self.dashboad       = self.client.find_link("Dashboard")
        self.sightings      = self.client.find_link("Sightings")

    def goto_sightings_page(self):
        self.sightings.click()
        return PanelSightingsPage(self.client)

    def goto_expert_panel_page(self):
        self.client.find_link("Validation panel").click()
        return PanelExpertsAssignmentsPage(self.client)

    def goto_content_page(self):
        self.client.find_link("Content").click()
        return PanelContentNewsPage(self.client)

    def goto_administration_page(self):
        self.client.find_link("Administration").click()
        return PanelAdministrationMembersPage(self.client)


class PanelSightingsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/sightings/')
        self.require_validation_link = self.client.find_link("Require validation")
        self.all_sightings_link      = self.client.find_link("All sightings")
        self.filter_username         = self.client.find_id("filter_username")
        self.filter_species          = self.client.find_id("filter_species")


class PanelExpertsAssignmentsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/assignments/')
        
        self.species_experts_link  = self.client.find_link("Species Experts")
        self.regional_admins_link  = self.client.find_link("Regional Admins")
        self.validation_rules_link = self.client.find_link("Validation rules")
        self.templates_link        = self.client.find_link("Templates")
        self.conditions_link       = self.client.find_link("Conditions")

        self.filter_username       = self.client.find_select("filter_username", by="id")
        self.filter_region         = self.client.find_select("filter_region", by="id")
        self.filter_species        = self.client.find_select("filter_species", by="id")

        self.add_link              = self.client.find_link("Add species expert")

    def add_species_expert(self, data):
        self.add_link.click()
        return PanelExpertsAssignmentsAddPage(self.client).add_species_expert(data)
        
    def goto_regional_admins(self):
        self.regional_admins_link.click()
        return PanelExpertsAllocationsPage(self.client)

    def goto_validation_rules(self):
        self.validation_rules_link.click()
        return PanelExpertsRulesPage(self.client)

    def goto_templates(self):
        self.templates_link.click()
        return PanelExpertsTemplatesPage(self.client)

    def goto_conditions(self):
        self.conditions_link.click()
        return PanelExpertsConditionsPage(self.client)


class PanelExpertsAssignmentsAddPage():
    
    def __init__(self, client):
        
        self.client = client
        self.client.assert_path_equals('/panel/experts/assignments/add/')

        self.species          = self.client.find_select("species")
        self.region           = self.client.find_select("region")
        self.person           = self.client.find_select("person")
        self.rank             = self.client.find_input("rank")
        self.contact_in_range = self.client.find_input("contact_in_range")

        self.submit           = self.client.find_submit()
        self.cancel           = self.client.find_link("Cancel")

    def enter_data(self, data):

        if 'region' in data:
            self.region(data["region"]).click()
            
        if 'species' in data:
            self.species(data["species"]).click()

        if 'person' in data:
            self.person(data["person"]).click()
                          
        if 'rank' in data:
            self.rank.send_keys(data["rank"])
            
        if 'contact_in_range' in data:
            self.contact_in_range.click()

    def add_species_expert(self, data):
        self.enter_data(data)
        self.submit.click()
        self.client.assert_no_errors()
        return PanelExpertsAssignmentsPage(self.client)


class PanelExpertsAllocationsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/allocations/')
        
        self.filter_username = self.client.find_id("filter_username")
        self.filter_region = self.client.find_id("filter_region")

        self.add_link = self.client.find_link("Add regional administrator")

    def add_regional_admin(self, data):
        self.add_link.click()
        return PanelExpertsAllocationsAddPage(self.client).add_regional_admin(data)


class PanelExpertsAllocationsAddPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/allocations/add/')
        
        self.region = self.client.find_select("region")
        self.person = self.client.find_select("person")
        self.rank   = self.client.find_select("rank")
        # self.update_number    TODO: shouldn't have update_number
        self.submit = self.client.find_submit()
        self.cancel = self.client.find_link("Cancel")

    def enter_data(self, data):
        
        if 'region' in data:
            self.region(data['region']).click()
            
        if 'person' in data:
            self.person(data['person']).click()
            
        if 'rank' in data:
            self.rank(data['rank']).click()    

    def add_regional_admin(self, data):
        self.enter_data(data)
        self.submit.click()
        return PanelExpertsAllocationsPage(self.client)


class PanelExpertsRulesPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/rules/')
        self.add_link = self.client.find_link("Add validation rule")
    
    def add_validation_rule(self, data):
        self.add_link.click()
        return PanelExpertsRulesAddPage(self.client).add_validation_rule(data)


class PanelExpertsRulesAddPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/rules/add/')
        self.rule_name         = self.client.find_input("name")
        self.rule_priority     = self.client.find_select("rank")
        self.valid_sighting    = self.client.find_radio("valid_sighting")
        self.valid_photo       = self.client.find_radio("valid_photo")
        # self.additonal_rules = # TODO: 
        self.template          = self.client.find_input("validation_message_template")
        self.submit            = self.client.find_submit()
        self.cancel            = self.client.find_link("Cancel")
    
    def enter_data(self, data):
        
        if 'rule_name' in data: 
            self.rule_name.send_keys(data['rule_name'])
            
        if 'rule_priority' in data:
            self.rule_priority(data['rule_priority']).click()
            
        if 'valid_sighting' in data: 
            self.valid_sighting(data['valid_sighting']).click()
            
        if 'valid_photo' in data: 
            self.valid_photo(data['valid_photo']).click()
                        
        if 'template' in data: 
            self.template(data['template']).click()
    
    def add_validation_rule(self, data):
        self.enter_data(data)
        self.submit.click()
        return PanelExpertsRulesPage(self.client)


class PanelExpertsTemplatesPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/templates/')
        self.add_link = self.client.find_link("Add template")

    def add_template(self, data):
        self.add_link.click()
        return PanelExpertsTemplatesAddPage(self.client).add_template(data)


class PanelExpertsTemplatesAddPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/templates/add/')
        self.name     = self.client.find_input("name")
        self.template = self.client.find_input("template")
        self.submit   = self.client.find_submit()
        self.cancel   = self.client.find_link("Cancel")

    def enter_data(self, data):
        if 'name' in data: 
            self.name.send_keys(data['name'])
        if 'template' in data: 
            self.template.send_keys(data['template'])
        
    def add_template(self, data):
        self.enter_data(data)
        self.submit.click()
        return PanelExpertsTemplatesPage(self.client)


class PanelExpertsConditionsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/conditions/')
        self.add_link = self.client.find_link("Add validation condition")

    def add_condition(self, data):
        self.add_link.click()
        return PanelExpertsConditionsAddPage(self.client).add_condition(data)


class PanelExpertsConditionsAddPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/experts/conditions/add/')
        self.name    = self.client.find_input("name")
        self.step    = self.client.find_select("step")
        self.section = self.client.find_select("section")
        self.submit  = self.client.find_submit()
        self.cancel  = self.client.find_link("Cancel")
        # TODO: "Templates" pil is highlighted when on this page.  SHould be "Conditions" pil

    def enter_data(self, data):
        if 'name' in data: 
            self.name.send_keys(data['name'])
        if 'step' in data: 
            self.step(data['step']).click()
            self.client.fail("refactored wizard won't need step")
        if 'section' in data:
            self.section(data['section']).click()
    
    def add_condition(self, data):
        self.enter_data(data)
        self.submit.click()
        return PanelExpertsConditionsPage(self.client)


class PanelContentPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/content/')
        self.client.fail("incomplete")


class PanelAdministrationMembersPage():
    
    def __init__(self, client):
        self.client               = client
        self.client.assert_path_equals('/panel/administration/members/')
        self.members_link         = self.client.find_link("Members")
        self.scientists_link      = self.client.find_link("Scientists")
        self.region_admins_link = self.client.find_link("Region Admins")
        self.organisations_link   = self.client.find_link("Organisations")
        self.region_tags_link     = self.client.find_link("Region Tags")
        self.sponsors_link        = self.client.find_link("Sponsors")
        # todo: should have sponsor_categories link
    
    def add_member(self, data):
        self.members_link.click()
        return PanelAdminMembersPage(self.client).add_member(data)
    
    def goto_scientists_page(self):
        self.scientists_link.click()
        return PanelAdminScientistsPage(self.client)
    
    def goto_region_admins_page(self):
        self.region_admins_link.click()
        return PanelAdminAdministratorsPage(self.client)
    
    def goto_organisations_page(self):
        self.organisations_link.click()
        return PanelAdminOrganisationsPage(self.client)
    
    def goto_region_tags_page(self):
        self.region_tags_link.click()
        return PanelAdminTagsPage(self.client)
    
    def goto_sponsors_page(self):
        self.sponsors_link.click()
        return PanelAdminSponsors(self.client)
    
    def goto_beta_invites_page(self):
        self.client.find_link("Beta invites").beta_invites_link.click()
        return PanelAdminBeta(self.client)


class PanelAdminScientistsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/admin/scientists/')
        self.add_scientist_link = self.client.find_link("Add scientist")
        # TODO: remove buttons
    
    def add_scientist(self, username):
        self.add_scientist_link.click()
        return PanelAdminScientistsAddPage(self.client).add_scientist(username)

    def remove_scientist(self, username):
        # find username in table
        # find related remove link
        # click remove 
        self.client.assertTrue("Are you sure" in self.client.selenium.page_source)
        # click to confirm
        # check for confirmation flash message
        self.client.fail("incomplete")


class PanelAdminScientistsAddPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/admin/scientists/add/')
        self.username = self.client.find_select("username")
        self.submit = self.client.find_submit()
        
    def add_scientist(self, name):
        self.username(name).click()
        self.submit.click()
        return PanelAdminScientistsPage(self.client)


class PanelAdminAdministratorsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/admin/administrators/')
        self.add_link = self.client.find_link("Add regional admin")
        # TODO: remove buttons
    
    def add_regional_admin(self, username):
        self.add_link.click()
        return PanelAdminAdministratorsAddPage(self.client).add_regional_admin(username)


class PanelAdminAdministratorsAddPage():
    
    def __init__(self, client):
        self.client   = client
        self.client.assert_path_equals('/panel/admin/administrators/add/')
        self.username = self.client.find_select("username")
        self.submit   = self.client.find_submit()
        self.cancel   = self.client.find_link("Cancel")

    def add_regional_admin(self, username):
        self.username(username).click()
        self.submit()
        return PanelAdminAdministratorsPage(self.client)


class PanelAdminOrganisationsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/admin/organisations/')
        self.add_link = self.client.find_link("Add organisation")

    def add_organisation(self, data):
        self.add_link.click()
        return PanelAdminOrganisationsAddPage(self.client)
    
    def edit_organisation(self, description, edit_data):
        fail("incomplete")
        # find description text in table
        # find parent row
        # find related edit button
        # click edit
        # do edit workflow

    def delete_organisation(self, description):
        fail("incomplete")
        # find description text in table
        # find parent row
        # find related edit button
        # click edit
        # do delete workflow
    

class PanelAdminOrganisationsAddPage():
    
    def __init__(self, client):
        self.client      = client
        # self.client.assert_path_equals('/panel/admin/organisations/add/')
        self.description = self.client.find_input("description")
        self.blurb       = self.client.find_input("blurb")
        self.url         = self.client.find_input("url")
        self.citation    = self.client.find_input("citation")
        self.logo        = self.client.find_input("image_url")
        # TODO: shouldn't show update_number
        self.submit      = self.client.find_submit()
        self.cancel      = self.client.find_link("Cancel")
    
    def enter_data(self, data):
        if "description" in data:
            self.description.send_keys(data['description'])
        if "blurb" in data:
            self.blurb.send_keys(data['blurb'])
        if "url" in data:
            self.url.send_keys(data['url'])
        if "citation" in data:
            self.citation.send_keys(data['citation'])
        if "logo" in data:
            self.logo.send_keys(data['logo'])
    
    def add_organisation(self, data):
        self.enter_data(data)
        self.submit.click()
        return PanelAdminOrganisationsPage(self.client)


class PanelAdminOrganisationsEditPage(PanelAdminOrganisationsAddPage):
    
    def __init__(self, client):
        super(PanelAdminOrganisationsEditPage, self).__init__(client)
        # self.client.assert_path_equals('/panel/admin/organisations/edit/')
        self.delete_link = self.client.find_link("Delete")

    def edit_organisation(self, data):
        self.enter_data(data)
        self.submit.click()
        # TODO: expect confirmation flash message
        return PanelAdminOrganisationsPage(self.client)

    def delete_organisation(self):
        self.delete_link.click()
        self.client.assertTrue("Are you sure" in self.client.selenium.page_source)
        self.client.find_submit().click()
        # TODO: expect confirmation flash message
        return PanelAdminOrganisationsPage(self.client)


class PanelAdminTagsPage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/admin/tags/')
        self.client.fail("incomplete")
        # TODO: let's pull this from the admin panel


class PanelAdminSponsorsPage():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/admin/sponsors/')
        self.add_link = self.client.find_link("Add sponsor")
        self.categories_link = self.client.find_link("Manage categories")  # TODO: move to own page

    def add_sponsor(self, data):
        self.add_link.click()
        return PanelAdminSponsorsAddPage(self.client).add_sponsor(data)

    def delete_sponsor(self, name):
        # find row in table by name
        # click related edit link
        # do delete workflow
        self.client.fail("incomplete")
    
    def edit_sponsor(self, name, data):
        # find row in table by name
        # click related edit link
        # do edit workflow
        self.client.fail("incomplete")


class PanelAdminSponsorsAddPage():
        
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/panel/admin/sponsors/add/')
        self.name     = self.client.find_input("name")
        self.category = self.client.find_select("category")
        self.logo     = self.client.find_input("image_url")
        self.region   = self.client.find_select("region")
        self.is_major = self.client.find_input("is_major")
        self.submit   = self.client.find_submit()
        self.cancel   = self.client.find_link("Cancel")

    def enter_data(self, data):
        if "name" in data:
            self.name.submit_keys(data['name'])
        if "category" in data:
            self.category(data['category']).click()
        if "logo" in data:
            self.logo.submit_keys(data['logo'])
        if "region" in data:
            self.region(data['region']).click()
        if "is_major" in data:
            self.is_major.click() # TODO: should be enable/disable rather than toggle

    def add_sponsor(self, data):
        self.enter_data(data)
        self.submit.click()
        return PanelAdminSponsorsPage(self.client)


class PanelAdminSponsorsEditPage(PanelAdminSponsorsAddPage):
    
    def __init__(self, client):
        super(PanelAdminSponsorsEditPage, self).__init__(client)
        self.delete_link = self.client.find_link("Delete")

    def edit_sponsor(self, data):
        self.enter_data(data)
        self.submit.click()
        return PanelAdminSponsorsPage(self.client)
    
    def delete_sponsor(self):
        self.delete_link.click()
        self.client.assertTrue("Are you sure" in self.client.selenium.page_source)
        self.client.find_submit().click()
        # TODO: check for flash message confirmation
        return PanelAdminSponsorsPage(self.client)
        

class PanelAdminBetaPage():
    
    def __init__(self, client):
        self.client = client
        # TODO: this page has no invite button


class HomePage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/')
        self.client.assertIn(HOME_PAGE_TITLE, self.client.selenium.title)
    
    def goto_login_page(self):
        self.login_link = self.client.find_link("Sign in")
        self.login_link.click()
        return AccountsLoginPage(self.client)

    def goto_register_page(self):
        self.register_link = self.client.find_link("Create an account")
        self.register_link.click()
        return AccountsRegisterPage(self.client)
        
    def goto_logging_form(self):
        self.register_link = self.client.find_link("Log a sighting")
        self.register_link.click()
        return SightingAddPage(self.client)


class SightingAddPage():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/sightings/add/')
        self.client.assertIn(LOG_SIGHTING_PAGE1_TITLE, self.client.selenium.title)
        self.client.assertTrue("Step 1" in self.client.selenium.page_source)

        self.caption    = self.client.find_input("0-photo_caption")
        self.permission = self.client.find_input("0-photo_permission")
        self.species    = self.client.find_select("0-species")
        self.photo_url  = self.client.find_input("0-photo_url")
        self.submit     = self.client.find_submit()

    def add_sighting(self, sighting):
        
        # Setup 
        mail.outbox = []
        
        # Log sighting
        thanks_page = self.add_sighting_page1(sighting).add_sighting_page2(sighting).add_sighting_page3(sighting)
        
        # Check validation email was sent
        self.client.assertEqual(len(mail.outbox), 1)
        self.client.assertIn("New sighting", mail.outbox[0].subject)
        
        # Return details of the email
        to   = mail.outbox[0].to
        link = re.search(r'/panel/verify/\d+', mail.outbox[0].body).group(0)
        
        return to, link, thanks_page

    def add_sighting_page1(self, sighting):
        
        if 'caption' in sighting:
            self.caption.send_keys(sighting['caption'])
            
        if 'photo_path' in sighting:
            self.photo_url.send_keys(sighting['photo_path'])
            
        if 'permission' in sighting:
            self.permission.click() # TODO: this feels clumsy (effectively toggle, not set)

        self.species(sighting['species']).click()
        
        # submit form
        self.submit.click()
        self.client.assert_no_errors()
        return SightingAddPage2(self.client)
    
    
class SightingAddPage2():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/sightings/add/')
        self.client.assertIn(LOG_SIGHTING_PAGE2_TITLE, self.client.selenium.title)
        self.client.assertTrue("Step 2" in self.client.selenium.page_source)
        
        self.latitude      = self.client.find_input("1-latitude")
        self.longitude     = self.client.find_input("1-longitude")
        self.accuracy      = self.client.find_select("1-accuracy")
        self.time          = self.client.find_select("1-time")
        self.activity      = self.client.find_select("1-activity")
        self.sighting_date = self.client.find_input("1-sighting_date")        
        self.submit        = self.client.find_input("submit")

    def add_sighting_page2(self, sighting):
        
        self.latitude.send_keys(sighting['latitude'])
        self.longitude.send_keys(sighting['longitude'])
        
        if 'accuracy' in sighting:
            self.accuracy(sighting['accuracy']).click()
        
        if 'time' in sighting: 
            # TODO: should throw errors when validation fails
            self.time(sighting['time']).click()
        
        if 'activity' in sighting:
            # TODO: this is hacked from a select to radio boxes in JS!
            self.activity(sighting['activity']).click()

        if 'sighting_date' in sighting: 
            self.sighting_date.send_keys(sighting['sighting_date'])
        
        self.submit.click()
        self.client.assert_no_errors()
        return SightingAddPage3(self.client)


class SightingAddPage3():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/sightings/add/')
        self.client.assertIn(LOG_SIGHTING_PAGE3_TITLE, self.client.selenium.title)
        self.client.assertTrue("Step 3" in self.client.selenium.page_source)
        
        self.count             = self.client.find_input("2-count")
        self.size              = self.client.find_input("2-size")
        self.weight            = self.client.find_input("2-weight")
        self.depth             = self.client.find_input("2-depth")
        self.water_temperature = self.client.find_input("2-water_temperature")
        self.depth             = self.client.find_input("2-depth")
        self.notes             = self.client.find_input("2-notes")
        self.sex               = self.client.find_select("2-sex")
        self.size_method       = self.client.find_select("2-size_method")
        self.weight_method     = self.client.find_select("2-weight_method")
        self.habitat           = self.client.find_select("2-habitat")

        self.submit           = self.client.find_input("submit")

    def add_sighting_page3(self, sighting):

        if 'count' in sighting: 
            self.count.send_keys(sighting['count'])
            
        if 'weight' in sighting: 
            self.count.send_keys(sighting['weight'])
            
        if 'weight_method' in sighting:
            self.weight_method(sighting['weight_method']).click()
        
        if 'size' in sighting: 
            self.count.send_keys(sighting['size'])

        if 'size_method' in sighting:
            self.size_method(sighting['size_method']).click()

        if 'sex' in sighting:
            self.sex(sighting['sex']).click()
        
        if 'depth' in sighting: 
            self.count.send_keys(sighting['depth'])
            
        if 'habitat' in sighting:
            self.habitat(sighting['habitat']).click()
        
        if 'water_temperature' in sighting: 
            self.water_temperature.send_keys(sighting['water_temperature'])
            
        if 'notes' in sighting: 
            self.notes.send_keys(sighting['notes'])

        self.submit.click()
        self.client.assert_no_errors()
        
        return LogSightingComplete(self.client)


class LogSightingComplete():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/sightings/add/')
        self.client.assertIn(LOG_SIGHTING_COMPLETE_PAGE_TITLE, self.client.selenium.title) 
        self.client.assertTrue("Thank you!" in self.client.selenium.page_source)


class AccountsLoginPage():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/accounts/login/')
        self.client.assertIn(LOGIN_PAGE_TITLE, self.client.selenium.title)
        self.username_input = self.client.find_input("username")
        self.password_input = self.client.find_input("password")
            
    def login(self, username, password):
        self.username_input.send_keys(username)
        self.password_input.send_keys(password)
        self.password_input.submit()
        self.client.assert_no_errors()
        self.client.assert_path_equals('/')
        return HomePage(self.client)
    
    def login_expecting_error(self, username, password):
        self.username_input.send_keys(username)
        self.password_input.send_keys(password)
        self.password_input.submit()
        self.client.assert_path_equals('/accounts/login/')
        return AccountsLoginPage(self.client)
        
class AccountsRegisterPage():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/accounts/register/')
        self.client.assertIn(REGISTER_FORM_PAGE_TITLE, self.client.selenium.title)
        
        self.username_input = self.client.find_input("username")
        self.email_input    = self.client.find_input("email")
        self.password1      = self.client.find_input("password1")
        self.password2      = self.client.find_input("password2")
            
    def register(self, username, email, password):
        
        # clear inbox
        mail.outbox = []
        
        # complete form
        self.username_input.send_keys(username)
        self.email_input.send_keys(email)
        self.password1.send_keys(password)
        self.password2.send_keys(password)
        self.password2.submit()
        
        # check email
        self.client.assertEqual(len(mail.outbox), 1)
        self.client.assertEqual(mail.outbox[0].subject, 'Account registration for example.com')
        
        # fetch activation link from email
        activation_link = re.search(r'/accounts/activate/[a-z0-9]+/', mail.outbox[0].body).group(0)
        
        return activation_link, AccountsRegisterCompletePage(self.client)

    def register_and_expect_error(self, username, email, password):
        
        # complete form
        self.username_input.send_keys(username)
        self.email_input.send_keys(email)
        self.password1.send_keys(password)
        self.password2.send_keys(password)
        self.password2.submit()
        
        # confirm we haven't succeeded
        return AccountsRegisterPage(self.client)
        
    def register_and_activate(self, username, email, password):
        activation_link, complete = self.register(username, email, password)
        self.client.go(activation_link)
        # TODO: this workflow is ugly - can we log them in and show them their profile page 
        return AccountsActivateCompletePage(self.client)
        
    def registerExpectingError(self, username, email, password):
        try:
            self.register(username, password)
            return AccountsRegisterPage(self.client)
        except:
            pass

class AccountsActivateCompletePage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/accounts/activate/complete/')
        self.client.assertIn(REGISTER_ACTIVATED_PAGE_TITLE, self.client.selenium.title)
        

class AccountsRegisterCompletePage():
    
    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/accounts/register/complete/')
        self.client.assertIn(REGISTER_COMPLETE_PAGE_TITLE, self.client.selenium.title)
        

class MyRedmapPage():

    def __init__(self, client):
        self.client = client
        self.client.assert_path_equals('/my-redmap/')
        self.client.assertIn(PROFILE_PAGE_TITLE, self.client.selenium.title)
        self.settings_link        = self.client.find_link("Settings")
        self.change_password_link = self.client.find_link("Change Password")  # TODO: goes to admin theme
        self.log_sighting_link    = self.client.find_link("Log a Sighting")
        self.my_groups_link       = self.client.find_link("My Groups")  # TODO: not working

    def edit_profile(self, data):
        self.client.fail("TODO: incomplete")

# Parent class for our tests based on a live server and selenium client
class SeleniumLiveServerTestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNIT)
        super(SeleniumLiveServerTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(SeleniumLiveServerTestCase, cls).tearDownClass()
        cls.selenium.quit()

    def go(self, path):
        "fetch a relative url"
        self.selenium.get('%s%s' % (self.live_server_url, path))

    def goto_panel(self):
        self.go('/panel/')
        return PanelPage(self)

    def goto_home(self):
        self.go('/')
        return HomePage(self)
    
    def new_visitor(self):
        self.selenium.delete_all_cookies()
        return self.goto_home()
    
    def login_as(self, username, password):
        return self.new_visitor().goto_login_page().login(username, password)
    
    def add_sighting(self, sighting):
        return self.goto_home().goto_logging_form().add_sighting(sighting)
    
    # additional selenium helpers
    # TODO: inconsistent place to add these but it's practical
    def find_link(self, text):
        return self.selenium.find_element_by_link_text(text)
    
    def find_option(self, element, text):
        try:
            return element.find_element_by_xpath("option[contains(text(),'%s')]" % (text))
        except:
            text_options = [o.text for o in element.find_elements_by_tag_name("option")]
            self.fail("Failed to match for '%s' in options: %s" % (text, text_options))
        
    def find_id(self, id):
        return self.selenium.find_element_by_id(id)
    
    def find_element_by_partial_text(self, elements, text):
        """Pick the option which contains text from a select box"""
        for element in elements:
            if text in element.text:
                return element
        self.fail("Element containing partial text '%s' not found in: %s" % (text, [e.text for e in elements]))
    
    def find_input(self, name):
        return self.selenium.find_element_by_name(name)
    
    def find_select(self, id_or_name, by="name"):
        """ return's a function for clicking on select options"""
        if by=="name":
            select = self.find_input(id_or_name)
        elif by=="id":
            select = self.find_id(id_or_name)
        return lambda (x): self.find_option(select, x)
    
    def find_submit(self):
        return self.selenium.find_element_by_xpath("//*[@type='submit']")        
        
    def find_select_options_by_name(self, name):
        return self.selenium.find_element_by_name(name).find_elements_by_tag_name("option")

    def find_radio_inputs(self, name):
        "Raw radio inputs.  Not very useful without labels."
        return self.selenium.find_elements_by_name(name)
        
    def find_radio_input_labels(self, name):
        "return labels for matching radio buttons.  click to pick radio."
        return self.selenium.find_elements_by_xpath("//*[@name='%s']/.." % name)
    
    def find_radio(self, name):
        labels = self.find_radio_input_labels(name)
        return lambda (text): self.find_element_by_partial_text(labels, text)
    
    def find_checkbox(self, name):
        return self.selenium.find_element_by_name(name)
    
    def assert_no_errors(self):
        errors = self.selenium.find_elements_by_css_selector(".error")
        for error in errors:
            try:
                label = error.find_element_by_tag_name("label").text
                help = error.find_element_by_css_selector(".help-inline").text
                print "%s: %s" % (label, help)
            except:
                pass
                
        if errors:
            self.fail("Page has %d errors" % (len(errors)))
    
    def assert_path_equals(self, path):
        self.assertEqual(urlparse(self.selenium.current_url).path, path)

class TestLandingPages(SeleniumLiveServerTestCase):
    
    def test_homepage(self):
        self.goto_home()


class TestRegistrationWorkflows(SeleniumLiveServerTestCase):
    
    def setUp(self):
        load_redmapdb_data()
        load_cms_data()

    def test_registration_form_validation(self):
        
        # should throw validation errors
        self.new_visitor().goto_register_page().register_and_expect_error("", "", "")
        
        # should throw password error
        self.new_visitor().goto_register_page().register_and_expect_error("user1", "user1@example.com", "")
        
        # should throw email validation error
        self.new_visitor().goto_register_page().register_and_expect_error("user1", "user1.com", "1234")

    def test_registration(self):
        
        # should work.  we have our first user.
        self.new_visitor().goto_register_page().register_and_activate("user1", "user1@example.com", "u1")
        
    def test_register_duplicate_usernames(self):

        # should work.  we have our first user.
        self.new_visitor().goto_register_page().register_and_activate("user1", "user1@example.com", "u1")

        # should fail, can't use duplicate usernames
        self.new_visitor().goto_register_page().register_and_expect_error("user1", "user2@example.com", "u1")

    def test_register_duplicate_usernames_before_activation(self):

        # should work.  we have our first user.
        self.new_visitor().goto_register_page().register("user1", "user1@example.com", "u1")

        # should fail, can't use duplicate usernames
        self.new_visitor().goto_register_page().register_and_expect_error("user1", "user2@example.com", "u1")

    @unittest.skip("TODO: Are duplicate emails legal?")
    def test_register_duplicate_emails(self):
        
        # should work.  we have our first user.
        self.goto_home().goto_register_page().register_and_activate("user1", "user1@example.com", "u1")
        
        # TODO: should fail, can't use duplicate emails
        self.goto_home().goto_register_page().register_and_expect_error("user2", "user1@example.com", "u1")


# Make sure logging in works
class TestAuthWorkflows(SeleniumLiveServerTestCase):
    
    def setUp(self):
        load_redmapdb_data()
        load_test_users()

    def test_login(self):
        self.login_as("user1", "u1")
        
    def test_login_form_validation(self):
        self.new_visitor().goto_login_page().login_expecting_error("", "")
        self.new_visitor().goto_login_page().login_expecting_error("baduser", "badpass")
        self.new_visitor().goto_login_page().login_expecting_error("user1", "badpass")

    
# Helpers for log sightings tests
swansea = dict(latitude="-42.1278", longitude="148.0761", accuracy='Within 1 kilometre')
diving = dict(activity='Diving')
last_week = dict(sighting_date='2012-09-15')
morning = dict(time='09:00 am')
afternoon = dict(time='02:00 pm')
gloomy_octopus = dict(species='Gloomy Octopus', count='1')
octopus_tetricus = dict(species='Octopus tetricus ( Gloomy Octopus )', count='1')

# TODO: I expect Django has a way to find a fixture's absolute path - good or binary files?
app_path = path.abspath(path.dirname(__file__))
fix_path = path.join(app_path, "fixtures")
photo_path = path.join(fix_path, "test-logging-photo.jpg")
photo = dict(photo_path=photo_path, caption="Look at the shiny scales!", permission=True)
 
def make_data(*ds, **data):
    for d in ds:
        data.update(d)
    return data
    
# Make sure we can log sightings successfully
class TestLoggingWorkflows(SeleniumLiveServerTestCase):

    """ 
    These tests make the logging, routing and validating workflows are working.
    
    The test fixture includes users, sighting meta data and the species database but 
    does not have any expert panel assignments setup.
    
    Users include:
        admin / a1             (assigned as admin)
        user1 / u1             (just regular user)
        scientist1 / s1        (assigned as scientist)
        scientist2 / s2        (just regular user)
        regionaladmin1 / ra1   (assigned as admin)
        regionaladmin2 / ra2   (just regular user)
    
    """

    def setUp(self):
        load_redmapdb_data()
        load_test_users()

    def test_can_promote_user_to_scientist(self):

        # check scientist2 doens't currently have access
        self.login_as("scientist2", "s2")
        self.go("/panel/")
        self.assertTrue("you don't have permission to access this page" in self.selenium.page_source)
        
        # promote scientist2 to be a scientist
        self.login_as("admin1", "a1")
        self.goto_panel().goto_administration_page().goto_scientists_page().add_scientist("scientist2")
        
        # check scientist2 gets access
        self.login_as("scientist2", "s2")
        self.goto_panel()

    #
    def test_can_add_species_expert1(self):

        # setup test data and environment
        assignment_data = make_data(gloomy_octopus, region="All", person="scientist1", rank=1, contact_in_range=True)
        sighting_data   = make_data(gloomy_octopus, swansea, diving, last_week, morning)

        # give scientist1 an assignment
        self.login_as("admin1", "a1")
        self.goto_panel().goto_expert_panel_page().add_species_expert(assignment_data)
        
        # submit a sighting
        self.login_as("user1", "u1")
        to, link, thanks_page = self.add_sighting(sighting_data)
        
        # check it's recieved by scientist
        self.assertIn("scientist1@example.com", to)
    
    def test_can_add_species_expert(self):

        # setup test data and environment
        assignment_data = make_data(
            gloomy_octopus, region="All", person="scientist1", rank=1,
            contact_in_range=True)

        sighting_data = make_data(
            gloomy_octopus, swansea, diving, last_week, morning, photo)

        # give scientist1 an assignment
        self.login_as("admin1", "a1")
        self.goto_panel().goto_expert_panel_page().add_species_expert(assignment_data)

        # submit a sighting
        self.login_as("user1", "u1")
        to, link, thanks_page = self.add_sighting(sighting_data)
        
        # check it's recieved by scientist
        self.assertIn("scientist1@example.com", to)

    def test_can_promote_user_to_administrator(self):
        pass
        
    def test_can_assign_scientist_to_expert_panel(self):
        pass

    def test_can_not_assign_user_to_expert_panel(self):
        pass
        
    def test_can_not_assign_regionaladmin_to_expert_panel(self):
        pass
    
    def test_logging_requires_authentication(self):
        try:
            self.new_visitor().goto_logging_form()
            self.fail("Should not have been able to see logging form as unauthenticated user")
        except:
            AccountsLoginPage(self)
    
    def test_expert_assignment_full_match(self):
        
        # setup test data and environment
        mail.outbox = []
        assignment_data = make_data(gloomy_octopus, region="All", person="scientist1", rank=1, in_ranage=True)
        sighting_data   = make_data(gloomy_octopus, swansea, diving, last_week, morning)
        
        # login as admin
        self.login_as("admin1", "a1")
        
        # setup scientist as expert of gloomy octopus
        self.goto_panel().goto_expert_panel_page().add_species_expert(assignment_data)
        
        # login as user and log sighting gloomy_octopus sighting
        self.login_as("admin1", "a1").goto_logging_form().add_sighting(sighting_data)
        
        # check email goes to scientist
        email = mail.outbox[0]
        self.assertIn("scientist1@example.com", email.to)
    
    def test_logging_basic_sighting(self):
        
        # clear email outbox
        mail.outbox = []

        # prepare sighting data
        sighting = make_data(gloomy_octopus, swansea, diving, last_week, afternoon)

        # login and log sighting
        self.login_as("user1", "u1")
        to_list, link, thanks = self.add_sighting(sighting)
        
        # check sighting was stored in db
        self.assertEqual(len(Sighting.objects.all()), 1)
        
        # check admin as assigned sighting (as no scientists match)
        self.assertIn("admin@example.com", to_list)
        
    def test_logging_basic_sighting_with_photo(self):
        self.login_as("user1", "u1")
        sighting_data = make_data(gloomy_octopus, swansea, diving, last_week, afternoon, photo)
        self.add_sighting(sighting_data)
        self.assertEqual(len(Sighting.objects.all()), 1)

