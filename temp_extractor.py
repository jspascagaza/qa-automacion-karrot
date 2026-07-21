from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.maximize_window()
try:
    driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    wait = WebDriverWait(driver, 20)
    
    # Login
    wait.until(EC.presence_of_element_located((By.ID, "login-form_email"))).send_keys("karrotdev@outlook.com")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button"))).click()
    
    # Wait for Sede/Caja selection page to load
    time.sleep(10)
    
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    driver.quit()
