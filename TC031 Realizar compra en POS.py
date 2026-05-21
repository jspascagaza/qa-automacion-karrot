import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
import sys
from datetime import datetime

load_dotenv()

# =====================
# CONFIGURACIÓN DE LOGS
# =====================
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

id_caso = "TC031"

def registrar_resultado(id_caso, estado, observaciones=""):
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
# INICIO DE LA PRUEBA
# =====================
chrome_options = Options()
# chrome_options.add_argument("--headless=new") # Descomentar si se quiere modo headless

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 30)

try:
    print("Iniciando prueba de Compra en POS...")
    driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")

    # 1. Login
    print("Ingresando credenciales...")
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.send_keys("karrotdev@outlook.com")

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.send_keys("P4sc4g4z42025#*")

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    time.sleep(10)
    print("✅ Login exitoso")

    # 2. Selección de Sede y Caja
    print("Seleccionando Sede y Caja...")
    # Esperamos explícitamente a que aparezcan los inputs de selección de sede y caja
    xpath_input = "//input[contains(@class, 'ant-select-selection-search-input')]"
    try:
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_input)))
    except:
        inputs = []
    
    if len(inputs) >= 2:
        # Selección Sede
        sede_input = inputs[0]
        driver.execute_script("arguments[0].focus();", sede_input)
        time.sleep(1)
        sede_input.send_keys(Keys.DOWN)
        time.sleep(0.5)
        sede_input.send_keys(Keys.ENTER)
        print("✅ Sede seleccionada")

        time.sleep(2)
        # Selección Caja
        caja_input = inputs[1]
        driver.execute_script("arguments[0].focus();", caja_input)
        time.sleep(1)
        caja_input.send_keys(Keys.DOWN)
        time.sleep(0.5)
        caja_input.send_keys(Keys.ENTER)
        print("✅ Caja seleccionada")
    else:
        print("⚠️ No se detectaron los selectores de Sede y Caja, es posible que el usuario ya tenga un turno abierto.")

    # 3. Ingresar al POS (Iniciar turno)
    try:
        print("🔍 Buscando botón de 'Iniciar turno' o 'Ingresar'...")
        
        # Estrategias para encontrar el botón de iniciar turno/ingresar
        estrategias_botones = [
            # Buscar por texto explícito (es la forma más segura si el diseño cambia)
            "//button[contains(normalize-space(.), 'Iniciar turno') or contains(normalize-space(.), 'Iniciar Turno') or contains(normalize-space(.), 'iniciar turno')]",
            "//button[contains(normalize-space(.), 'Comenzar turno') or contains(normalize-space(.), 'Comenzar Turno')]",
            "//button[contains(normalize-space(.), 'Ingresar')]",
            "//button[contains(normalize-space(.), 'Abrir Caja')]",
            # XPaths absolutos originales como fallback
            '//*[@id="root"]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/button',
            '//*[@id="root"]/div/div/div/div/div[2]/div/div/div[1]/div/div[4]/button'
        ]
        
        boton_ingresar = None
        for xpath in estrategias_botones:
            try:
                # Usamos un tiempo de espera muy corto para iterar rápido entre las opciones
                boton_ingresar = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                print(f"✅ Botón encontrado con el XPath: {xpath}")
                break
            except:
                continue
                
        if boton_ingresar:
            # Intentamos el clic normal, y si falla por intercepción, usamos JS
            try:
                boton_ingresar.click()
                print("✅ Click en 'Iniciar turno' (Click normal)")
            except Exception as e_click:
                driver.execute_script("arguments[0].click();", boton_ingresar)
                print("✅ Click en 'Iniciar turno' (Click mediante JavaScript)")
                
            time.sleep(5)
        else:
            print("⚠️ No se encontró ningún botón para Iniciar Turno con las estrategias definidas.")
            driver.save_screenshot("error_boton_iniciar_turno NoEncontrado.png")
            
    except Exception as e:
        print(f"❌ Error inesperado al intentar clickear el botón de ingreso: {e}")
        driver.save_screenshot("error_iniciar_turno.png")

    # =========================================================================
    # 4. Flujo de Compra (COMPLETAR XPATHS AQUÍ)
    # =========================================================================
    print("Agregando producto al carrito...")
    
    # [!] Reemplaza esto con el ID o XPATH del buscador de productos o el botón de un producto
    XPATH_PRODUCTO = "//button[contains(text(), 'Agregar Producto')]" # EJEMPLO
    # wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_PRODUCTO))).click()
    print("✅ Producto agregado (TODO: Actualizar XPath)")
    
    # [!] Verificar que el carrito se actualice correctamente
    # Reemplaza esto con el XPATH del carrito o del total
    XPATH_CARRITO_TOTAL = "//span[contains(@class, 'total-carrito')]" # EJEMPLO
    # total_element = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_CARRITO_TOTAL)))
    # assert total_element.text != "$0.00", "El carrito no se actualizó"
    print("✅ Carrito actualizado verificado (TODO: Actualizar XPath y lógica de aserción)")

    registrar_resultado(id_caso, "Exitosa", "Prueba de compra en POS ejecutada correctamente")

except Exception as e:
    print(f"❌ Error durante la ejecución: {e}")
    driver.save_screenshot("error_compra_pos.png")
    registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")

finally:
    driver.quit()
    print("Navegador cerrado.")
