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

# Navegar a Proveedores primero para emular la ruta exacta de TC055
wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Proveedores'] | //a[normalize-space()='Proveedores']"))).click()
time.sleep(2)

wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ordenes de Compra'] | //a[normalize-space()='Ordenes de Compra']"))).click()
time.sleep(5)

boton_xpath = '//*[@id="root"]/div/section/section/section/div/main/div[5]/div/div[1]/div[2]/div/button[1]'
wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath))).click()
time.sleep(5)

# Save HTML
html = driver.page_source
with open("pagina_ordenes.html", "w", encoding="utf-8") as f:
    f.write(html)

driver.quit()
