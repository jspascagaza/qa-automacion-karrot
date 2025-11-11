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
except Exception as e:
        print(f"❌ Error inesperado {str(e)}")


listar_opciones_producto = wait.until(
EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div[3]/div/div/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/table/tbody/tr[11]/td[6]/div/button"))
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