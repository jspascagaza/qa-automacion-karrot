import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.relative_locator import locate_with


#Tipo_de_Actividad = input("Ingrese el tipo de actividad:")

# =====================
# CONFIGURACIÓN GOOGLE SHEETS
# =====================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "automatizacion-karrot-1105a7349e3e.json", scope
)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"
)
sheet = spreadsheet.sheet1

# Variables de control
observaciones = ""
url_final = ""
estado = "PENDIENTE"

# =====================
# FUNCIÓN PARA REGISTRAR RESULTADOS
# =====================
def registrar_resultado(id_caso, estado, observaciones=""):
    try:
        celda = sheet.find(id_caso)
        if not celda:
            print(f"⚠️ No se encontró el ID {id_caso}")
            return False
        fila = celda.row
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        automatizado = "Sí"
        sheet.update_cell(fila, 11, automatizado)   # Columna K
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"✅ Caso {id_caso} actualizado -> {estado}")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")
        return False

# =====================
# CONFIGURACIÓN DEL DRIVER
# =====================
try:
    driver = webdriver.Chrome()
    driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    print("✅ Navegador iniciado correctamente")
except Exception as e:
    print(f"❌ Error al iniciar el navegador: {str(e)}")
    exit()

wait = WebDriverWait(driver, 40)
id_caso = "TC020"
#nombre_caja = input("Ingrese el nombre de la caja a crear: ")

try:
    # =====================
    # LOGIN
    # =====================
    print("🔐 Iniciando proceso de login...")
    
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys("js.pascagaza@karrotup.com")

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys("P4sc4g4z42025#*")

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    time.sleep(10)

    panel_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
    )
    panel_button.click()

    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]")))
    time.sleep(5)

    # =====================
    # NAVEGACIÓN A UBICACIONES
    # =====================
    ModuloUbicaciones = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/aside/div/ul/li[1]/ul/li[12]/div"))
    )
    ModuloUbicaciones.click()
    time.sleep(5)

    segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
    driver.get(segundopath.get_attribute("href"))
    time.sleep(5)

    # =====================
    driver.find_element(By.CSS_SELECTOR, "button.ant-btn.ant-btn-secondary.ant-btn-sm").click()
    time.sleep(5)
    
    fecha_inicio = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Start date"]')
    driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].removeAttribute('disabled');", fecha_inicio)
    fecha_inicio.send_keys(Keys.ESCAPE)  # Cierra el calendario si está abierto
    fecha_inicio.clear()
    try:
        fecha_inicio.send_keys("2025-09-01")
        fecha_inicio.send_keys(Keys.ENTER)
    except Exception:
        # Si falla, usa JS para poner el valor
        driver.execute_script("arguments[0].value = arguments[1];", fecha_inicio, "2025-09-01")
        fecha_inicio.send_keys(Keys.ENTER)
    time.sleep(10)

    # Fecha de fin
    fecha_fin = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="End date"]')
    driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].removeAttribute('disabled');", fecha_fin)
    fecha_fin.send_keys(Keys.ESCAPE)
    fecha_fin.clear()
    try:
        fecha_fin.send_keys("2025-09-30")
        fecha_fin.send_keys(Keys.ENTER)
    except Exception:
        driver.execute_script("arguments[0].value = arguments[1];", fecha_fin, "2025-09-30")
        fecha_fin.send_keys(Keys.ENTER)
    time.sleep(10)
    boton_buscar = driver.find_element(By.XPATH, "//button[@type='button' and contains(@class, 'ant-btn-default')]//span[text()='Buscar']/..")
    boton_buscar.click()
    time.sleep(10)
    observaciones = "Prueba  completada exitosamente permite filtrar por fecha de inicio y fin"
    estado = "EXITOSO"
    registrar_resultado(id_caso, estado, observaciones)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    observaciones = f"Error: {str(e)}"
    estado = "FALLIDO"
    registrar_resultado(id_caso, estado, observaciones)