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
id_caso = "TC024"

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

# =====================
# INICIO DE AUTOMATIZACIÓN
# =====================

try:
    driver = webdriver.Chrome()
    driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    wait = WebDriverWait(driver, 40)

    # Login
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys("js.pascagaza@karrotup.com")

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
    time.sleep(10)

    productos_servicios = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Productos y Servicios']"))
    )
    productos_servicios.click()
    print("✅ Click en Productos y Servicios")
    time.sleep(10)

    # Agregar Artículo
    boton_agregar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agregar Artículo')]"))
    )
    boton_agregar.click()
    print("✅ Click en Agregar Artículo")
    time.sleep(10)

    # Verificar que el texto "Añadir nuevo producto" esté presente
    elemento = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h2[@class='mb-3' and text()='Añadir nuevo producto']"))
    )
    print("Texto encontrado:", elemento.text)
    time.sleep(2)
except Exception as e:
    print(f"❌ Error al encontrar el elemento: {e}")


boton_anadir = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'ant-btn-primary') and contains(text(), 'Añadir')]")
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
boton_anadir.click()
print("✅ Click en Añadir")

def buscar_texto_con_espera(driver, texto, timeout=10):
    """
    Busca texto esperando a que aparezca
    """
    try:
        wait = WebDriverWait(driver, timeout)
        elemento = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{texto}')]")))
        print(f"✅ Texto encontrado: {elemento.text}")
        time.sleep(5)
        return elemento 
    except TimeoutException:
        print(f"❌ Texto no apareció después de {timeout}s: {texto}")
        observaciones = f"No se encontró el texto: {texto}"
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        observaciones = f"Error: {e}"
        return None

# Uso
textos_a_buscar = [
    "Introduce el nombre del producto",
    "Introduce la categoría del producto",
    "Por favor seleccione un grupo de unidades", 
    "Introduce la descripción del producto",
    "Introduce un precio de producto válido"
]

for texto in textos_a_buscar:
    elemento = buscar_texto_con_espera(driver, texto, 10)
    if elemento:
        exito = True
    else:
        exito = False
        

if exito==True:
    observaciones = f"Se encontró el texto los campos obligatorios"
    estado = "ÉXITOSO"
    registrar_resultado(id_caso, estado, observaciones)
else:
    observaciones = f"No se encontró el texto"
    estado = "FALLIDO"
    registrar_resultado(id_caso, estado, observaciones)