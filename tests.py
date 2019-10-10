from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os

driver = os.getcwd() + "/chromedriver"
print(driver)
driver = webdriver.Chrome(driver)
home = driver.get("https://minimalstore.herokuapp.com")
assert "Home" in home
login = driver.get('https://minimalstore.herokuapp.com/login')
assert 'Login' in login
driver.close()
