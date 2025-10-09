import time
from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/documentation/webdriver/elements/file_upload/")

title_h1 = driver.find_element(By.CSS_SELECTOR, "body > div > div.td-main > div > main > div > h1")
time.sleep(3)
print(title_h1.text)