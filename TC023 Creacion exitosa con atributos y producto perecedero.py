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
from faker import Faker
import faker_commerce; print(faker_commerce.__file__)
import random


fake = Faker('es_CO')
# =====================
# ENTRADA DE DATOS
# =====================
try:
    fake.add_provider(faker_commerce.Provider)
except Exception as e:
    print("⚠️ No se pudo añadir faker_commerce.Provider:", e)

# Intentar detectar el mejor método disponible para nombre de producto
if hasattr(fake, 'ecommerce_name'):
    nombre_producto = fake.ecommerce_name()
elif hasattr(fake, 'commerce_product_name'):
    nombre_producto = fake.commerce_product_name()
elif hasattr(fake, 'product_name'):
    nombre_producto = fake.product_name()
elif hasattr(fake, 'commerce_name'):
    nombre_producto = fake.commerce_name()
else:
    # Fallback: lista manual (celulares + computadores)
    productos = [
        "Samsung Galaxy S23", "Apple iPhone 15", "Xiaomi Redmi Note 13", "Motorola Edge 40",
        "Huawei P60 Pro", "Oppo Find X7", "Realme GT Neo 6", "Honor Magic 6", "Nokia G60",
        "HP Pavilion 15", "Dell Inspiron 14", "Lenovo ThinkPad X1", "Asus VivoBook 16",
        "Acer Aspire 5", "Apple MacBook Air M3", "MSI Modern 14", "Huawei MateBook D16",
        "Samsung Galaxy Book4", "Lenovo IdeaPad 3", "Asus ZenBook 14", "Dell XPS 13"
    ]
    nombre_producto = random.choice(productos)

# Descripción: intentar métodos del provider o usar faker como fallback
if hasattr(fake, 'ecommerce_description'):
    descripcion = fake.ecommerce_description()
elif hasattr(fake, 'commerce_description'):
    descripcion = fake.commerce_description()
elif hasattr(fake, 'product_description'):
    descripcion = fake.product_description()
else:
    descripcion = fake.sentence(nb_words=15)
print (f"🛒 Nombre del producto generado: {nombre_producto}")
if hasattr(fake, 'ecommerce_price'):
    precio = fake.ecommerce_price()
elif hasattr(fake, 'commerce_price'):
    precio = fake.commerce_price()
elif hasattr(fake, 'commerce_price_in_cents'):
    precio = fake.commerce_price_in_cents()
else:
    # Fallback: precio aleatorio realista en COP (ej. entre 400k y 8M)
    precio = round(random.uniform(400_000, 8_000_000), 2)
print(f"💰 Precio del producto generado: {precio}")

pregunta_atributos = "true"
if pregunta_atributos == 'true':
    activar_atributos = True
    noactivar_atributos = False
    print("✅ Modo: ACTIVAR atributos")
elif pregunta_atributos == 'false':
    activar_atributos = False
    noactivar_atributos = True
    print("⏭️ Modo: NO activar atributos")
