import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

email_user = "js.pasca@karrotup.com"
password_user = "ContraseñaIncorrecta123#*"

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")

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
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Iniciar sesión')]")))
    login_button.click()

    # =====================
    # Verificar mensaje de error
    # =====================
    try:
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "ant-alert-message"),
                "User does not exist"
            )
        )

        # Obtener el texto real
        error_message = driver.find_element(By.CLASS_NAME, "ant-alert-message").text.strip()
        print(f"Mensaje encontrado en pantalla: '{error_message}'")

        if "User does not exist" in error_message:
            print("✅ Caso exitoso: mensaje correcto detectado")
            registrar_resultado(id_caso, "Exitosa", "Mensaje de error mostrado")
        else:
            print("❌ Caso fallido: mensaje no coincide")
            registrar_resultado(id_caso, "Fallida", f"Mensaje encontrado: {error_message}")

    except Exception:
        print("❌ Caso fallido: no apareció el mensaje en 5 segundos")
        registrar_resultado(id_caso, "Fallida", "No apareció el mensaje 'User does not exist.'")

except Exception as e:
    print(f"❌ Error inesperado: {e}")
    registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")

finally:
    time.sleep(15)  # Mantener abierto unos segundos antes de cerrar
    driver.quit()
