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
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
wait = WebDriverWait(driver, 20)

email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button"))).click()
time.sleep(5)

wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Proveedores']"))).click()
time.sleep(2)
wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Lista de proveedores'] | //a[normalize-space()='Lista de proveedores']"))).click()
time.sleep(5)

fila_proveedor = wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[contains(@class, 'ant-table-row')][1]")))
btn_mas_info = fila_proveedor.find_element(By.XPATH, ".//button[contains(., 'Más información')] | .//span[contains(., 'Más información')]")
driver.execute_script("arguments[0].click();", btn_mas_info)
time.sleep(5)

print("HTML of all titles:")
titles = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-card-head-title')]")
for t in titles:
    print(t.text)

print("\nHTML of thead:")
theads = driver.find_elements(By.TAG_NAME, "thead")
for t in theads:
    print(t.text)

driver.quit()
