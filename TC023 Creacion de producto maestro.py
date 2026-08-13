import csv
import datetime
from socket import timeout
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
from datetime import datetime

if not os.path.exists("logs"):
    os.makedirs("logs")

nombre_archivo = "TC023_Maestro"
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

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import string
from faker import Faker
import faker_commerce
import subprocess

fake = Faker('es_CO')
try:
    fake.add_provider(faker_commerce.Provider)
except Exception as e:
    print("⚠️ No se pudo añadir faker_commerce.Provider:", e)

# =====================
# CONFIGURACIÓN GOOGLE SHEETS
# =====================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    os.getenv("GOOGLE_CREDENTIALS_PATH", "automatizacion-karrot-11b5a5de79c5.json"),
    scope
)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(
    os.getenv("SPREADSHEET_URL", "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0")
)
sheet = spreadsheet.sheet1

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


import json

def generar_datos_producto():
    nombres_catalogo = []
    ruta_json = os.path.join(os.path.dirname(__file__), "nombres_productos.json")
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, "r", encoding="utf-8") as f:
                data_cat = json.load(f)
                for cat, prods in data_cat.items():
                    nombres_catalogo.extend(prods)
        except Exception as e:
            print("⚠️ Error al leer nombres_productos.json:", e)

    if not nombres_catalogo:
        nombres_catalogo = [
            "Samsung Galaxy S24", "iPhone 15 Pro", "Xiaomi Redmi Note 13", "Motorola Edge 40",
            "Televisor Smart TV 55", "Laptop HP Pavilion 15", "Laptop Lenovo IdeaPad 3",
            "Audífonos Inalámbricos Bluetooth", "Camisa Casual Manga Larga", "Zapatos Deportivos",
            "Arroz Roa 1kg", "Aceite Gourmet 1L", "Café Sello Rojo 500g", "Leche Alquería 1L",
            "Jabón Líquido Rey 500ml", "Detergente Multiusos 1kg", "Galletas Festival Pack",
            "Agua Mineral 600ml", "Gaseosa Coca-Cola 1.5L", "Atún Van Camp's 160g"
        ]

    nombre_producto = random.choice(nombres_catalogo)

    if hasattr(fake, 'ecommerce_description'):
        descripcion = fake.ecommerce_description()
    elif hasattr(fake, 'commerce_description'):
        descripcion = fake.commerce_description()
    elif hasattr(fake, 'product_description'):
        descripcion = fake.product_description()
    else:
        descripcion = fake.sentence(nb_words=15)

    if hasattr(fake, 'ecommerce_price'):
        precio = fake.ecommerce_price()
    elif hasattr(fake, 'commerce_price'):
        precio = fake.commerce_price()
    elif hasattr(fake, 'commerce_price_in_cents'):
        precio = fake.commerce_price_in_cents()
    else:
        precio = round(random.uniform(400_000, 8_000_000), 2)
        
    return nombre_producto, descripcion, precio