else:
    activar_atributos = False
    noactivar_atributos = False
    print("❌ Respuesta inválida")
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
id_caso = "TC023-003"

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
        sheet.update_cell(fila, 11, automatizado)   # Columna K
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
    #email_input.send_keys("js.pascagaza@karrotup.com")
    email_input.send_keys("karrotdev@outlook.com")

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
    respuesta = "si"
    while respuesta not in ['si', 's', 'no', 'n']:
        print("Respuesta no válida. Por favor responde 'si' o 'no'")
        respuesta = "si"

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
    def crear_categoria_si_es_necesario(driver, wait):
        """
        Verifica si existe el botón 'añadir categoria' y lo crea si es necesario
        """
        try:
            # Verificar si existe el botón "añadir categoria"
            # Hacer clic y mantener el hover sobre el dropdown
            dropdown_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ant-select-selector")))
            actions = ActionChains(driver)
            actions.click_and_hold(dropdown_element).perform()

            # Obtener las opciones
            opciones_categorias = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//*[text()]"))
            )

            # Liberar cuando termines
            actions.release().perform()
            boton_anadir_categoria_xpath = "/html/body/div[4]/div/div/div/div/div/div[3]/button"
            boton_anadir_categoria = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, boton_anadir_categoria_xpath))
            )
            
            if boton_anadir_categoria:
                print("🔍 Botón 'añadir categoria' encontrado, procediendo a crear categoría...")
                boton_anadir_categoria.click()
                time.sleep(2)
                
                # Esperar a que aparezca el input para agregar categoría
                categoria_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.ant-input")))
                
                # Generar nombre de categoría (puedes ajustar según tus necesidades)
                categorias_posibles = ["Consolas", "Computadores", "Celulares", "Accesorios", "Portátiles", "Otros"]
                nombre_categoria = random.choice(categorias_posibles)
                categoria_input.send_keys(nombre_categoria)
                print(f"✅ Nombre de categoría ingresado: {nombre_categoria}")
                time.sleep(2)
                
                # Hacer click en el botón de confirmar (OK o similar)
                boton_confirmar = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-btn-primary"))
                )
                boton_confirmar.click()
                print("✅ Categoría creada exitosamente")
                time.sleep(3)
                
                return True
        except TimeoutException:
            # El botón no existe, continuar con el flujo normal
            print("ℹ️ No se encontró el botón 'añadir categoria', continuando con el flujo normal")
            return False
        except Exception as e:
            print(f"⚠️ Error al verificar/crear categoría: {e}")
            return False
    
    # Intentar seleccionar categoría (con reintentos si es necesario crear una)
    max_intentos = 2
    categoria_seleccionada = False
    
    for intento in range(max_intentos):
        listadocategorias = wait.until(
            EC.element_to_be_clickable((By.ID, "advanced_search_category"))
        )
        ActionChains(driver).move_to_element(listadocategorias).click().perform()
        time.sleep(1)
        
        # Verificar si necesitamos crear una categoría
        if intento == 0:
            crear_categoria_si_es_necesario(driver, wait)
        
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
            categoria_seleccionada = True
            break
        else:
            print(f"❌ No se encontró la categoría 'Portátiles' (intento {intento + 1}/{max_intentos})")
            if intento < max_intentos - 1:
                # Cerrar el dropdown y reintentar
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(1)
    
    if not categoria_seleccionada:
        print("❌ No se pudo seleccionar la categoría 'Portátiles' después de los intentos")

    crear_categoria_si_es_necesario(driver, wait)

    # Selección de unidad (tipo de unidad)
    # Esperar el input (aunque no sea clickeable)
    input_tipounidad = wait.until(
        EC.presence_of_element_located((By.ID, "advanced_search_unitGroup"))
    )

    time.sleep(1)    
    dropdown_container = input_tipounidad.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-select')]")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select') and .//input[@id='advanced_search_unitGroup']]")))
    ActionChains(driver).move_to_element(dropdown_container).click().perform()
    time.sleep(1)   
    opciones_unidad = wait.until(
    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-option-content')]"))
    )

    for opcion in opciones_unidad:
        print(opcion.text)

    opcion_unidad_encontrada = None
    for opcion in opciones_unidad:
        if opcion.text.strip() == "Cantidad / Unidades":  # Cambia aquí por la unidad que necesites
            opcion_unidad_encontrada = opcion
            break
    if opcion_unidad_encontrada:
        opcion_unidad_encontrada.click()
        print("✅ Unidad 'Cantidad / Unidades' seleccionada")
    else:
        print("❌ No se encontró la unidad 'Cantidad / Unidades'")


    inputs = driver.find_elements(By.CLASS_NAME, "ant-select-selection-search-input")
    # Selecciona de forma segura el tercer input si existe; de lo contrario usa el último disponible
    if not inputs:
        raise Exception("No se encontraron inputs 'ant-select-selection-search-input'")
    index = 2 if len(inputs) > 2 else len(inputs) - 1
    imput_unidad = inputs[index]
    imput_unidad.click()    
    time.sleep(1)

    opciones_unidad = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-option-content')]"))
    )

    for opcion in opciones_unidad:
        print(opcion.text)
        if opcion.text.strip() == "Unidad (u)":
            opcion_unidad_encontrada = opcion
            break
    if opcion_unidad_encontrada:
        opcion_unidad_encontrada.click()
        print("✅ Unidad 'Unidad' seleccionada")
    else:
        print("❌ No se encontró la unidad 'Unidad'")    

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
    configurar_producto_perecedero(driver, es_perecedero=True)
    time.sleep(2)
    
    # TENER EN CUENTA QUE PARA LAS FUNCIONES DE ABAJO, SE DEBE ACTIVAR agregar_atributos=True PARA QUE FUNCIONEN
    def manejar_atributos_adicionales(driver, agregar_atributos=False, timeout=10):
        """
        Maneja el botón 'Agregar nuevo atributo' y retorna los valores usados
     """
        try:
            if not agregar_atributos:
                print("⏭️  No se agregarán atributos adicionales")
                return None, None
        
            wait = WebDriverWait(driver, timeout)
        
            # Buscar el botón por texto y clases
            boton_xpath = "//button[contains(@class, 'ant-btn') and contains(text(), 'Agregar nuevo atributo')]"
            boton = wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath)))
        
            # Scroll y clic
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
            time.sleep(0.5)
            boton.click()
            print("✅ Botón 'Agregar nuevo atributo' clickeado")
        
            # Obtener nombre del atributo (mantener espacios)
            nombre_atributo = "memoria"
            input_nombre_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_attributeName")))
            input_nombre_atributo.send_keys(nombre_atributo)

            # Obtener valores de atributos (mantener espacios)
            valores_atributos = []
        
            # valor primer atributo
            valor1 = "1tb"
            input_valor_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_option1")))
            input_valor_atributo.send_keys(valor1)
            valores_atributos.append(valor1)  # Mantener el espacio
            time.sleep(1)
        
            # valor segundo atributo
            valor2 = "2tb"
            input_valor_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_option2")))
            input_valor_atributo.send_keys(valor2)
            valores_atributos.append(valor2)  # Mantener el espacio
            time.sleep(1)
        
            print("✅ Atributos adicionales configurados")
        
            # Guardar
            boton_ok = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-btn-primary')]//span[text()='OK']")))
            boton_ok.click()
            print("✅ Atributos adicionales guardados")
        
            return nombre_atributo, valores_atributos
        except Exception as e:
            print(f"❌ Error al hacer clic en 'Agregar nuevo atributo': {e}")
            return None, None
        
    nombre_atributo, valores_atributos = manejar_atributos_adicionales(driver, agregar_atributos=activar_atributos)
    time.sleep(2)
    
    def generar_campos_por_atributo(driver, nombre_atributo, valores_atributos, timeout=10, agregar_atributos=False):
        """
        Genera SKU, barcode, costo y precio para cada combinación de atributos
        Maneja IDs con espacios como: advanced_search_memoria 1tbsku
        """
        # Si no se deben agregar atributos, salir sin ejecutar
        if not agregar_atributos:
            print("⏭️  generar_campos_por_atributo: agregar_atributos=False, no se ejecuta")
            return False

        try:
            wait = WebDriverWait(driver, timeout)
        
            for valor_atributo in valores_atributos:
                print(f"\n🎯 Procesando combinación: {nombre_atributo} - {valor_atributo}")
            
                # Construir el ID base dinámico CON ESPACIO
                id_base = f"advanced_search_{valor_atributo}"
            
                # 1. SKU Aleatorio
                sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
                # Buscar por ID exacto con espacio
                try:
                    campo_sku = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}sku")))
                except:
                    # Si falla, buscar por contains
                    campo_sku = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@class, 'sku')]")) )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_sku)
                time.sleep(0.5)
                campo_sku.clear()
                campo_sku.send_keys(sku_aleatorio)
                print(f"✅ SKU para {valor_atributo}: '{sku_aleatorio}'")
            
                # 2. Barcode Aleatorio
                barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                try:
                    campo_barcode = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}barcode")))
                except:
                    campo_barcode = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@class, 'barcode')]")) )
                campo_barcode.clear()
                campo_barcode.send_keys(barcode_aleatorio)
                print(f"✅ Barcode para {valor_atributo}: '{barcode_aleatorio}'")

                # 3. Costo
                valor_costo = precio            
                try:
                    campo_costo = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}cost")))
                except:
                    campo_costo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@id, 'cost')]")) )
                campo_costo.clear()
                campo_costo.send_keys(valor_costo)
                print(f"✅ Costo para {valor_costo}: '{valor_costo}'")

                # 4. Precio
                valor_precio = precio            
                try:
                    campo_precio = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}price")))
                except:
                    campo_precio = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@id, 'price')]")) )
                campo_precio.clear()
                campo_precio.send_keys(valor_precio)
                print(f"✅ Precio para {valor_atributo}: '{valor_precio}'")
                time.sleep(1)
            return barcode_aleatorio,sku_aleatorio
        
        except Exception as e:
            print(f"❌ Error al generar campos para atributos: {e}")
            return False
    resultado = generar_campos_por_atributo(driver, nombre_atributo, valores_atributos, timeout=10, agregar_atributos=activar_atributos)
    
    # Capturar los valores de barcode y sku
    if activar_atributos and resultado:
        barcode_aleatorio, sku_aleatorio = resultado
    else:
        barcode_aleatorio = None
        sku_aleatorio = None
    print(f"✅ Barcode: {barcode_aleatorio}, SKU: {sku_aleatorio}")

    boton_anadir = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'ant-btn-primary') and contains(text(), 'Añadir')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
    boton_anadir.click()
    print("✅ Click en Añadir")
    time.sleep(10)
    driver.refresh()
    time.sleep(5)
    try:
        # abrir el select y esperar a que el dropdown esté visible sin que se cierre
        select_xpath = "//div[contains(@class, 'ant-select') and .//span[contains(@title, 'Buscar por')]]"
        select_element = wait.until(EC.element_to_be_clickable((By.XPATH, select_xpath)))
        print("✅ Select encontrado")
        # usar ActionChains para abrir y mantener foco
        ActionChains(driver).move_to_element(select_element).click().perform()
        time.sleep(1)
        print("✅ Select abierto")
        # esperar a que el dropdown real de Ant Design sea visible
        dropdown = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]"))
        )
        print("✅ Dropdown visible")
        # mover el cursor dentro del dropdown para evitar que el foco se pierda y se cierre
        ActionChains(driver).move_to_element(dropdown).perform()
        time.sleep(1)
        print("✅ Dropdown movido")
        # ahora buscar las opciones dentro del dropdown (no vuelvas a clickear el select)
        opciones_dropdown = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'ant-select-dropdown')]//div[contains(@class,'ant-select-item-option-content')]"))
        )
        time.sleep(1)
        print("Opciones de busqueda encontradas:")
        for opcion in opciones_dropdown:
            print(opcion.text)
        opcion_busqueda_encontrada = None
        for opcion in opciones_dropdown:
            if opcion.text.strip() == "Buscar por Código de barras":  # Cambia aquí por la busqueda que necesites
                opcion_busqueda_encontrada = opcion
                break
        if opcion_busqueda_encontrada:
                opcion_busqueda_encontrada.click()
                print("✅ Opción de búsqueda 'Buscar por codigo de barras ' seleccionada")
                time.sleep(5)
                campo_busqueda = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@role='combobox' and @type='search' and contains(@class, 'ant-input')]")))
                campo_busqueda.clear()
                campo_busqueda.send_keys(barcode_aleatorio)
                time.sleep(10)  # Usar el barcode generado
                campo_busqueda.send_keys(Keys.CONTROL + "a")
                campo_busqueda.send_keys(barcode_aleatorio)    
                campo_busqueda.send_keys(Keys.ARROW_DOWN)
                time.sleep(2)
                campo_busqueda.send_keys(Keys.ENTER)
                print(f"✅ Búsqueda realizada con : {barcode_aleatorio}")
                time.sleep(5)
                elemento = driver.find_element(By.XPATH, f"//*[contains(text(), '{nombre_producto
                }')]")
                print("✅ campo encontrado enviado en campo de búsqueda")
                time.sleep(5)
                observaciones = f"Producto creado con éxito. SKU: {sku_aleatorio}, Barcode: {barcode_aleatorio}"
                estado = "EXITOSO"
                registrar_resultado(id_caso, estado, observaciones)
        else:
            print("❌ No se encontró la opción de búsqueda 'Buscar ")
            observaciones = "No se encontró la opción de búsqueda 'Buscar por Nombre'"
            estado = "FALLIDO"
            registrar_resultado(id_caso, estado, observaciones)
    except Exception as e:
        print(f"❌ Error al abrir el dropdown: {e}")
        print("Opciones de busqueda encontradas:")
        observaciones = f"Error al abrir el dropdown: {e}"
        estado = "FALLIDO"
        registrar_resultado(id_caso, estado, observaciones)
except Exception as e:
    print(f"❌ Error durante la ejecución: {str(e)}")
    observaciones = f"Error durante la ejecución: {str(e)}"
    estado = "FALLIDO"
    registrar_resultado(id_caso, estado, observaciones)