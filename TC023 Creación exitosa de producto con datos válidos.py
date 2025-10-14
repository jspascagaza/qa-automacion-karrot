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
    def configurar_producto_perecedero(driver, es_perecedero=True, timeout=10):
        """
        Controla el switch basado en el atributo aria-checked
        """
        try:
            wait = WebDriverWait(driver, timeout)
        
            # Buscar el switch por role y clase
            switch_xpath = "//button[@role='switch' and contains(@class, 'ant-switch')]"
            switch_btn = wait.until(EC.element_to_be_clickable((By.XPATH, switch_xpath)))
        
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch_btn)
            time.sleep(0.5)
        
            # Verificar estado actual usando aria-checked
            current_state = switch_btn.get_attribute("aria-checked")
            is_currently_checked = current_state == "true"
        
            print(f"🔍 Estado actual del switch: {'ACTIVADO' if is_currently_checked else 'DESACTIVADO'}")
        
            # Activar/desactivar solo si es necesario
            if es_perecedero and not is_currently_checked:
                switch_btn.click()
                print("✅ Switch ACTIVADO (Producto perecedero)")
            elif not es_perecedero and is_currently_checked:
                switch_btn.click()
                print("✅ Switch DESACTIVADO (Producto no perecedero)")
            else:
                print(f"⏭️ Switch ya está en el estado deseado")
        
            return True
        
        except Exception as e:
            print(f"❌ Error al configurar el switch: {e}")
            return False
    configurar_producto_perecedero(driver, es_perecedero=False)
    time.sleep(2)

    def manejar_atributos_adicionales(driver, agregar_atributos=False, timeout=10):
        """
        Maneja el botón 'Agregar nuevo atributo'
        Solo hace clic si agregar_atributos es True
        """
        try:
            if not agregar_atributos:
                print("⏭️  No se agregarán atributos adicionales")
                return True
        
            wait = WebDriverWait(driver, timeout)
        
            # Buscar el botón por texto y clases
            boton_xpath = "//button[contains(@class, 'ant-btn') and contains(text(), 'Agregar nuevo atributo')]"
            boton = wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath)))
        
            # Scroll y clic
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
            time.sleep(0.5)
            boton.click()
            print("✅ Botón 'Agregar nuevo atributo' clickeado")
            nombre_atributo = input("Nombre del atributo: ")
            input_nombre_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_attributeName")))
            input_nombre_atributo.send_keys(nombre_atributo)

            # valor primer atributo
            input_valor_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_option1")))
            input_valor_atributo.send_keys("memoria 1tb")
            time.sleep(1)
            # valor segundo atributo
            input_valor_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_option2")))
            input_valor_atributo.send_keys("memoria 2tb")
            time.sleep(1)
            print("✅ Atributos adicionales configurados")
            boton_ok = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-btn-primary')]//span[text()='OK']")))
            boton_ok.click()
            print("✅ Atributos adicionales guardados")
            return True
        
        except Exception as e:
            print(f"❌ Error al hacer clic en 'Agregar nuevo atributo': {e}")
            return False

    manejar_atributos_adicionales(driver, agregar_atributos=True)
    time.sleep(2)
    def generar_sku_aleatorio(driver, agregar_atributos=True, timeout=10):
        """
        Genera y llena el campo SKU con un ID aleatorio si se agregan atributos
        """
        try:
            if not agregar_atributos:
                print("⏭️  No se agregaron atributos - omitiendo SKU")
                return True
            wait = WebDriverWait(driver, timeout)
            sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            campo_sku = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'sku') and contains(@id, 'advanced_search_memoria')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_sku)
            time.sleep(0.5)
            campo_sku.clear()
            campo_sku.send_keys(sku_aleatorio)
            print(f"✅ SKU aleatorio generado: '{sku_aleatorio}'")
            
            barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            campo_barcode = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, 'advanced_search_memoria') and contains(@class, 'barcode')]")))
            campo_barcode.clear()
            campo_barcode.send_keys(barcode_aleatorio)
            print(f"✅ Barcode aleatorio generado: '{barcode_aleatorio}'")

            valor_costo = input("ingresa Valor de costo: ")
            campo_costo = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, 'advanced_search_memoria') and contains(@id, 'cost')]")))
            campo_costo.clear()
            campo_costo.send_keys(valor_costo)
            print(f"✅ Valor de costo ingresado: '{valor_costo}'")

            valor_precio = input("ingresa Valor de precio: ")
            campo_precio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, 'advanced_search_memoria') and contains(@id, 'price')]")))
            campo_precio.clear()
            campo_precio.send_keys(valor_precio)
            print(f"✅ Valor de precio ingresado: '{valor_precio}'")
            return True
        
        except Exception as e:
            print(f"❌ Error al generar SKU: {e}")
            return False
    generar_sku_aleatorio(driver, agregar_atributos=True)
    
except Exception as e:
    print(f"❌ Error durante la ejecución: {str(e)}")