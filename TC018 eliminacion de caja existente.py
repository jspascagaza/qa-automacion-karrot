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
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode("ascii", "replace").decode("ascii"))
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
id_caso = "TC018"

try:
    exito = False
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
    print("📍 Iniciando navegación al módulo de Ubicaciones...")
    
    try:
        # Paso 1: Desplegar menú lateral pasando el cursor sobre el aside/nav
        print("📂 Desplegando menú lateral...")
        aside_menu = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//aside[contains(@class, 'side-nav') or contains(@class, 'ant-layout-sider')] | //nav | //*[@id='root']//aside"
        )))
        ActionChains(driver).move_to_element(aside_menu).perform()
        time.sleep(1)

        # Si el sidebar tiene icono de tienda (shop), posicionarse sobre él
        try:
            icono_shop = driver.find_element(By.XPATH, "//*[@data-icon='shop' or contains(@class, 'anticon-shop')]")
            ActionChains(driver).move_to_element(icono_shop).perform()
            time.sleep(1)
        except Exception:
            pass

        # Paso 2: Desplegar el módulo Ubicaciones si no está abierto
        print("🏬 Buscando módulo Ubicaciones en el menú...")
        modulo_ubicaciones = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//li[contains(@class, 'ant-menu-submenu') and .//span[text()='Ubicaciones']] | //div[contains(@class, 'ant-menu-submenu-title') and contains(., 'Ubicaciones')]"
        )))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", modulo_ubicaciones)
        time.sleep(0.5)

        clases_modulo = modulo_ubicaciones.get_attribute("class") or ""
        aria_exp = modulo_ubicaciones.get_attribute("aria-expanded") or ""
        if "ant-menu-submenu-open" not in clases_modulo and aria_exp != "true":
            try:
                modulo_ubicaciones.click()
            except Exception:
                driver.execute_script("arguments[0].click();", modulo_ubicaciones)
            print("✅ Módulo Ubicaciones desplegado")
            time.sleep(1)
        else:
            print("ℹ️ Módulo Ubicaciones ya se encuentra desplegado")

        # Paso 3: Clic en la opción 'Ubicaciones' dentro del submenú
        print("📍 Clickeando opción 'Ubicaciones'...")
        opcion_ubicaciones = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//a[contains(@href, '/locations/list-locations')] | //ul[contains(@class, 'ant-menu-sub')]//span[normalize-space()='Ubicaciones'] | //ul[contains(@class, 'ant-menu-sub')]//a[contains(., 'Ubicaciones')]"
        )))
        driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", opcion_ubicaciones)
        time.sleep(0.5)
        try:
            opcion_ubicaciones.click()
        except Exception:
            driver.execute_script("arguments[0].click();", opcion_ubicaciones)
        print("✅ Click en opción Ubicaciones realizado")
        time.sleep(4)
    except Exception as e_nav:
        print(f"⚠️ Menú lateral no interactuable, navegando directamente por URL: {str(e_nav)}")
        driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/list-locations")
        time.sleep(5)

    # Asegurar que estemos en list-locations
    if "list-locations" not in driver.current_url:
        driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/list-locations")
        time.sleep(5)
    print("✅ Página de lista de ubicaciones cargada")

    # =====================
    # SELECCIONAR SEDE Y VER CAJAS
    # =====================
    print("📋 Buscando botón de acciones en la tabla de ubicaciones...")
    time.sleep(3)
    listado_editar = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//tbody/tr[contains(@class, 'ant-table-row')][1]//button[contains(@class, 'ant-dropdown-trigger')] | //tbody/tr[contains(@class, 'ant-table-row')][1]//td[last()]//button[2] | //*[@id='root']//table//tbody/tr[2]/td[8]/div/button[2] | //tbody/tr[1]//button[last()]"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listado_editar)
    time.sleep(1)
    try:
        listado_editar.click()
    except Exception:
        driver.execute_script("arguments[0].click();", listado_editar)
    print("✅ Click en acciones de la sede")
    time.sleep(2)

    # Click en 'Ver Cajas'
    print("📦 Seleccionando opción 'Ver Cajas'...")
    editar_caja = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ver Cajas'] | //*[contains(text(), 'Ver Cajas')] | //li[contains(., 'Ver Cajas')]"))
    )
    try:
        editar_caja.click()
    except Exception:
        driver.execute_script("arguments[0].click();", editar_caja)
    print("✅ Click en 'Ver Cajas'")
    time.sleep(5)

    # =====================
    # ELIMINAR CAJA EXISTENTE
    # =====================
    print("🔘 Buscando botón de opciones de la caja en la tabla...")
    listado_opciones = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//tbody/tr[contains(@class, 'ant-table-row')][1]//button[contains(@class, 'ant-dropdown-trigger') or contains(@class, 'ant-btn')] | //table//tbody/tr[1]//td[last()]//button | //table//tbody/tr[1]//button[last()] | //*[@id='root']/div/section/section/section/div/main/div[2]/div/div/div/div/div[3]/div/div/div/div/div/table/tbody/tr[1]/td[6]/button"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listado_opciones)
    time.sleep(1)
    try:
        listado_opciones.click()
    except Exception:
        driver.execute_script("arguments[0].click();", listado_opciones)
    print("✅ Botón de opciones clickeado")

    # Esperar y buscar las opciones del menú dropdown
    time.sleep(2)
    opciones = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-dropdown-menu .ant-dropdown-menu-item"))
    )

    print(f"🔍 Encontradas {len(opciones)} opciones:")
    for i, opcion in enumerate(opciones):
        print(f"  {i+1}. {opcion.text.strip()}")
    
    # Buscar la opción que contiene "Eliminar caja" o "Eliminar"
    opcion_encontrada = None
    for opcion in opciones:
        if "Eliminar caja" in opcion.text or "Eliminar" in opcion.text:
            opcion_encontrada = opcion
            break

    if opcion_encontrada:
        try:
            ActionChains(driver).move_to_element(opcion_encontrada).click().perform()
        except Exception:
            driver.execute_script("arguments[0].click();", opcion_encontrada)
        print("✅ 'Eliminar caja' seleccionado")
        time.sleep(1)

        # Manejar modal o popconfirm de confirmación si aparece
        try:
            boton_confirmar = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(@class, 'ant-modal')]//button[contains(@class, 'ant-btn-primary') or contains(., 'Sí') or contains(., 'Aceptar') or contains(., 'Eliminar') or contains(., 'Yes')] | //div[contains(@class, 'ant-popover')]//button[contains(@class, 'ant-btn-primary') or contains(., 'Sí') or contains(., 'Yes') or contains(., 'Aceptar')]"
                ))
            )
            boton_confirmar.click()
            print("✅ Confirmación de eliminación aceptada")
            time.sleep(2)
        except TimeoutException:
            print("ℹ️ No se requirió confirmación adicional o se eliminó directamente")

        time.sleep(3)
        exito = True
        observaciones = "Caja eliminada exitosamente"
        print("✅ Caja eliminada exitosamente")
    else:
        exito = False
        observaciones = "No se encontró la opción 'Eliminar caja' en el menú"
        print(f"❌ {observaciones}")

except TimeoutException as e:
    exito = False
    observaciones = f"Timeout esperando elemento: {str(e)}"
    print(f"❌ {observaciones}")

except Exception as e:
    exito = False
    observaciones = f"Error en la ejecución: {str(e)}"
    print(f"❌ {observaciones}")

finally:
    # =====================
    # REGISTRAR RESULTADO EN GOOGLE SHEETS Y CERRAR
    # =====================
    estado = "EXITOSO" if exito else "FALLIDO"
    print(f"\n📊 Registrando resultado en Google Sheets: {id_caso} -> {estado}")
    try:
        if registrar_resultado(id_caso, estado, observaciones):
            print(f"✅ Caso {id_caso} registrado exitosamente en Google Sheets como {estado}")
        else:
            print(f"❌ Falló el registro del caso {id_caso} en Google Sheets")
    except Exception as e_sheet:
        print(f"❌ Error al conectar con Google Sheets: {str(e_sheet)}")

    try:
        print(f"🌐 URL final: {driver.current_url}")
        print(f"📄 Título de la página: {driver.title}")
    except Exception:
        pass

    time.sleep(3)
    driver.quit()
    print("✅ Navegador cerrado")
