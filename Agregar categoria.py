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


# listado categorias
categorias_posibles = ["Electrónicos", "Hogar", "Oficina", "Personal", "General", "Variados"]

try:
        driver = webdriver.Chrome()
        driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
        driver.maximize_window()
        wait = WebDriverWait(driver, 40)

        # Login
        email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
        email_input.click()
        email_input.send_keys("js.pascagaza@karrotup.com")
        #email_input.send_keys("karrotdev@outlook.com")

        password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
        password_input.click()
        password_input.send_keys("P4sc4g4z42025#*")

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Iniciar sesión')]")))
        login_button.click()
        time.sleep(15)

        # Ir al panel de administración
        panel_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
        )
        panel_button.click()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]"))
        )
        print("✅ Panel de control cargado correctamente")
        time.sleep(5)

        # Menú Catálogo
        catalogo = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Catálogo']"))
        )
        catalogo.click()
        print("✅ Click en Catálogo")

        categorias_servicios = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Categorías y Unidades']"))
        )
        categorias_servicios.click()
        print("✅ Click en Categorías y Unidades")

        boton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Agregar Categoría Raíz')]"))
        )
        boton.click()
        print("✅ Botón 'Agregar Categoría Raíz' clickeado")

        categoria_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.ant-input")))
        categorias= [
        "Consolas", "Computadores", "Celulares", "Accesorios",
        "Otros"]
        nombre_categoria = random.choice(categorias)
        categoria_input.send_keys(nombre_categoria)
        time.sleep(5)

        panel_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-btn-primary"))
        )
        panel_button.click()
        time.sleep(5)
except Exception as e:
        print(f"❌ Error inesperado {str(e)}")