import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.relative_locator import locate_with

# =====================
# INICIO DRIVER
# =====================
try:
    driver = webdriver.Chrome()
    driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)  # 🔹 Definir aquí el WebDriverWait
    print("✅ Navegador iniciado correctamente")
except Exception as e:
    print(f"❌ Error al iniciar el navegador: {str(e)}")
    exit()

# =====================
# LOGIN
# =====================
print("🔐 Iniciando proceso de login...")

# Esperar campo de correo
email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
email_input.click()
email_input.send_keys("js.pascagaza@karrotup.com")
print("✅ Correo electrónico ingresado")

# Esperar campo de contraseña
password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
password_input.click()
password_input.send_keys("P4sc4g4z42025#*")
print("✅ Contraseña ingresada")

# Click en el botón "Iniciar sesión"
login_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button"))
)
login_button.click()
print("✅ Botón de login clickeado")
time.sleep(10)

# =====================
# IR AL PANEL DE ADMINISTRACIÓN
# =====================
panel_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]")
    )
)
panel_button.click()
print("✅ Click en 'Ir al panel de administración'")

# Esperar a que cargue el Panel de control
wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]")))
print("✅ Panel de control cargado correctamente")
time.sleep(5)

# =====================
# NAVEGACIÓN A UBICACIONES
# =====================
print("📍 Navegando al módulo de Ubicaciones...")

ModuloUbicaciones = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//*[@id='root']/div/section/section/aside/div/ul/li[1]/ul/li[12]/div")
    )
)
ModuloUbicaciones.click()
print("✅ Click en Ubicaciones")
time.sleep(5)

# Obtener y seguir el enlace de ubicaciones
segundopath = ModuloUbicaciones.find_element(
    By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a"
)
print(segundopath.text)
print(segundopath.get_attribute("href"))
driver.get(segundopath.get_attribute("href"))
print("✅ Dirigiendo a Ubicaciones")
time.sleep(10)

# =====================
# VALIDACIÓN TABLA UBICACIONES
# =====================
# Esperar que la tabla cargue
celdas = wait.until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "tbody.ant-table-tbody tr td:nth-child(1)")
    )
)

# Revisar si alguna está vacía
hay_vacias = any(celda.text.strip() == "" for celda in celdas)

# 🔹 Validación
if hay_vacias:
    observaciones = "❌ Fallido: La creación de la sede dejó celdas vacías en la columna 'Nombre de ubicación'"
    estado = "FALLIDO"
else:
    observaciones = "✅ Éxito: Todas las filas tienen 'Nombre de ubicación' válido"
    estado = "ÉXITOSO"

print(observaciones)
