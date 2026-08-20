import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")

wait = WebDriverWait(driver, 20)

try:
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    
    time.sleep(10)
    
    submenu_proveedores = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[normalize-space()='Proveedores'] | //a[normalize-space()='Proveedores']")
    ))
    submenu_proveedores.click()
    time.sleep(1)
    
    opcion_lista_proveedores = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[normalize-space()='Lista de proveedores'] | //a[normalize-space()='Lista de proveedores']")
    ))
    opcion_lista_proveedores.click()
    time.sleep(5)
    
    celdas = driver.find_elements(By.XPATH, "(//table/tbody/tr[contains(@class, 'ant-table-row')])[1]/td")
    for i, c in enumerate(celdas):
        print(f"td[{i+1}]: {c.text.strip()}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
