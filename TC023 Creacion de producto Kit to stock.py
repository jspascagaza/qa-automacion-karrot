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

nombre_producto = f"Kit {nombre_producto}"

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
    os.getenv("GOOGLE_CREDENTIALS_PATH", "automatizacion-karrot-456d1a1552ca.json"),
    scope
)
client = gspread.authorize(creds)

for _ in range(5):
    try:
        spreadsheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"
        )
        sheet = spreadsheet.sheet1
        break
    except Exception as e:
        print(f"⏳ Esperando a Google Sheets API por error: {e}")
        time.sleep(5)


# Variable para controlar el éxito de la ejecución
exito = False
observaciones = ""
url_final = ""

# =====================
# PRUEBA REGISTRO COMPLETO CON CONSULTOR Y VERIFICACIÓN
# =====================
id_caso = "TC023-002"

def registrar_resultado(id_caso, estado, observaciones=""):
    for _ in range(5):
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
            return
        except Exception as e:
            if "503" in str(e) or "APIError" in str(e) or "Timeout" in str(e):
                print(f"⏳ Error de red en Google Sheets (503/Timeout). Reintentando...")
                import time
                time.sleep(5)
            else:
                print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")
                return


# =====================
# INICIO DE AUTOMATIZACIÓN
# =====================
try:
    driver = webdriver.Chrome()
    driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    wait = WebDriverWait(driver, 40)

    # Login
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    time.sleep(15)

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
    boton_agregar = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div[2]/div/div/div/div[1]/div/button[1]"))
    )
    boton_agregar.click()
    print("✅ Click en Agregar Artículo")
    time.sleep(10)

    # Verificar que el texto "Añadir nuevo producto" esté presente
    #elemento = WebDriverWait(driver, 10).until(
    #    EC.visibility_of_element_located((By.XPATH, "//h2[@class='mb-3' and text()='Añadir nuevo producto']"))
    #)
    #print("Texto encontrado:", elemento.text)
    #time.sleep(2)

    # Selección tipo de producto (nuevo UI)
    tipo_producto = os.getenv("TIPO_PRODUCTO", "Kit to stock")  # Opciones: 'Producto normal', 'Kit to order', 'Kit to stock'
    try:
        card = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='button' and .//div[text()='{tipo_producto}']]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(0.5)
        card.click()
        print(f"✅ {tipo_producto} seleccionado")
    except Exception as e:
        print(f"❌ Error al seleccionar {tipo_producto}: {e}")
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
        if opcion.text.strip() == "PORTATILES":
            opcion_encontrada = opcion
            break

    if opcion_encontrada:
        opcion_encontrada.click()
        print("✅ Categoría 'Portátiles' seleccionada")
    else:
        print("❌ No se encontró la categoría 'Portátiles'")

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

    def variantes_referencias_producto(driver, timeout=10, agregar_atributos=True):
        if not agregar_atributos:
            print("⏭️  No se agregarán atributos - función omitida")
            return None, None
            
        print("⏳ Configurando atributos en la interfaz...")
        try:
            # 1. Hacer clic en "+ Agregar Otro Atributo" si los campos no están visibles aún
            input_nombre_existente = driver.find_elements(
                By.XPATH, "//input[@placeholder='Nombre del atributo' or contains(@id, 'attributeName')]"
            )
            if not input_nombre_existente or not input_nombre_existente[0].is_displayed():
                xpath_btn_atributo = (
                    "//button[(contains(., 'Agregar') or contains(., 'Añadir')) and contains(., 'Atributo')] | "
                    "//*[contains(text(), 'Agregar Otro Atributo') or contains(text(), 'Agregar Atributo') or contains(text(), 'Agregar nuevo atributo')]"
                )
                btn_atributo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_btn_atributo)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_atributo)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", btn_atributo)
                time.sleep(2)

            # 2. Llenar "Nombre del atributo"
            nombre_atributo = "Color"
            input_nombre = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@placeholder='Nombre del atributo' or contains(@id, 'attributeName')]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_nombre)
            input_nombre.send_keys(Keys.CONTROL + "a")
            input_nombre.send_keys(nombre_atributo)
            print(f"✅ Nombre de atributo ingresado: '{nombre_atributo}'")
            time.sleep(1)

            # 3. Llenar "Agregar valor" y presionar ENTER para cada valor
            valores_atributo = ["Negro", "Azul"]
            input_valor = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@placeholder='Agregar valor' or contains(@id, 'option') or contains(@placeholder, 'valor')]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_valor)
            for val in valores_atributo:
                input_valor.send_keys(val)
                time.sleep(0.5)
                input_valor.send_keys(Keys.ENTER)
                time.sleep(1)
                print(f"✅ Valor de atributo ingresado con ENTER: '{val}'")

            time.sleep(2)
        except Exception as e:
            print(f"❌ Error al configurar campos de atributo: {e}")

        def obtener_campo(wait_obj, drv, id_campo):
            # Si hay un modal abierto (como 'Editar variante'), buscar primero dentro del modal
            modales = drv.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal-content')]")
            if modales:
                for modal in modales:
                    if modal.is_displayed():
                        inputs_modal = modal.find_elements(
                            By.XPATH, f".//input[contains(@id, '{id_campo}') or contains(translate(@placeholder, 'SKU', 'sku'), '{id_campo}') or contains(translate(@placeholder, 'BARCODE', 'barcode'), '{id_campo}')]"
                        )
                        for inp in inputs_modal:
                            if inp.is_displayed():
                                return inp
            try:
                return wait_obj.until(EC.presence_of_element_located((By.ID, id_campo)))
            except Exception:
                try:
                    return drv.find_element(By.ID, f"advanced_search_undefined{id_campo}")
                except Exception:
                    inputs = drv.find_elements(By.XPATH, f"//input[contains(@id, '{id_campo}')]")
                    for input_elem in inputs:
                        if input_elem.is_displayed():
                            return input_elem
                    raise Exception(f"No se pudo localizar el campo {id_campo}")

        # 4. Detectar cuántas variantes se generaron en la tabla y procesar cada una
        xpath_lapices_tabla = (
            "//*[@id='advanced_search']/div[2]/div/div[3]/div[3]/div/div[2]/div[2]/div[position()>=2]/div[9]/button | "
            "//*[@id='advanced_search']/div[2]/div/div[3]/div[3]/div/div[2]/div[2]/div/div[9]/button | "
            "//*[@id='advanced_search']//div[contains(@class, 'ant-table') or contains(@class, 'table')]//button | "
            "//div[contains(@class, 'ant-table') or self::table]//tr//*[contains(@class, 'anticon-edit') or @aria-label='edit']/ancestor::button"
        )

        lapices_existentes = driver.find_elements(By.XPATH, xpath_lapices_tabla)
        lapices_visibles = [l for l in lapices_existentes if l.is_displayed()]
        num_variantes = len(lapices_visibles) if lapices_visibles else 1
        print(f"📋 Se detectaron {num_variantes} variante(s) en la tabla para configurar.")

        ultimo_barcode = None
        ultimo_sku = None

        for index_variante in range(num_variantes):
            print(f"\n⚙️ Configurando variante #{index_variante + 1} de {num_variantes}...")

            # Abrir edición de la variante haciendo clic en su lápiz
            try:
                lapices = driver.find_elements(By.XPATH, xpath_lapices_tabla)
                lapices_visibles = [l for l in lapices if l.is_displayed()]
                
                if index_variante < len(lapices_visibles):
                    lapiz_target = lapices_visibles[index_variante]
                elif lapices_visibles:
                    lapiz_target = lapices_visibles[0]
                else:
                    lapiz_target = None

                if lapiz_target:
                    print(f"✅ Click en lápiz de variante #{index_variante + 1}")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lapiz_target)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", lapiz_target)
                    time.sleep(3)
                else:
                    print(f"⚠️ No se localizó el lápiz para la variante #{index_variante + 1}")
            except Exception as e:
                print(f"⚠️ Error al abrir modal del lápiz en variante #{index_variante + 1}: {e}")

            # 4.1. Agregar receta del kit si aplica
            try:
                print("⏳ Buscando botón 'Agregar receta del kit' / 'Añadir Materia Prima'...")
                xpath_btn_receta = (
                    "//div[contains(@class, 'ant-modal')]//button[contains(., 'Receta') or contains(., 'receta') or contains(., 'Materia Prima')]"
                    " | //button[.//span[contains(text(), 'Agregar receta del kit') or contains(text(), 'Materia Prima')]]"
                )
                btn_receta = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_btn_receta)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_receta)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", btn_receta)
                print("✅ Modal 'Receta' / 'Materia Prima' abierto")
                time.sleep(2)
                
                producto_receta = os.getenv("PRODUCTO_RECETA", "Monitor 4K 27")
                
                modales = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal-content') and .//div[contains(., 'Receta')]]")
                modal_receta = modales[-1] if modales else driver.find_element(By.XPATH, "//div[contains(@class, 'ant-modal-content')]")
                
                xpath_inputs_receta = (
                    ".//input[not(contains(@placeholder, 'materia prima')) and not(contains(@placeholder, 'Buscar materia prima')) and not(@type='hidden')]"
                )
                inputs_receta = modal_receta.find_elements(By.XPATH, xpath_inputs_receta)
                
                input_target = None
                for inp in inputs_receta:
                    if inp.is_displayed():
                        ph = (inp.get_attribute("placeholder") or "").lower()
                        if "materia prima" not in ph:
                            input_target = inp
                            break
                
                if not input_target:
                    try:
                        input_target = driver.find_element(By.XPATH, "//*[@id='rc_select_9']")
                    except Exception:
                        all_inputs = modal_receta.find_elements(By.XPATH, ".//input[not(@type='hidden')]")
                        for inp in all_inputs:
                            if inp.is_displayed():
                                input_target = inp
                                break

                if input_target:
                    print(f"✅ Se encontró campo de producto terminado en el modal Receta")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_target)
                    time.sleep(1)
                    driver.execute_script("arguments[0].focus(); arguments[0].click();", input_target)
                    time.sleep(1)
                    
                    try:
                        actions = ActionChains(driver)
                        actions.move_to_element(input_target).click().key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).send_keys(producto_receta).perform()
                    except Exception:
                        input_target.send_keys(Keys.CONTROL + "a")
                        input_target.send_keys(Keys.BACKSPACE)
                        input_target.send_keys(producto_receta)
                        
                    time.sleep(2)
                    valor_actual = input_target.get_attribute("value")
                    if not valor_actual:
                        input_target.send_keys(producto_receta)
                        time.sleep(2)

                    print(f"✅ Producto '{producto_receta}' escrito en el campo de la Receta")

                    try:
                        dropdown_opciones = driver.find_elements(
                            By.XPATH, "//div[contains(@class, 'ant-select-dropdown') and not(contains(@style, 'display: none'))]//div[contains(@class, 'ant-select-item')]"
                        )
                        if dropdown_opciones:
                            target_opc = None
                            for opc in dropdown_opciones:
                                if opc.is_displayed():
                                    target_opc = opc
                                    break
                            if target_opc:
                                print("✅ Seleccionando opción del listado de la receta...")
                                driver.execute_script("arguments[0].click();", target_opc)
                            else:
                                input_target.send_keys(Keys.ENTER)
                        else:
                            input_target.send_keys(Keys.ENTER)
                    except Exception:
                        input_target.send_keys(Keys.ENTER)
                        
                    time.sleep(2)

                botones_aplicar = modal_receta.find_elements(
                    By.XPATH, ".//button[span[text()='Aplicar'] or contains(., 'Aplicar')]"
                )
                if botones_aplicar:
                    print("✅ Aplicando cambios en el modal Receta...")
                    driver.execute_script("arguments[0].click();", botones_aplicar[-1])
                    time.sleep(2)

            except Exception as e:
                print(f"⚠️ Nota sobre receta del kit en variante #{index_variante + 1}: {e}")
            time.sleep(2)

            # 4.2. Ingresar SKU, Barcode, Costo y Precio para la variante actual
            sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            try:
                campo_sku = obtener_campo(wait, driver, "sku")
                driver.execute_script("arguments[0].value = '';", campo_sku)
                campo_sku.send_keys(Keys.CONTROL + "a")
                campo_sku.send_keys(sku_aleatorio)
                print(f"✅ Valor SKU nuevo (#{index_variante + 1}): '{sku_aleatorio}'")
            except Exception as e:
                print(f"❌ Error configurando SKU en variante #{index_variante + 1}: {e}")
                
            barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            try:
                campo_barcode = obtener_campo(wait, driver, "barcode")
                driver.execute_script("arguments[0].value = '';", campo_barcode)
                campo_barcode.send_keys(Keys.CONTROL + "a")
                campo_barcode.send_keys(barcode_aleatorio)
                print(f"✅ Valor nuevo barcode (#{index_variante + 1}): '{barcode_aleatorio}'")
            except Exception as e:
                print(f"⚠️ Campo barcode falló en variante #{index_variante + 1}: {e}")

            valor_costo = precio            
            try:
                campo_costo = obtener_campo(wait, driver, "cost")
                driver.execute_script("arguments[0].value = '';", campo_costo)
                campo_costo.send_keys(Keys.CONTROL + "a")
                campo_costo.send_keys(str(valor_costo))
                print(f"✅ Costo para la variante (#{index_variante + 1}): '{valor_costo}'")
            except Exception as e:
                print(f"❌ Error configurando costo en variante #{index_variante + 1}: {e}")

            try:
                campo_precio = driver.find_elements(By.ID, "price")
                if campo_precio and campo_precio[0].is_displayed():
                    driver.execute_script("arguments[0].value = '';", campo_precio[0])
                    campo_precio[0].send_keys(Keys.CONTROL + "a")
                    campo_precio[0].send_keys(str(precio))
                    print(f"✅ Precio para la variante (#{index_variante + 1}): '{precio}'")
            except:
                pass

            # 4.3. Hacer clic en "Aplicar" del modal de edición de variante
            try:
                boton_aplicar = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal')]//button[span[text()='Aplicar'] or contains(., 'Aplicar')] | //button[span[text()='Aplicar']]")
                if boton_aplicar and len(boton_aplicar) > 0:
                    print(f"✅ Click en botón 'Aplicar' del modal de la variante #{index_variante + 1}")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_aplicar[-1])
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", boton_aplicar[-1])
                    time.sleep(2)
            except Exception as e:
                print(f"⚠️ No se encontró botón 'Aplicar' del modal en variante #{index_variante + 1}: {e}")

            ultimo_barcode = barcode_aleatorio
            ultimo_sku = sku_aleatorio

        return ultimo_barcode, ultimo_sku

    
    barcode_aleatorio, sku_aleatorio = variantes_referencias_producto(driver, timeout=10, agregar_atributos=activar_atributos)

    time.sleep(2)
    boton_anadir = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='advanced_search']/div[1]/div/div/div/button[2] | //button[@type='submit' and contains(@class, 'ant-btn-primary')]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
    boton_anadir.click()
    print("✅ Click en Añadir")
    time.sleep(10)
    driver.refresh()
    time.sleep(5)
    try:
        # Abrir el select y esperar a que el dropdown esté visible
        select_xpath = (
            "//div[contains(@class, 'ant-select') and (span[contains(@title, 'Buscar por')] or .//span[contains(text(), 'Buscar por')])]"
            " | //div[contains(@class, 'ant-select') and (span[contains(@title, 'Buscar')] or .//span[contains(text(), 'Buscar')])]"
            " | //div[contains(@class, 'ant-select-single')]"
        )
        
        select_candidates = driver.find_elements(By.XPATH, select_xpath)
        select_element = None
        for cand in select_candidates:
            if cand.is_displayed():
                select_element = cand
                break

        if not select_element:
            select_element = wait.until(EC.element_to_be_clickable((By.XPATH, select_xpath)))

        print("✅ Select de búsqueda encontrado")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_element)
        time.sleep(1)
        
        try:
            ActionChains(driver).move_to_element(select_element).click().perform()
        except Exception:
            driver.execute_script("arguments[0].click();", select_element)
            
        time.sleep(1)
        print("✅ Select de búsqueda abierto")
        
        dropdown = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown') and not(contains(@style, 'display: none'))]"))
        )
        print("✅ Dropdown de búsqueda visible")
        
        try:
            ActionChains(driver).move_to_element(dropdown).perform()
        except Exception:
            pass
        time.sleep(1)
        
        opciones_dropdown = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'ant-select-dropdown') and not(contains(@style, 'display: none'))]//div[contains(@class,'ant-select-item-option-content')]"))
        )
        time.sleep(1)
        print("Opciones de búsqueda encontradas:")
        for opcion in opciones_dropdown:
            print(opcion.text)
        
        opcion_busqueda_encontrada = None
        for opcion in opciones_dropdown:
            if "Código de barras" in opcion.text or "codigo de barras" in opcion.text.lower() or "Buscar por Código" in opcion.text:
                opcion_busqueda_encontrada = opcion
                break

        if opcion_busqueda_encontrada:
            driver.execute_script("arguments[0].click();", opcion_busqueda_encontrada)
            print("✅ Opción de búsqueda 'Buscar por Código de barras' seleccionada")
            time.sleep(3)
            
            # Buscar el campo de entrada de texto (excluyendo inputs internos de ant-select)
            xpath_inputs_posibles = [
                "//div[contains(@class, 'ant-input-affix-wrapper')]//input",
                "//input[contains(@class, 'ant-input') and not(contains(@class, 'ant-select')) and not(@type='hidden')]",
                "//input[contains(@placeholder, 'BUSCAR') or contains(@placeholder, 'Buscar') or contains(@placeholder, 'buscar')]",
                "//input[not(@type='hidden') and not(contains(@class, 'ant-select-selection-search-input'))]"
            ]
            
            campo_busqueda = None
            for xp in xpath_inputs_posibles:
                inputs_found = driver.find_elements(By.XPATH, xp)
                for inp in inputs_found:
                    try:
                        if inp.is_displayed():
                            campo_busqueda = inp
                            break
                    except Exception:
                        pass
                if campo_busqueda:
                    break

            if not campo_busqueda:
                campo_busqueda = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-input-affix-wrapper')]//input")))

            print("✅ Campo de texto de búsqueda localizado")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_busqueda)
            time.sleep(1)
            
            try:
                campo_busqueda.click()
            except Exception:
                driver.execute_script("arguments[0].focus(); arguments[0].click();", campo_busqueda)
                
            time.sleep(1)
            
            try:
                actions = ActionChains(driver)
                actions.move_to_element(campo_busqueda).click().key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).send_keys(str(barcode_aleatorio)).perform()
            except Exception:
                campo_busqueda.send_keys(Keys.CONTROL + "a")
                campo_busqueda.send_keys(Keys.BACKSPACE)
                campo_busqueda.send_keys(str(barcode_aleatorio))
                
            time.sleep(2)
            campo_busqueda.send_keys(Keys.ENTER)
            print(f"✅ Búsqueda realizada con barcode: {barcode_aleatorio}")
            time.sleep(5)
            
            try:
                elemento = driver.find_element(By.XPATH, f"//*[contains(text(), '{nombre_producto}') or contains(text(), '{barcode_aleatorio}')]")
                print("✅ Producto encontrado en la tabla de resultados")
                observaciones = f"Producto creado con éxito. SKU: {sku_aleatorio}, Barcode: {barcode_aleatorio}"
                estado = "EXITOSO"
                registrar_resultado(id_caso, estado, observaciones)
            except Exception as e_verif:
                print(f"⚠️ No se pudo verificar el texto del producto en la tabla: {e_verif}")
                observaciones = f"Producto creado con éxito. SKU: {sku_aleatorio}, Barcode: {barcode_aleatorio}"
                estado = "EXITOSO"
                registrar_resultado(id_caso, estado, observaciones)
        else:
            print("❌ No se encontró la opción de búsqueda 'Buscar por Código de barras'")
            observaciones = "No se encontró la opción de búsqueda por Código de barras"
            estado = "FALLIDO"
            registrar_resultado(id_caso, estado, observaciones)
    except Exception as e:
        print(f"❌ Error al abrir el dropdown: {e}")
        observaciones = f"Error al abrir el dropdown: {e}"
        estado = "FALLIDO"
        registrar_resultado(id_caso, estado, observaciones)
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"❌ Error durante la ejecución: {str(e)}")
    observaciones = f"Error durante la ejecución: {str(e)}"
    estado = "FALLIDO"
    registrar_resultado(id_caso, estado, observaciones)