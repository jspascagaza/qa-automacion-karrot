import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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
    "automatizacion-karrot-1105a7349e3e.json", scope
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
    driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    print("✅ Navegador iniciado correctamente")
except Exception as e:
    print(f"❌ Error al iniciar el navegador: {str(e)}")
    exit()

wait = WebDriverWait(driver, 40)
id_caso = "TC018"
#nombre_caja = input("Ingrese el nombre de la caja a crear: ")

try:
    # =====================
    # LOGIN
    # =====================
    print("🔐 Iniciando proceso de login...")
    
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys("js.pascagaza@karrotup.com")

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys("P4sc4g4z42025#*")

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Iniciar sesión')]")))
    login_button.click()
    time.sleep(10)

    panel_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
    )
    panel_button.click()

    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]")))
    time.sleep(5)

    # =====================
    # NAVEGACIÓN A UBICACIONES
    # =====================
    ModuloUbicaciones = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/aside/div/ul/li[1]/ul/li[12]/div"))
    )
    ModuloUbicaciones.click()
    time.sleep(5)

    segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
    driver.get(segundopath.get_attribute("href"))
    time.sleep(5)

    listado_editar = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/table/tbody/tr[2]/td[7]/div/button[2]")))
    listado_editar.click()
    URL_caja = "https://dev.do5o1l1ov8f4a.amplifyapp.com/app/locations/list-cashdrawers/abda433b-d026-4726-ab7d-3b4eddb765c3"
    driver.get(URL_caja)
    
    # Hacer clic en el botón de tres puntos
    listado_opciones = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-dropdown-trigger"))
    )
    listado_opciones.click()
    print("✅ Botón de opciones clickeado")

    # Esperar y buscar las opciones del menú dropdown
    time.sleep(2)
    opciones = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-dropdown-menu .ant-dropdown-menu-item"))
    )

    print(f"🔍 Encontradas {len(opciones)} opciones:")
    for i, opcion in enumerate(opciones):
        print(f"  {i+1}. {opcion.text}")
    
    # Buscar y hacer clic en la opción que contiene exactamente "Eliminar caja"
    opcion_encontrada = None
    for opcion in opciones:
        if "Eliminar caja" in opcion.text:
            opcion_encontrada = opcion
            break

    if opcion_encontrada:
        # Usar ActionChains por si el click normal no funciona
        ActionChains(driver).move_to_element(opcion_encontrada).click().perform()
        print("✅ 'Eliminar caja' seleccionado")
        observaciones = "Caja eliminada exitosamente"
        estado = "EXITOSO"
    else:
        print("❌ No se encontró la opción 'Eliminar caja'")
        observaciones = "No se encontró la opción 'Eliminar caja'"
        estado = "FALLIDO"
    registrar_resultado(id_caso, estado, observaciones)
except Exception as e:
    print(f"❌ Error: {str(e)}")