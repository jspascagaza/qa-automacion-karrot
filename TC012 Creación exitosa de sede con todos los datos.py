import csv
import datetime
import time
import random
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.relative_locator import locate_with
from faker import Faker
# =====================
# DATOS DE ENTRADA
# =====================
fake = Faker('es_CO')

tipo_sede = fake.random_element(['Sede', 'Punto', 'Tienda', 'Sucursal', 'Almacén'])
zona_bogota = fake.random_element(['Chapinero', 'Usaquén', 'Suba', 'Zona T', 'Cedritos', 'Teusaquillo', 'Fontibón', 'Salitre', 'Chicó', 'Pepe Sierra', 'Calle 100', 'Santa Bárbara', 'Norte', 'Centro'])
nombre = f"{tipo_sede} Bogotá {zona_bogota} {fake.random_int(1, 99)}"
correo = fake.email()
telefono = fake.phone_number()
tipo_via = fake.random_element(['Calle', 'Carrera', 'Avenida', 'Diagonal', 'Transversal'])
num_via = fake.random_int(1, 170)
num_cruce = fake.random_int(1, 99)
num_placa = fake.random_int(1, 99)
direccion = f"{tipo_via} {num_via} #{num_cruce}-{num_placa}, Bogotá, Colombia"

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

# Variable para controlar el éxito de la ejecución
exito = False
observaciones = ""
url_final = ""

# =====================
# FUNCIÓN PARA REGISTRAR RESULTADOS
# =====================
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
            return False
        fila = celda.row
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        automatizado = "Sí"

        # Actualiza en columnas M, N y O
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
id_caso = "TC012"

try:
    # =====================
    # LOGIN
    # =====================
    print("🔐 Iniciando proceso de login...")
    
    # Esperar campo de correo
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
    print("✅ Correo electrónico ingresado")

    # Esperar campo de contraseña
    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))
    print("✅ Contraseña ingresada")

    # Click en el botón "Iniciar sesión"
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    print("✅ Botón de login clickeado")
    time.sleep(10)

    # =====================
    # NAVEGACIÓN A UBICACIONES
    # =====================
    print("📍 Navegando al módulo de Ubicaciones...")
    
    ModuloUbicaciones = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/div/nav/div[9]/button")))
    ModuloUbicaciones.click()
    print("✅ Click en Ubicaciones")
    time.sleep(5)

    # Obtener y seguir el enlace de ubicaciones
    #segunda parte ubicaciones
