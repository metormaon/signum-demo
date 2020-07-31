import os
import subprocess
import time
import unittest
import docker as docker
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# noinspection PyUnresolvedReferences
import chromedriver_binary


class TestLogin(unittest.TestCase):
    container = None
    process = None
    
    @classmethod
    def setUpClass(cls):
        if os.name != 'nt':
            client = docker.from_env()
            for previous_container in client.containers.list(filters={"ancestor": "signum-demo"}):
                previous_container.kill()

            cls.container = client.containers.run("signum-demo", detach=True, ports={"5000": "5000"})
        else:
            cls.subprocess = subprocess.Popen("python ../app.py", shell=True)

    @classmethod
    def tearDownClass(cls):
        if cls.container:
            cls.container.kill()
            
        if cls.process:
            cls.process.kill()

    def setUp(self) -> None:
        self.browser = webdriver.Chrome()
        self.browser.get("http://127.0.0.1:5000/")
        timeout = 3  # seconds
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.ID, 'username')))
        except TimeoutException:
            self.fail("Timeout")

    def tearDown(self) -> None:
        self.browser.close()

    def test_failure(self):
        username = self.browser.find_element_by_id("username")
        username.clear()
        username.send_keys("unregistered_user")

        password = self.browser.find_element_by_id("password")
        password.clear()
        password.send_keys("123456")

        captcha = self.browser.find_element_by_id("captcha")
        captcha.clear()
        captcha.send_keys("something")

        url = self.browser.current_url

        submit = self.browser.find_element_by_id("submit")
        submit.click()

        time.sleep(10)

        assert self.browser.current_url == url
        assert self.browser.find_element_by_id("errorMessage").is_displayed()


