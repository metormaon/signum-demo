import unittest
import docker as docker
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# noinspection PyUnresolvedReferences
import chromedriver_binary


class MyTest(unittest.TestCase):
    container = None

    @classmethod
    def setUpClass(cls):
        client = docker.from_env()
        cls.container = client.containers.run("signum-demo", detach=True, ports={"5000": "5000"})

    @classmethod
    def tearDownClass(cls):
        cls.container.kill()

    def setUp(self) -> None:
        self.browser = webdriver.Chrome()

    def tearDown(self) -> None:
        self.browser.close()
        self.browser.get("http://0.0.0.0:5000/")
        delay = 3  # seconds
        try:
            WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.ID, 'username')))
            print("Page is ready!")
        except TimeoutException:
            self.fail("Timeout")

    def test_x(self):
        # elem = self.browser.find_element_by_id("username")
        # elem.clear()
        # elem.send_keys("yossi")
        # elem.send_keys(Keys.RETURN)
        # assert "No results found." not in self.browser.page_source
        pass

