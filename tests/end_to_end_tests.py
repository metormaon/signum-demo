import json
import os
import subprocess
import time
import unittest

import docker as docker
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, expected_conditions

# noinspection PyUnresolvedReferences
import chromedriver_binary


class TestLogin(unittest.TestCase):
    container = None
    process = None

    # @classmethod
    # def setUpClass(cls):
    #     if os.name != 'nt':
    #         client = docker.from_env()
    #
    #         for previous_container in client.containers.list(filters={
    #                                                 "ancestor": "docker.pkg.github.com/metormaon/signum-demo/demo:noam-enhancements",
    #                                                 "status": "running"}):
    #             previous_container.kill()
    #
    #         cls.container = client.containers.run("docker.pkg.github.com/metormaon/signum-demo/demo:noam-enhancements",
    #                                               detach=True,
    #                                               ports={"5000": "5000"}, environment=["SIGNUM_TEST_MODE=True"])
    #     else:
    #         cls.subprocess = subprocess.Popen("python ../app.py", shell=True, env={"SIGNUM_TEST_MODE": "True"})
    #
    # @classmethod
    # def tearDownClass(cls):
    #     if cls.container:
    #         cls.container.kill()
    #
    #     if cls.process:
    #         cls.process.kill()

    def setUp(self) -> None:
        self.browser = webdriver.Chrome()
        self.browser.get("http://127.0.0.1:5000/signup")
        timeout = 3  # seconds
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.ID, 'username')))
        except TimeoutException:
            self.fail("Timeout")

    def tearDown(self) -> None:
        self.browser.close()

    def test_sign_up_then_login(self):
        username = self.browser.find_element_by_id("username")
        username.clear()
        username.send_keys("test_user")

        password = self.browser.find_element_by_id("password")
        password.clear()
        password.send_keys("123456abcEE$")

        password = self.browser.find_element_by_id("confirm_password")
        password.clear()
        password.send_keys("123456abcEE$")

        captcha_options_text = self.browser.find_element_by_id("state").get_attribute("value")

        captcha_options = json.loads(captcha_options_text.replace("\'", "\""))

        captcha_solution = captcha_options[0]

        captcha = self.browser.find_element_by_id("captcha")
        captcha.clear()
        captcha.send_keys(captcha_solution)

        submit = self.browser.find_element_by_id("submit")
        submit.click()

        WebDriverWait(self.browser, 30).until(
            expected_conditions.url_contains("http://127.0.0.1:5000/post-signup")
        )

        self.browser.get("http://127.0.0.1:5000/")

        username = self.browser.find_element_by_id("username")
        username.clear()
        username.send_keys("test_user")

        password = self.browser.find_element_by_id("password")
        password.clear()
        password.send_keys("123456abcEE$")

        captcha_options_text = self.browser.find_element_by_id("state").get_attribute("value")

        captcha_options = json.loads(captcha_options_text.replace("\'", "\""))

        captcha_solution = captcha_options[0]

        captcha = self.browser.find_element_by_id("captcha")
        captcha.clear()
        captcha.send_keys(captcha_solution)

        submit = self.browser.find_element_by_id("submit")
        submit.click()

        WebDriverWait(self.browser, 30).until(
            expected_conditions.url_contains("http://127.0.0.1:5000/post-login")
        )
