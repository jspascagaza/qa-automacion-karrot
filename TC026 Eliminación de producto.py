import csv
import datetime
from socket import timeout
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import string
from faker import Faker
import faker_commerce; print(faker_commerce.__file__)
import random
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
    os.getenv("GOOGLE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0")
)
sheet = spreadsheet.sheet1

# Variable para controlar el éxito de la ejecución
exito = False
observaciones = ""
url_final = ""

# =====================
# PRUEBA REGISTRO COMPLETO CON CONSULTOR Y VERIFICACIÓN
# =====================
id_caso = "TC025"

def registrar_resultado(id_caso, estado, observaciones=""):
    """
    Busca un ID Caso y actualiza las columnas M, N y O:
      M = Fecha Ejecución
      N = Estado Ejecución
      O = Observaciones
    """
    try:
        celda = sheet.find(id_caso)
        if not celda:
            print(f"⚠️ No se encontró el ID {id_caso}")
            return
        fila = celda.row
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        automatizado = "Sí"
        sheet.update_cell(fila, 11, automatizado)   # Columna K
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"✅ Caso {id_caso} actualizado -> {estado}")
    except Exception as e:
        print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")

try:
        driver = webdriver.Chrome()
        driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
        driver.maximize_window()
        wait = WebDriverWait(driver, 40)

        # Login
        email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
        email_input.click()
        email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

        password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
        password_input.click()
        password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
        login_button.click()
        time.sleep(15)

        # Menú Catálogo
        catalogo = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Catálogo']"))
        )
        catalogo.click()
        print("✅ Click en Catálogo")
        time.sleep(10)

        productos_servicios = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Productos y Servicios']"))
        )
        productos_servicios.click()
        print("✅ Click en Productos y Servicios")
        time.sleep(10)
except Exception as e:
        print(f"❌ Error inesperado {str(e)}")


listar_opciones_producto = wait.until(
EC.element_to_be_clickable((By.XPATH, "(//table/tbody/tr[contains(@class, 'ant-table-row')])[1]//button[last()]"))
)
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listar_opciones_producto)
listar_opciones_producto.click()
print("✅ Click en los 3 puntos")
time.sleep(5)

borrar_producto = wait.until(
EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Borrar']"))
)
borrar_producto.click()
print("✅ Click en Borrar producto")
time.sleep(5)

mensaje_confirmacion = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Estás seguro que deseas eliminar este producto?')]"))
    )
print("✅ Mensaje de confirmación encontrado")

def encontrar_boton_eliminar():
    selectors = [
        "//button[contains(@class, 'ant-btn-primary') and contains(text(), 'Eliminar')]",
        "//button[contains(text(), 'Eliminar')]",
        "//span[contains(text(), 'Eliminar')]/ancestor::button",
        "//div[contains(@class, 'ant-modal')]//button[contains(text(), 'Eliminar')]"
    ]
    
    for selector in selectors:
        try:
            elemento = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            print(f"✅ Botón Eliminar encontrado con: {selector}")
            return elemento
        except Exception as e:
            print(f"❌ Selector falló: {selector}")
            continue
    
    print("❌ No se pudo encontrar el botón Eliminar")
    return None

# Uso
boton_eliminar = encontrar_boton_eliminar()
if boton_eliminar:
    boton_eliminar.click()
time.sleep(10)


#pendiente por terminar hasta poder encontrar una solucion donde se pueda verificar que el producto seleccionado fue eliminado.
