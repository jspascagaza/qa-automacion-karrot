import time
import sys
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

chrome_options = Options()
if os.getenv("JENKINS_URL") or os.getenv("CI") or os.getenv("HEADLESS") == "true":
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
driver.maximize_window()
wait = WebDriverWait(driver, 40)

# Login
print("Iniciando sesión...")
email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
email_input.click()
email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
password_input.click()
password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))

login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
login_button.click()
print("Login exitoso")
time.sleep(10)

try:
    menu_proveedores = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Proveedores']")))
    menu_proveedores.click()
    time.sleep(2)
    
    submenu_lista_proveedores = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Lista de proveedores'] | //a[normalize-space()='Lista de proveedores']")))
    submenu_lista_proveedores.click()
    time.sleep(5)
    
    fila_proveedor = wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[contains(@class, 'ant-table-row')][1] | //table//tbody/tr[2]")))
    btn_mas_info = fila_proveedor.find_element(By.XPATH, ".//button[contains(., 'Más información')] | .//span[contains(., 'Más información')] | .//a[contains(., 'Más información')] | .//*[contains(text(), 'Más información')]")
    driver.execute_script("arguments[0].click();", btn_mas_info)
    time.sleep(5)
    
    print("En pantalla de proveedor. Volcando HTML de las tablas...")
    tablas = driver.find_elements(By.TAG_NAME, "table")
    for i, t in enumerate(tablas):
        print(f"--- TABLA {i} ---")
        filas = t.find_elements(By.TAG_NAME, "tr")
        for j, f in enumerate(filas[:5]):
            celdas = f.find_elements(By.TAG_NAME, "td")
            if not celdas: celdas = f.find_elements(By.TAG_NAME, "th")
            textos = [c.text.replace('\\n', ' ') for c in celdas]
            print(f"Fila {j}: {textos}")
            if j == 1 and len(celdas) > 0:
                print(f"HTML celda 0: {celdas[0].get_attribute('outerHTML')}")
                
except Exception as e:
    print(e)
finally:
    driver.quit()
