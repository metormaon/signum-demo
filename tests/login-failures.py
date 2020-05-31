from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import app

app.main()

driver = webdriver.Chrome("chromedriver.exe")
driver.get("http://127.0.0.1:5000/")
#assert "Python" in driver.title
elem = driver.find_element_by_name("username")
elem.clear()
elem.send_keys("yossi")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()

