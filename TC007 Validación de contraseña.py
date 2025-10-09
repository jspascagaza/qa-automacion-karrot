import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

        # Actualiza en columnas M, N y O
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"✅ Caso {id_caso} actualizado -> {estado}")
    except Exception as e:
        print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")


# =====================
# PRUEBA REGISTRO (validación contraseña)
# =====================
id_caso = "TC007"   # <- ajusta el caso de prueba en el sheet
observaciones = ""

# --- Pedir datos por consola ---
company_name = input("👉 Ingresa el nombre de tu negocio o tienda: ")
first_name = input("👉 Ingresa tu nombre: ")
last_name = input("👉 Ingresa tu apellido: ")
email = input("👉 Ingresa tu correo electrónico: ")
phone_number = input("👉 Ingresa tu número de celular: ")
password = input("👉 Ingresa tu contraseña: ")  # Aquí probamos con una contraseña inválida

# Inicializar navegador
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/register/es")

wait = WebDriverWait(driver, 15)

try:
    # Nombre de empresa
    wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
    print("✅ Nombre de empresa ingresado")

    # Nombre persona
    wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
    print("✅ Nombre ingresado")

    # Apellido persona
    wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
    print("✅ Apellido ingresado")

    # --- Seleccionar país: Colombia ---
    print("🔄 Intentando seleccionar país...")
    pais_seleccionado = False
    try:
        country_selector = wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
        country_selector.click()
        print("✅ Click en el selector de país")
        time.sleep(2)

        try:
            colombia_option = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
            colombia_option.click()
            print("✅ Colombia seleccionado desde dropdown (método 1)")
            pais_seleccionado = True
        except:
            colombia_option = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
            colombia_option.click()
            print("✅ Colombia seleccionado desde dropdown (método 2)")
            pais_seleccionado = True
    except Exception as e:
        print(f"⚠️ Método dropdown falló: {e}")
        observaciones += f"Método dropdown falló: {str(e)}. "

        try:
            country_input = driver.find_element(By.ID, "register-form_mainCountry")
            country_input.clear()
            country_input.send_keys("Colombia")
            time.sleep(1)
            country_input.send_keys(Keys.ENTER)
            print("✅ Colombia ingresado manualmente")
            pais_seleccionado = True
        except Exception as e2:
            print(f"⚠️ Método escritura falló: {e2}")
            observaciones += f"Método escritura falló: {str(e2)}. "

            try:
                driver.execute_script("""
                    var element = document.getElementById('register-form_mainCountry');
                    element.value = 'Colombia';
                    var event = new Event('change', { bubbles: true });
                    element.dispatchEvent(event);
                """)
                print("✅ Valor establecido con JavaScript")
                pais_seleccionado = True
            except Exception as e3:
                print(f"⚠️ Método JavaScript falló: {e3}")
                observaciones += f"Método JavaScript falló: {str(e3)}. "
                raise Exception("❌ No se pudo seleccionar el país")

    if not pais_seleccionado:
        raise Exception("❌ No se pudo seleccionar el país")

    # Correo electrónico
    wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
    print("✅ Correo electrónico ingresado")

    # Número de celular
    wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
    print("✅ Número de celular ingresado")

    # Contraseña
    password_input = wait.until(EC.presence_of_element_located((By.ID, "register-form_password")))
    password_input.send_keys(password)
    print("✅ Contraseña ingresada")

    # Click fuera para disparar validación
    driver.find_element(By.TAG_NAME, "body").click()

    # Esperar mensaje de error de contraseña
    error_msg_elem = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'ant-form-item-explain-error') and contains(text(),'La contraseña debe tener al menos 8 caracteres')]")
        )
    )
    error_msg = error_msg_elem.text.strip()
    print(f"⚠️ Mensaje mostrado en pantalla: '{error_msg}'")

    if "La contraseña debe tener al menos 8 caracteres" in error_msg:
        print("✅ Caso exitoso: validación de contraseña detectada")
        registrar_resultado(id_caso, "Exitosa", "Mensaje de validación de contraseña mostrado")
    else:
        print("❌ Caso fallido: mensaje no coincide")
        registrar_resultado(id_caso, "Fallida", f"Mensaje encontrado: {error_msg}")

except Exception as e:
    print(f"❌ Caso fallido: {e}")
    registrar_resultado(id_caso, "Fallida", f"No apareció el mensaje esperado: {str(e)}")

finally:
    time.sleep(10)
    driver.quit()
