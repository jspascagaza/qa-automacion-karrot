import csv
import datetime
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

# =====================
# ENTRADA DE DATOS
# =====================
nombre_producto = input("Nombre del producto: ")
descripcion = input("Descripción: ")

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
id_caso = "TC023"

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
    time.sleep(30)

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

    # Selección tipo de producto
    respuesta = input("¿Vas a crear un producto? (si/no): ").lower().strip()
    while respuesta not in ['si', 's', 'no', 'n']:
        print("Respuesta no válida. Por favor responde 'si' o 'no'")
        respuesta = input("¿Vas a crear un producto? (si/no): ").lower().strip()

    if respuesta in ['si', 's']:
        driver.find_element(By.XPATH, "//input[@value='Product']").click()
        print("Producto seleccionado")
    else:
        driver.find_element(By.XPATH, "//input[@value='Service']").click()
        print("Servicio seleccionado")
    time.sleep(2)

    # Nombre del producto
    input_nombre_producto = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='advanced_search_name']")))
    input_nombre_producto.send_keys(nombre_producto)
    time.sleep(1)

    # Selección de categoría
    listadocategorias = wait.until(
        EC.element_to_be_clickable((By.ID, "advanced_search_category"))
    )
    ActionChains(driver).move_to_element(listadocategorias).click().perform()
    time.sleep(1)

    opciones_categorias = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//*[text()]"))
    )

    print("Opciones encontradas:")
    for opcion in opciones_categorias:
        print(opcion.text)

    opcion_encontrada = None
    for opcion in opciones_categorias:
        if opcion.text.strip() == "Portátiles":
            opcion_encontrada = opcion
            break

    if opcion_encontrada:
        opcion_encontrada.click()
        print("✅ Categoría 'Portátiles' seleccionada")
    else:
        print("❌ No se encontró la categoría 'Portátiles'")

    # Selección de unidad (tipo de unidad)
    # Esperar el input (aunque no sea clickeable)
    input_unidad = wait.until(
        EC.presence_of_element_located((By.ID, "advanced_search_unit"))
    )

    # Buscar el contenedor visual del dropdown y hacer clic ahí
    dropdown_container = input_unidad.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-select')]")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select') and .//input[@id='advanced_search_unit']]")))
    ActionChains(driver).move_to_element(dropdown_container).click().perform()
    time.sleep(1)

    # Ahora selecciona la opción como ya lo haces
    opciones_unidad = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-option-content')]"))
    )

    print("Opciones de unidad encontradas:")
    for opcion in opciones_unidad:
        print(opcion.text)

    opcion_unidad_encontrada = None
    for opcion in opciones_unidad:
        if opcion.text.strip() == "Kilogramo":  # Cambia aquí por la unidad que necesites
            opcion_unidad_encontrada = opcion
            break

    if opcion_unidad_encontrada:
        opcion_unidad_encontrada.click()
        print("✅ Unidad 'Kilogramo' seleccionada")
    else:
        print("❌ No se encontró la unidad 'Kilogramo'")

    # Descripción del producto
    descripcionproducto = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='advanced_search_description']")))
    descripcionproducto.send_keys(descripcion)
    time.sleep(2)

    # Aquí puedes continuar con el flujo de guardado, etc.

    # --- Switch de producto perecedero ---
    def configurar_producto_perecedero(driver, es_perecedero=True, timeout=10):
        """
        Configura el switch "¿Es un producto perecedero?" en Alhadi
        
        Args:
            driver: Instancia del WebDriver
            es_perecedero (bool): True para activar, False para desactivar
            timeout (int): Tiempo de espera en segundos
        """
        if es_perecedero:
            try:
                wait = WebDriverWait(driver, timeout)
                label_perecedero = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//label[contains(text(), '¿Es un producto perecedero?')]"))
                )
                switch_container = label_perecedero.find_element(By.XPATH, "./following-sibling::div//div[contains(@class, 'ant-switch-handle')]")
                switch_container.click()
                print("✅ Switch '¿Es un producto perecedero?' ACTIVADO")
                return True
            except Exception as e:
                print(f"❌ Error al activar el switch de producto perecedero: {e}")
                return False
        else:
            print("⏭️  Switch '¿Es un producto perecedero?' NO activado (configuración: False)")
            return True

    configurar_producto_perecedero(driver, es_perecedero=True, timeout=10)

except Exception as e:
    print(f"❌ Error durante la ejecución: {str(e)}")