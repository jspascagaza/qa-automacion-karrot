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
from faker import Faker
import random
# =====================
# DATOS DE ENTRADA
# =====================
nombre = f"{random.choice(['Tienda', 'Supermercado', 'Mini Market', 'Boutique', 'Almacén', 'Punto'])} {random.choice(['La Esquina', 'El Sol', 'Central', 'Del Norte', 'Express', 'Del Pueblo', '24 Horas', 'Económico'])}"
direccion = Faker.address().replace("\n", ", ")
usuario = Faker.email()
ciudad = Faker.city()

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
id_caso = "TC016"

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
    time.sleep(10)

    url_agregar = "https://dev.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
    driver.get(url_agregar)
    time.sleep(5)

    # =====================
    # LLENAR FORMULARIO
    # =====================
    nombre_input = wait.until(EC.presence_of_element_located((By.ID, "advanced_search_name")))
    nombre_input.clear()
    nombre_input.send_keys(nombre)

    tipo_tienda = driver.find_element(By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
    tipo_tienda.click()
    time.sleep(2)
    opciones = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")))
    for opcion in opciones:
        if opcion.text.strip() == "Tienda":
            opcion.click()
            break

    # Selección de ciudad con validación
    ciudad_input = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[@id='advanced_search']/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[3]/div/div[2]/div/div/div/div"
    )))
    ciudad_input.click()
    time.sleep(2)

    opciones = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")))
    ciudad_encontrada = False
    for opcion in opciones:
        if opcion.text.strip() == ciudad:
            opcion.click()
            ciudad_encontrada = True
            break

    if not ciudad_encontrada:
        estado = "FALLIDO"
        observaciones = f"La ciudad '{ciudad}' no está en las opciones disponibles"
        raise Exception(observaciones)

    direccion_input = wait.until(EC.presence_of_element_located((By.ID, "advanced_search_address")))
    direccion_input.clear()
    direccion_input.send_keys(direccion)
    ActionChains(driver).move_by_offset(0, 0).click().perform()
    time.sleep(2)

    # =====================
    # CLICK EN AÑADIR (SIN USUARIO)
    # =====================
    boton_anadir = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[@type='submit' and contains(text(), 'Añadir')]"
    )))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
    time.sleep(2)
    boton_anadir.click()
    print("✅ Botón 'Añadir' clickeado")

    # =====================
    # VALIDACIÓN DEL MENSAJE DE ERROR
    # =====================
    try:
        error_msg = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Ups, algo salió mal al crear la ubicación')]")))
        if error_msg:
            estado = "EXITOSO"
            observaciones = "El sistema no permitió crear la ubicación sin usuario"
            print("✅ Caso exitoso: apareció mensaje de error esperado")
    except TimeoutException:
        estado = "FALLIDO"
        observaciones = "El sistema permitió crear la ubicación sin usuario"
        print("❌ Caso fallido: no apareció el mensaje de error")

except Exception as e:
    if estado == "PENDIENTE":
        estado = "FALLIDO"
    observaciones = str(e)
    print(f"❌ Error: {observaciones}")

finally:
    if registrar_resultado(id_caso, estado, observaciones):
        print("✅ Resultado registrado en Google Sheets")
    else:
        print("❌ No se pudo registrar el resultado en Google Sheets")
    
    print(f"\n🌐 URL final: {driver.current_url}")
    print(f"📄 Título de la página: {driver.title}")
    
    time.sleep(3)
    driver.quit()
    print("✅ Navegador cerrado")

# =====================
# RESUMEN FINAL
# =====================
print("\n" + "="*80)
print("RESUMEN DE EJECUCIÓN - REGISTRO SEDE SIN USUARIO")
print("="*80)
print(f"📋 ID Caso: {id_caso}")
print(f"✅ Estado: {estado}")
print(f"🔗 URL Final: {url_final}")
print(f"📝 Observaciones: {observaciones}")
print("="*80)