def ejecutar_caso(config_caso):
    id_caso = config_caso["id_caso"]
    activar_atributos = config_caso["atributos"]
    es_perecedero = config_caso["perecedero"]
    nombre_caso = config_caso["nombre_caso"]
    
    print("\n" + "="*60)
    print(f"🚀 INICIANDO EJECUCIÓN DE: {nombre_caso} ({id_caso})")
    print(f"👉 Atributos: {'Sí' if activar_atributos else 'No'}")
    print(f"👉 Perecedero: {'Sí' if es_perecedero else 'No'}")
    print("="*60)
    
    nombre_producto, descripcion, precio = generar_datos_producto()
    print (f"🛒 Nombre del producto generado: {nombre_producto}")
    print(f"💰 Precio del producto generado: {precio}")
    
    estado = "FALLIDO"
    observaciones = ""
    driver = None
    try:
        chrome_options = Options()
        # Configuración para Jenkins o ejecución sin interfaz (Headless)
        if os.getenv("JENKINS_URL") or os.getenv("CI") or os.getenv("HEADLESS") == "true":
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
        driver = webdriver.Chrome(options=chrome_options)
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

        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button"))
        )
        login_button.click()
        time.sleep(15)

        # Menú Catálogo
        catalogo = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Catálogo']"))
        )
        catalogo.click()
        print("✅ Click en Catálogo")
        time.sleep(5)

        productos_servicios = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Productos y Servicios']"))
        )
        productos_servicios.click()
        print("✅ Click en Productos y Servicios")
        time.sleep(10)

        # Agregar Artículo
        boton_agregar = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div[2]/div/div/div/div[1]/div/button[1]")))
        boton_agregar.click()
        print("✅ Click en Agregar Artículo")
        time.sleep(10)

        # Verificar texto "Añadir nuevo producto"
        elemento = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='advanced_search']/div[1]/div[1]/div/div[1]/h1"))
        )
        print("Texto encontrado:", elemento.text)
        time.sleep(2)

        # Selección tipo de producto
        radio_producto = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Product']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_producto)
        driver.execute_script("arguments[0].click();", radio_producto)
        print("Producto seleccionado")
        time.sleep(2)

        # Nombre del producto
        input_nombre_producto = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='advanced_search_name']"))
        )
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
        opcion_encontrada = None
        for opcion in opciones_categorias:
            if opcion.text.strip():
                opcion_encontrada = opcion
                break
        
        if opcion_encontrada:
            opcion_encontrada.click()
            print("✅ Categoría seleccionada")
        else:
            print(f"❌ No se encontró la categorías")

        # Selección de unidad (tipo de unidad)
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

        opcion_unidad_encontrada = None
        for opcion in opciones_unidad:
            if opcion.text.strip() == "Cantidad / Unidades":
                opcion_unidad_encontrada = opcion
                break
        if opcion_unidad_encontrada:
            opcion_unidad_encontrada.click()
            print("✅ Unidad 'Cantidad / Unidades' seleccionada")
        
        inputs = driver.find_elements(By.CLASS_NAME, "ant-select-selection-search-input")
        if not inputs:
            raise Exception("No se encontraron inputs 'ant-select-selection-search-input'")
        index = 2 if len(inputs) > 2 else len(inputs) - 1
        imput_unidad = inputs[index]
        imput_unidad.click()    
        time.sleep(1)

        opciones_unidad_2 = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-option-content')]"))
        )

        opcion_unidad_encontrada_2 = None
        for opcion in opciones_unidad_2:
            if opcion.text.strip() == "Unidad (u)":
                opcion_unidad_encontrada_2 = opcion
                break
        if opcion_unidad_encontrada_2:
            opcion_unidad_encontrada_2.click()
            print("✅ Unidad 'Unidad' seleccionada")

        # Descripción del producto
        descripcionproducto = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='advanced_search_description']")))
        descripcionproducto.send_keys(descripcion)
        time.sleep(2)
        
        # Configurar producto perecedero
        try:
            switch_xpath = "//button[@role='switch' and contains(@class, 'ant-switch')]"
            switch_btn = wait.until(EC.element_to_be_clickable((By.XPATH, switch_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch_btn)
            time.sleep(0.5)
            is_currently_checked = switch_btn.get_attribute("aria-checked") == "true"
            if es_perecedero and not is_currently_checked:
                switch_btn.click()
                print("✅ Switch ACTIVADO (Producto perecedero)")
            elif not es_perecedero and is_currently_checked:
                switch_btn.click()
                print("✅ Switch DESACTIVADO (Producto no perecedero)")
        except Exception as e:
            print(f"❌ Error al configurar el switch: {e}")

        time.sleep(2)
        
        barcode_aleatorio = None
        sku_aleatorio = None
        
        # Manejar atributos adicionales
        if activar_atributos:
            try:
                boton_xpath = "//*[@id='advanced_search']/div[2]/div/div[1]/div/div[3]/div/div/button"
                boton = wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
                time.sleep(0.5)
                boton.click()
                
                nombre_atributo = "memoria"
                input_nombre_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_attributeName")))
                input_nombre_atributo.send_keys(nombre_atributo)

                valores_atributos = []
                valor1 = "1tb"
                input_valor_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_option1")))
                input_valor_atributo.send_keys(valor1)
                valores_atributos.append(valor1)
                time.sleep(1)
                
                valor2 = "2tb"
                input_valor_atributo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_option2")))
                input_valor_atributo.send_keys(valor2)
                valores_atributos.append(valor2)
                time.sleep(1)
                
                boton_ok = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-btn-primary') and (.//span[text()='OK'] or .//span[text()='Aceptar'])]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_ok)
                time.sleep(0.5)
                try:
                    boton_ok.click()
                except:
                    driver.execute_script("arguments[0].click();", boton_ok)
                print("✅ Atributos adicionales configurados")
                time.sleep(2)
                
                # Generar campos por atributo
                for valor_atributo in valores_atributos:
                    id_base = f"advanced_search_{valor_atributo}"
                    
                    sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
                    try:
                        campo_sku = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}sku")))
                    except:
                        campo_sku = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@class, 'sku')]")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo_sku)
                    time.sleep(0.5)
                    campo_sku.clear()
                    campo_sku.send_keys(sku_aleatorio)
                    
                    barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                    try:
                        campo_barcode = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}barcode")))
                    except:
                        campo_barcode = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@class, 'barcode')]")))
                    campo_barcode.clear()
                    campo_barcode.send_keys(barcode_aleatorio)

                    valor_costo = precio            
                    try:
                        campo_costo = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}cost")))
                    except:
                        campo_costo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@id, 'cost')]")))
                    campo_costo.clear()
                    campo_costo.send_keys(valor_costo)

                    valor_precio = precio            
                    try:
                        campo_precio = wait.until(EC.element_to_be_clickable((By.ID, f"{id_base}price")))
                    except:
                        campo_precio = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@id, '{valor_atributo}') and contains(@id, 'price')]")))
                    campo_precio.clear()
                    campo_precio.send_keys(valor_precio)
                    time.sleep(1)
            except Exception as e:
                print(f"❌ Error al generar campos para atributos: {e}")
        else:
            # Si no activa atributos, rellenar undefinedsku, undefinedbarcode, etc
            sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            campo_sku = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedsku")))
            campo_sku.clear()
            campo_sku.send_keys(sku_aleatorio)
            
            barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            campo_barcode = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedbarcode")))
            campo_barcode.clear()
            campo_barcode.send_keys(barcode_aleatorio)

            valor_costo = precio            
            campo_costo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedcost")))
            campo_costo.clear()
            campo_costo.send_keys(valor_costo)

            valor_precio = precio
            campo_precio = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedprice")))
            campo_precio.clear()
            campo_precio.send_keys(valor_precio)

        print(f"✅ Barcode final: {barcode_aleatorio}, SKU final: {sku_aleatorio}")
        
        boton_anadir = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type=\'submit\' and contains(@class, \'ant-btn-primary\')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
        boton_anadir.click()
        print("✅ Click en Añadir")
        
        # Verificar si aparece un mensaje de error (ej. el producto ya existe)
        try:
            mensaje = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-message-notice-content') or contains(@class, 'ant-notification-notice')]"))
            )
            texto_mensaje = mensaje.text.lower()
            print(f"ℹ️ Mensaje en pantalla: {mensaje.text}")
            
            # Si el mensaje indica error o que el producto ya existe
            if "error" in texto_mensaje or "exist" in texto_mensaje or "ya" in texto_mensaje or "fail" in texto_mensaje:
                print("🔄 El producto ya existe o hubo un error. Reintentando caso...")
                driver.quit()
                return ejecutar_caso(config_caso)
        except TimeoutException:
            # Si no hay mensaje o no pudimos capturarlo, esperamos un poco más
            time.sleep(5)
            pass
            
        time.sleep(5)
        driver.refresh()
        time.sleep(5)
        
        # BUSQUEDA FINAL
        select_xpath = "//div[contains(@class, 'ant-select') and (span[contains(@title, 'Buscar por')] or .//span[contains(text(), 'Buscar por')])]"
        try:
            select_element = wait.until(EC.element_to_be_clickable((By.XPATH, select_xpath)))
        except TimeoutException:
            select_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select') and .//input[@type='search']]")))
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_element)
        try:
            # Intentar click sobre el selector interno de Ant Design si está presente
            selector_inner = select_element.find_element(By.XPATH, ".//div[contains(@class, 'ant-select-selector')]")
            selector_inner.click()
        except Exception:
            try:
                ActionChains(driver).move_to_element(select_element).click().perform()
            except Exception:
                driver.execute_script("arguments[0].click();", select_element)
        time.sleep(1)
        
        dropdown = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]")),
            message="No se encontró el menú desplegable (ant-select-dropdown) visible"
        )
        ActionChains(driver).move_to_element(dropdown).perform()
        time.sleep(1)
        
        opciones_dropdown = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]//div[contains(@class,'ant-select-item-option-content')]")),
            message="No se encontraron las opciones del menú desplegable"
        )
        
        opcion_busqueda_encontrada = None
        for opcion in opciones_dropdown:
            texto_opcion = opcion.text.strip().lower()
            if "código de barras" in texto_opcion or "codigo de barras" in texto_opcion:
                opcion_busqueda_encontrada = opcion
                break
        
        if opcion_busqueda_encontrada:
            opcion_busqueda_encontrada.click()
            time.sleep(5)
            campo_busqueda = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@role='combobox' and @type='search' and contains(@class, 'ant-input')]")),
                message="No se encontró el campo de búsqueda de código de barras"
            )
            campo_busqueda.clear()
            campo_busqueda.send_keys(barcode_aleatorio)
            time.sleep(5)
            campo_busqueda.send_keys(Keys.CONTROL + "a")
            campo_busqueda.send_keys(barcode_aleatorio)    
            campo_busqueda.send_keys(Keys.ARROW_DOWN)
            time.sleep(2)
            campo_busqueda.send_keys(Keys.ENTER)
            print(f"✅ Búsqueda realizada con : {barcode_aleatorio}")
            time.sleep(5)
            try:
                elemento = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{nombre_producto}')]")))
                print("✅ campo encontrado enviado en campo de búsqueda")
                time.sleep(5)
                observaciones = f"Producto creado con éxito. SKU: {sku_aleatorio}, Barcode: {barcode_aleatorio}"
                estado = "EXITOSO"
            except TimeoutException:
                print(f"❌ No se encontró el producto {nombre_producto} en la tabla")
                observaciones = f"Producto no encontrado tras la búsqueda. SKU: {sku_aleatorio}, Barcode: {barcode_aleatorio}"
                estado = "FALLIDO"
        else:
            print("❌ No se encontró la opción de búsqueda 'Buscar por Código de barras'")
            observaciones = "No se encontró la opción de búsqueda 'Buscar por Código de barras'"
            estado = "FALLIDO"

        registrar_resultado(id_caso, estado, observaciones)

    except Exception as e:
        msg = str(e).strip() or f"Excepción de tipo {type(e).__name__} (Timeout / Elemento no encontrado)"
        print(f"❌ Error durante la ejecución del caso {id_caso}: {msg}")
        observaciones = f"Error durante la ejecución ({type(e).__name__}): {msg}"
        estado = "FALLIDO"
        registrar_resultado(id_caso, estado, observaciones)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Definición de todos los casos TC023 a ejecutar
    casos_a_ejecutar = [
        {"id_caso": "TC023-001", "atributos": True, "perecedero": False, "nombre_caso": "Creacion exitosa con atributos"},
        {"id_caso": "TC023-002", "atributos": False, "perecedero": False, "nombre_caso": "Creacion exitosa sin atributos"},
        {"id_caso": "TC023-003", "atributos": True, "perecedero": True, "nombre_caso": "Creacion exitosa con atributos y producto perecedero"},
        {"id_caso": "TC023-004", "atributos": False, "perecedero": True, "nombre_caso": "Creacion exitosa sin atributos y perecedero"}
    ]
    
    print("="*60)
    print("🚀 INICIANDO EJECUCIÓN MAESTRA DE TODOS LOS CASOS TC023")
    print("="*60)
    
    for caso in casos_a_ejecutar:
        ejecutar_caso(caso)
        time.sleep(5)  # Pequeña pausa entre casos para evitar problemas de caché o cierres bruscos
        
    print("\n✅ TODAS LAS EJECUCIONES HAN TERMINADO.")
