import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
load_dotenv()

# =====================
# CONFIGURACIÓN DE LOGS
# =====================
import sys
import os
from datetime import datetime

if not os.path.exists("logs"):
    os.makedirs("logs")

nombre_archivo = os.path.basename(__file__).replace(".py", "")
fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"logs/{nombre_archivo}_{fecha_hora}.log"

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(log_filename)
sys.stderr = sys.stdout
# =====================


from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.relative_locator import locate_with

# =====================
# CONFIGURACIÓN GOOGLE SHEETS
# =====================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    os.getenv("GOOGLE_CREDENTIALS_PATH", "automatizacion-karrot-456d1a1552ca.json"),
    scope
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
    driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    print("✅ Navegador iniciado correctamente")
except Exception as e:
    print(f"❌ Error al iniciar el navegador: {str(e)}")
    exit()

wait = WebDriverWait(driver, 40)
id_caso = "TC019"
#nombre_caja = input("Ingrese el nombre de la caja a crear: ")

try:
    # =====================
    # LOGIN
    # =====================
    print("🔐 Iniciando proceso de login...")
    
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    time.sleep(10)
    
    # =====================
    # NAVEGACIÓN A UBICACIONES
    # =====================
    print("📍 Navegando al módulo de Ubicaciones...")
    ModuloUbicaciones = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]"
    )))
    ModuloUbicaciones.click()
    print("✅ Click en módulo Ubicaciones")
    time.sleep(2)

    # Redirección directa a la URL de lista de ubicaciones
    driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/list-locations")
    print("✅ Dirigido directamente a Ubicaciones por URL")
    time.sleep(5)

    # Hacer clic en el botón de tres puntos de la primera sede
    listado_opciones = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[3]/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[8]/div/button[2]"))
    )
    listado_opciones.click()
    print("✅ Botón de opciones clickeado")
    
    print(f"🔍 Encontradas {len(opciones)} opciones:")
    for i, opcion in enumerate(opciones):
        print(f"  {i+1}. {opcion.text}")
    
    # Buscar y hacer clic en la opción que contiene exactamente "borrar"
    opcion_encontrada = None
    for opcion in opciones:
        if "Borrar" in opcion.text:
            opcion_encontrada = opcion
            break
    time.sleep(10)

    if opcion_encontrada:
        max_intentos = 5
        for intento in range(max_intentos):
            # Vuelve a abrir el menú de opciones en cada intento
            listado_opciones = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[3]/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[8]/div/button[2]"))
            )
            listado_opciones.click()
            time.sleep(1)  # Espera breve para que el menú se despliegue

            # Vuelve a buscar las opciones del menú
            opciones = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div/div/div/div/div/table/tbody/tr[1]/td[6]/button"))
            )
            opcion_encontrada = None
            for opcion in opciones:
                if "Borrar" in opcion.text:
                    opcion_encontrada = opcion
                    break

            if opcion_encontrada:
                ActionChains(driver).move_to_element(opcion_encontrada).click().perform()
                print(f"Intento {intento+1}: click en 'Borrar'")
                try:
                    WebDriverWait(driver, 2).until(
                        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Delete Location?')]"))
                    )
                    print("✅ Apareció 'Delete Location?' en pantalla")
                    break
                except TimeoutException as e:
                        print(f"❌ Error: {str(e)}")
                        observaciones = f"Error: {str(e)}"
                        estado = "FALLIDO"
                        registrar_resultado(id_caso, estado, observaciones)
        boton_yes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Yes']]"))
        )
        boton_yes.click()
        print("✅ Botón 'Yes' clickeado")
        observaciones = "Sede eliminada exitosamente"
        estado = "EXITOSO"

    else:
        print("❌ No se encontró la opción 'Borrar'")
        observaciones = "No se encontró la opción 'Borrar'"
        estado = "FALLIDO"

    registrar_resultado(id_caso, estado, observaciones)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    observaciones = f"Error: {str(e)}"
    estado = "FALLIDO"