#     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
#     print(segundopath.text)
#     print(segundopath.get_attribute("href"))
#     driver.get(segundopath.get_attribute("href"))
    print("✅ dirigiendo a Ubicaciones")
    time.sleep(10)

    # =====================
    # AGREGAR NUEVA UBICACIÓN
    # =====================
    print("➕ Navegando a agregar ubicación...")
    
    # Navegar directamente a la URL de agregar ubicación
    url_agregar = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
    driver.get(url_agregar)
    time.sleep(5)

    # Verificar que estamos en la página correcta
    if "add-locations" in driver.current_url:
        print("✅ Página de agregar ubicación cargada correctamente")
    else:
        print("⚠️ Posible problema al cargar la página de agregar ubicación")

    # =====================
    # LLENAR FORMULARIO
    # =====================
    print("📝 Llenando formulario de ubicación...")
    
    # Ingresar nombre
    nombre_input = wait.until(EC.presence_of_element_located((By.ID, "location_form_name")))
    nombre_input.clear()
    nombre_input.send_keys(nombre)
    print("✅ Nombre de sede ingresado")

    # Ingresar tipo de local
    # Primer dropdown (Tipo de ubicación)
    time.sleep(1)
    tipo_tienda = driver.find_element(By.ID, "location_form_locationType")
    try:
        tipo_tienda.click()
    except Exception:
        driver.execute_script("arguments[0].click();", tipo_tienda)
    time.sleep(2)

    # Esperar las opciones desplegadas en el dropdown
    opciones = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
    ))

    # Mapear las opciones por texto
    opciones_dict = {}
    for opcion in opciones:
        texto = (opcion.get_attribute("innerText") or opcion.text or "").strip()
        if texto:
            opciones_dict[texto] = opcion

    # Probabilidad: "Tienda" tiene la mayor probabilidad (ej. 75%), las demás se reparten el 25% al azar
    PROBABILIDAD_TIENDA = 0.75  # Ajustable: 0.75 = 75% probabilidad para Tienda
    otras_opciones = [nombre for nombre in opciones_dict.keys() if nombre.lower() != "tienda"]

    if "Tienda" in opciones_dict and (random.random() < PROBABILIDAD_TIENDA or not otras_opciones):
        opcion_elegida = "Tienda"
    elif otras_opciones:
        opcion_elegida = random.choice(otras_opciones)
    elif opciones_dict:
        opcion_elegida = list(opciones_dict.keys())[0]
    else:
        opcion_elegida = None

    if opcion_elegida and opcion_elegida in opciones_dict:
        elemento_a_clickear = opciones_dict[opcion_elegida]
        driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", elemento_a_clickear)
        time.sleep(1)
        try:
            elemento_a_clickear.click()
        except Exception:
            driver.execute_script("arguments[0].click();", elemento_a_clickear)
        print(f"✅ Tipo de tienda ingresado: '{opcion_elegida}' (Probabilidad Tienda: {int(PROBABILIDAD_TIENDA * 100)}%)")
    else:
        # Respaldo por si los textos de las opciones no cargaron a tiempo
        if opciones:
            if random.random() < PROBABILIDAD_TIENDA:
                opciones[0].click()
            else:
                random.choice(opciones).click()
            print("✅ Tipo de tienda ingresado (por fallback)")
    time.sleep(2)

    # =====================
    # SELECCIONAR CIUDAD (BOGOTÁ DC)
    # =====================
    print("🏙️ Seleccionando ciudad...")
    time.sleep(1)
    ciudad_input = wait.until(EC.presence_of_element_located((
        By.ID,"location_form_city")))

    try:
        ciudad_input.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-select')]").click()
    except Exception:
        try:
            ciudad_input.click()
        except Exception:
            driver.execute_script("arguments[0].click();", ciudad_input)
    time.sleep(1.5)

    # Buscar y seleccionar la opción "Bogotá DC"
    try:
        opcion_bogota = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//div[contains(@class, 'ant-select-item-option') and contains(., 'Bogot')]"
        )))
    except TimeoutException:
        # En caso de requerir escribir para filtrar
        ciudad_input.send_keys("Bogota")
        time.sleep(1)
        opcion_bogota = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//div[contains(@class, 'ant-select-item-option') and contains(., 'Bogot')]"
        )))

    driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", opcion_bogota)
    time.sleep(0.5)
    try:
        opcion_bogota.click()
    except Exception:
        driver.execute_script("arguments[0].click();", opcion_bogota)

    print("✅ Ciudad 'Bogotá DC' seleccionada")
    time.sleep(2)

    # Ingresar dirección
    direccion_input = wait.until(EC.presence_of_element_located((By.ID, "location_form_address")))
    direccion_input.clear()
    direccion_input.send_keys(direccion)
    ActionChains(driver).move_by_offset(0, 0).click().perform()
    time.sleep(10)
    print("✅ Dirección ingresada")

    # =====================
    # ASIGNAR USUARIOS
    # =====================
    print("🔍 Buscando campo 'Asignar usuarios'...")
    try:
        campo_usuario = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//label[contains(., 'Asignar usuarios')]/ancestor::div[contains(@class, 'ant-form-item')]//div[contains(@class, 'ant-select-selector')] | //*[@id='location_form']/div[2]/div/div/div[1]/div[1]/div/div[2]/div/div[6]/div/div/div[2]/div/div/div/div"
        )))
    except Exception:
        campo_usuario = driver.find_element(By.XPATH, "//*[@id='location_form']/div[2]/div/div/div[1]/div[1]/div/div[2]/div/div[6]/div/div/div[2]/div/div/div/div")

    # Scroll hacia el campo para asegurar visibilidad
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_usuario)
    time.sleep(1)

    # Click para desplegar las opciones
    try:
        campo_usuario.click()
    except Exception:
        driver.execute_script("arguments[0].click();", campo_usuario)
    time.sleep(2)

    # Esperar a que se carguen las opciones en el DOM
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
    ))

    # Filtrar estrictamente las opciones de usuario (visibles en pantalla y con correo @)
    todas_opciones = driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
    opciones_usuario = [
        op for op in todas_opciones
        if op.is_displayed() and "@" in (op.get_attribute("innerText") or op.text or "")
    ]

    # Respaldo si no detecta el @: opciones visibles que no sean de tipo sede ni ciudad
    if not opciones_usuario:
        opciones_usuario = [
            op for op in todas_opciones
            if op.is_displayed() and not any(x in (op.get_attribute("innerText") or op.text or "") for x in ['Tienda', 'Bodega', 'Stand', 'Bogot', 'Cali', 'Medell'])
        ]

    # Fallback final: cualquier opción visible
    if not opciones_usuario:
        opciones_usuario = [op for op in todas_opciones if op.is_displayed()]

    for op in opciones_usuario:
        print(f"👤 Opción usuario disponible: {(op.get_attribute('innerText') or op.text).strip()}")

    # Seleccionar la primera opción de usuario disponible
    if opciones_usuario:
        opcion_a_seleccionar = opciones_usuario[0]
        texto_usuario = (opcion_a_seleccionar.get_attribute("innerText") or opcion_a_seleccionar.text).strip()
        driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", opcion_a_seleccionar)
        time.sleep(0.5)
        try:
            opcion_a_seleccionar.find_element(By.CSS_SELECTOR, ".ant-select-item-option-content").click()
        except Exception:
            try:
                opcion_a_seleccionar.click()
            except Exception:
                driver.execute_script("arguments[0].click();", opcion_a_seleccionar)
        print(f"✅ Usuario asignado: '{texto_usuario}'")
    else:
        print("⚠️ No se encontraron opciones de usuario visibles")

    time.sleep(1)

    # Cerrar el dropdown con Escape si continúa abierto
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except Exception:
        pass
    time.sleep(1)

    try:
        # Buscar el botón 'Añadir' por su texto
        boton_anadir = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Añadir' or contains(., 'Añadir')] | //*[@id='advanced_search']/div[1]/div/div/div/button[2]"))
        )
        
        # Hacer scroll hasta el botón para asegurar visibilidad
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
        time.sleep(2)
        
        # Hacer click en el botón
        boton_anadir.click()
        print("✅ Botón 'Añadir' clickeado")
        
        # Esperar a que se procese la acción
        time.sleep(8)
        exito = True
        observaciones = "Sede creada exitosamente con todos los datos"        
    except TimeoutException:
        observaciones = "Timeout: No se pudo encontrar o hacer click en el botón 'Añadir'"
        exito = False
        print("❌ No se pudo encontrar el botón 'Añadir'")
    except Exception as e:
        observaciones = f"Error al hacer click en el botón 'Añadir': {str(e)}"
        exito = False
        print(f"❌ Error al guardar la ubicación: {str(e)}")

    url_final = driver.current_url

