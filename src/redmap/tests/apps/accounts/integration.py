'''
Created on 05/09/2012

@author: thomas
'''

"""

selenium is evil

from django.test import LiveServerTestCase


from selenium.webdriver.firefox.webdriver import WebDriver

class UserAccountTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(UserAccountTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(UserAccountTests, cls).tearDownClass()
        cls.selenium.quit()

    def test_user_can_register(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/accounts/register/"))

        self.selenium.find_element_by_id("id_username").send_keys("new_user")
        self.selenium.find_element_by_id("id_email").send_keys("new_user@ionata.com.au")
        self.selenium.find_element_by_id("id_password").send_keys("password")
        self.selenium.find_element_by_id("id_password2").send_keys("password")

        self.selenium.find_element_by_xpath('//input[@value="Send activation email"]').click()

    def test_login(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/login/"))
        username_input = self.selenium.find_element_by_name("username")

        username_input.send_keys("myuser")

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("secret")

        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
"""