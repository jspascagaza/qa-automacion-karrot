from atexit import register
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

pregunta_atributos = "false"
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
    r"C:\Users\karrot\Documents\qa-automacion\automatizacion-karrot-a72723f4eafb.json",
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
# PRUEBA REGISTRO COMPLETO CON CONSULTOR Y VERIFICACIÓN
# =====================
id_caso = "TC025"

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
def manejar_confirmacion_precios():
    """
    Maneja la confirmación de actualización de precios/costos
    Retorna True si se manejó la confirmación, False si no apareció
    """
    try:
        # Buscar el mensaje de confirmación con un timeout corto
        confirmacion_wait = WebDriverWait(driver, 5)
        
        # Buscar el mensaje "Actualización de precios/costos"
        mensaje_confirmacion = confirmacion_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//strong[contains(text(), 'Actualización de precios/costos')]")
            )
        )
        
        if mensaje_confirmacion:
            print("⚠️ Apareció mensaje de confirmación de precios")
            
            # Buscar y hacer click en el botón "Sí"
            boton_si = confirmacion_wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-sm')]//span[text()='Sí']")
                )
            )
            boton_si.click()
            print("✅ Click en botón 'Sí' para confirmar actualización de precios")
            time.sleep(2)
            return True
    except Exception as e:
        print(f"❌ Error al manejar confirmación de precios: {e}")
        return False

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

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
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
except Exception as e:
        print(f"❌ Error inesperado {str(e)}")

def editar_producto_completo():
    try:

        elemento = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/section/div/main/div[2]/div[3]/div/div/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[1]/div/div[2]/span')))
        valor = elemento.text
        print(f"📖 Valor del elemento: '{valor}'")
        time.sleep(5)

        listar_opciones_producto = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div[3]/div/div/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[6]/div/button"))
        )
        listar_opciones_producto.click()
        print("✅ Click en los 3 puntos")
        time.sleep(5)

        editar_producto = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Editar producto']"))
        )
        editar_producto.click()
        print("✅ Click en Editar producto")
        time.sleep(10)

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

                # Generar SKU aleatorio y agregarlo al campo correspondiente
        sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        campo_sku = wait.until(EC.element_to_be_clickable((By.ID, f"advanced_search_{valor}sku")))
        valor_actual_sku = campo_sku.get_attribute("value")
        print(f"📖 Valor SKU actual del producto: '{valor_actual_sku}'")
        driver.execute_script("arguments[0].value = '';", campo_sku)
        campo_sku.send_keys(Keys.CONTROL + "a")
        campo_sku.send_keys(sku_aleatorio)
        print(f"✅ Valor SKU nuevo: '{sku_aleatorio}'")
        
        # Generar Barcode aleatorio y agregarlo al campo correspondiente
        barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        valor_barcode = barcode_aleatorio
        campo_barcode = wait.until(EC.element_to_be_clickable((By.ID, f"advanced_search_{valor}barcode")))
        valor_actual_barcode = campo_barcode.get_attribute("value")
        print(f"📖 Valor barcode actual del producto: '{valor_actual_barcode}'")
        driver.execute_script("arguments[0].value = '';", campo_barcode)
        campo_barcode.send_keys(Keys.CONTROL + "a")
        campo_barcode.send_keys(barcode_aleatorio)
        print(f"✅ Valor nuevo barcode: '{barcode_aleatorio}'")

        # Solicitar Valor de costo al usuario y agregarlo al campo correspondiente
        costo_aleatorio = precio
        valor_costo = costo_aleatorio            
        campo_costo = wait.until(EC.element_to_be_clickable((By.ID, f"advanced_search_{valor}cost")))
        valor_actual_cost = campo_costo.get_attribute("value")
        print(f"📖 Valor barcode actual del producto: '{valor_actual_cost}'")
        driver.execute_script("arguments[0].value = '';", campo_costo)
        campo_costo.send_keys(Keys.CONTROL + "a")
        campo_costo.send_keys(valor_costo)
        print(f"✅ Costo para el producto: '{costo_aleatorio}'")
        
        return valor_barcode, sku_aleatorio, valor_costo, valor_actual_sku, valor_actual_barcode, valor_actual_cost,valor

    except Exception as e:
        print(f"❌ Error al editar el producto: {str(e)}")

# Para usar la función simplemente llamas:
valor_barcode, sku_aleatorio, valor_costo, valor_actual_sku, valor_actual_barcode, valor_actual_cost,valor =  editar_producto_completo()

boton_guardar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='advanced_search']/div[1]/div/div/div/button[2]")))
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_guardar)
boton_guardar.click()
print("✅ Click en Guardar")
time.sleep(3)
manejar_confirmacion_precios()

time.sleep(3)

listar_opciones_producto = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div[3]/div/div/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[6]/div/button"))
        )
listar_opciones_producto.click()
print("✅ Click en los 3 puntos")
time.sleep(5)

editar_producto = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Editar producto']"))
    )
editar_producto.click()
print("✅ Click en Editar producto")
time.sleep(10)

campo_sku = wait.until(EC.element_to_be_clickable((By.ID, f"advanced_search_{valor}sku")))
valor_actualizado_sku = campo_sku.get_attribute("value")

campo_barcode = wait.until(EC.element_to_be_clickable((By.ID, f"advanced_search_{valor}barcode")))
valor_actualizado_barcode = campo_barcode.get_attribute("value")

campo_costo = wait.until(EC.element_to_be_clickable((By.ID, f"advanced_search_{valor}cost")))
valor_actualizado_cost = campo_costo.get_attribute("value")
valor_actualizado_cost_string = valor_actualizado_cost.replace('$', '').replace('.', '').replace(',', '').replace(' ', '').strip()
valor_actualizado_cost_int = int(valor_actualizado_cost_string)

if sku_aleatorio == valor_actualizado_sku and valor_barcode == valor_actualizado_barcode and valor_costo == valor_actualizado_cost_int:
    observaciones = ("CAMPOS ACTUALIZADOS CORRECTAMENTE " + "Estos son los valores anteriores " + " barcode anterior: " + valor_actual_barcode + " sku anterior: " + valor_actual_sku + " costo anterior: " + valor_actual_cost
    + " Estos son los valores anteriores " + " barcode nuevo: " + valor_actualizado_barcode + " sku nuevo: " + valor_actualizado_sku + " costo nuevo: " + valor_actualizado_cost)
    estado = "EXITOSO"
    print ("Estos son los valores anteriores" + " barcode anterior: " + valor_actual_barcode + " sku anterior: " + valor_actual_sku + " costo anterior: " + valor_actual_cost)
    print ("Estos son los valores anteriores" + " barcode nuevo: " + valor_actualizado_barcode + " sku nuevo: " + valor_actualizado_sku + " costo nuevo: " + valor_actualizado_cost)
    registrar_resultado(id_caso, estado, observaciones)
else:
    campos_fallidos = []
    if sku_aleatorio != valor_actualizado_sku:
        campos_fallidos.append("SKU")
    if valor_actualizado_barcode != valor_barcode:
        campos_fallidos.append("BARCODE")
    if valor_actualizado_cost_string != valor_costo:
        campos_fallidos.append("COST")
    observaciones = f"CAMPOS NO ACTUALIZADOS: {', '.join(campos_fallidos)}"
    estado = "FALLIDO"
    print (observaciones)
    registrar_resultado(id_caso, estado, observaciones)