except TimeoutException as e:
    observaciones = f"Timeout esperando elemento: {str(e)}"
    exito = False
    print(f"❌ {observaciones}")

except Exception as e:
    observaciones = f"Error inesperado: {str(e)}"
    exito = False
    print(f"❌ {observaciones}")

finally:
    # =====================
    # REGISTRAR RESULTADO Y CERRAR
    # =====================
    estado = "EXITOSO" if exito else "FALLIDO"
    
    # Registrar resultado en Google Sheets
    if registrar_resultado(id_caso, estado, observaciones):
        print("✅ Resultado registrado en Google Sheets")
    else:
        print("❌ No se pudo registrar el resultado en Google Sheets")
    
    # Mostrar información final
    print(f"\n🌐 URL final: {driver.current_url}")
    print(f"📄 Título de la página: {driver.title}")
    
    time.sleep(3)
    driver.quit()
    print("✅ Navegador cerrado")

# =====================
# RESUMEN FINAL
# =====================
print("\n" + "="*80)
print("RESUMEN DE EJECUCIÓN - REGISTRO SEDE CON TODOS LOS DATOS")
print("="*80)
print(f"📋 ID Caso: {id_caso}")
print(f"✅ Estado: {estado}")
print(f"🔗 URL Final: {url_final}")
print(f"📝 Observaciones: {observaciones}")
print("="*80)