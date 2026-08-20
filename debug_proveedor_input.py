import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
wait = WebDriverWait(driver, 20)

email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button"))).click()
time.sleep(5)

wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ordenes de Compra'] | //a[normalize-space()='Ordenes de Compra']"))).click()
time.sleep(5)

boton_xpath = '//*[@id="root"]/div/section/section/section/div/main/div[5]/div/div[1]/div[2]/div/button[1]'
wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath))).click()
time.sleep(3)

print("HTML de ant-form-item con Proveedor:")
try:
    items = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-form-item')]")
    for item in items:
        if "Proveedor" in item.text:
            print("FOUND ITEM:")
            print(item.get_attribute('outerHTML'))
            break
except Exception as e:
    print(e)

print("\nHTML de todos los inputs role=combobox:")
try:
    inputs = driver.find_elements(By.XPATH, "//input[@role='combobox']")
    for idx, inp in enumerate(inputs):
        print(f"Combobox {idx}:", inp.get_attribute('outerHTML'))
except Exception as e:
    print(e)

driver.quit()
