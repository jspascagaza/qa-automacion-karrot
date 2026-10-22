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

        # Actualiza en columnas M, N y O
        sheet.update_cell(fila, 11, automatizado)   # Columna K
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"✅ Caso {id_caso} actualizado -> {estado}")
    except Exception as e:
        print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")


# =====================
# PRUEBA LOGIN FALLIDO
# =====================
id_caso = "TC002"   # <- ajusta el caso de prueba que estés validando

email_user = os.getenv("KARROT_LOGIN_EMAIL")
password_user = "12345678"

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")

wait = WebDriverWait(driver, 20)

try:
    # Campo correo
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys(email_user)

    # Campo contraseña
    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys(password_user)

    # Botón iniciar sesión
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()

    # =====================
    # Verificar mensaje de error
    # =====================
    try:
        # Esperar a que la alerta sea VISIBLE en pantalla (no solo presente en el DOM)
        alert_element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'ant-alert')]"))
        )

        # Obtener el texto real (usando textContent como respaldo si .text está vacío por animaciones)
        error_message = (alert_element.text or alert_element.get_attribute("textContent") or "").strip()

        # Breve pausa por si la animación de Ant Design aún está rellenando el texto
        if not error_message:
            time.sleep(1)
            error_message = (alert_element.text or alert_element.get_attribute("textContent") or "").strip()

        print(f"Mensaje encontrado en pantalla: '{error_message}'")

        # Mensajes válidos de login fallido
        mensajes_esperados = ["Incorrect username or password.", "User does not exist"]

        if any(msg in error_message for msg in mensajes_esperados):
            print("✅ Caso exitoso: mensaje correcto detectado")
            registrar_resultado(id_caso, "Exitosa", f"Mensaje de error mostrado: {error_message}")
        else:
            print("❌ Caso fallido: mensaje no coincide")
            registrar_resultado(id_caso, "Fallida", f"Mensaje encontrado: {error_message}")

    except Exception:
        print("❌ Caso fallido: no apareció el mensaje de error en el tiempo esperado")
        registrar_resultado(id_caso, "Fallida", "No apareció la alerta de error de login")

except Exception as e:
    print(f"❌ Error inesperado: {e}")
    registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")

finally:
    time.sleep(15)  # Mantener abierto unos segundos antes de cerrar
    driver.quit()
