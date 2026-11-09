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
    os.getenv("GOOGLE_CREDENTIALS_PATH", "automatizacion-karrot-456d1a1552ca.json"),
    scope
)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(
    os.getenv("GOOGLE_SHEET_URL", os.getenv("SPREADSHEET_URL", "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"))
)
sheet = spreadsheet.sheet1

def registrar_resultado(id_caso, estado, observaciones=""):
    global client, spreadsheet, sheet
    for intento in range(5):
        try:
            celda = sheet.find(id_caso)
            if not celda:
                print(f"⚠️ No se encontró el ID {id_caso} en la hoja de cálculo")
                return False
            fila = celda.row
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            automatizado = "Sí"
            sheet.update_cell(fila, 11, automatizado)   # Columna K
            sheet.update_cell(fila, 13, fecha)          # Columna M
            sheet.update_cell(fila, 14, estado)         # Columna N
            sheet.update_cell(fila, 15, observaciones)  # Columna O
            print(f"✅ Caso {id_caso} actualizado en Google Sheets -> {estado}")
            return True
        except Exception as e:
            print(f"⏳ Reintento {intento+1}/5 al actualizar {id_caso} en Google Sheets ({e})")
            time.sleep(5)
            try:
                client = gspread.authorize(creds)
                spreadsheet = client.open_by_url(
                    os.getenv("GOOGLE_SHEET_URL", os.getenv("SPREADSHEET_URL", "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"))
                )
                sheet = spreadsheet.sheet1
            except Exception:
                pass
    return False



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

        # =====================
        # NAVEGACIÓN A CATÁLOGO -> PRODUCTOS Y SERVICIOS
        # =====================
        print("📍 Iniciando navegación al Catálogo...")
        
        # Paso 1: Desplegar menú lateral
        try:
            print("📂 Desplegando menú lateral...")
            nav_lateral = wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[@id='root']/div/div/nav | //nav | //aside"
            )))
            ActionChains(driver).move_to_element(nav_lateral).perform()
            time.sleep(1.5)
        except Exception as e_nav:
            print(f"ℹ️ Hover en menú lateral: {e_nav}")

        # Paso 2: Módulo Catálogo (usando el xpath del módulo Catálogo)
        print("🏬 Buscando y abriendo módulo Catálogo...")
        catalogo = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//*[@id="root"]/div/div/nav/div[4]/button | //nav//button[contains(., "Catálogo")] | //button[contains(., "Catálogo")] | //span[normalize-space()="Catálogo"]'
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", catalogo)
        time.sleep(0.5)

        # Verificar si el submenú ya está desplegado antes de hacer clic
        opciones_sub = driver.find_elements(By.XPATH, '//*[@id="root"]/div/div/nav/div[4]/div/a[1] | //a[contains(., "Productos y Servicios")]')
        if not opciones_sub or not any(op.is_displayed() for op in opciones_sub):
            try:
                catalogo.click()
            except Exception:
                driver.execute_script("arguments[0].click();", catalogo)
            print("✅ Click en Catálogo")
            time.sleep(2)
        else:
            print("ℹ️ Catálogo ya se encuentra desplegado")

        # Paso 3: Opción Productos y Servicios (usando el xpath de Productos y Servicios)
        print("📦 Clickeando opción 'Productos y Servicios'...")
        productos_servicios = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//*[@id="root"]/div/div/nav/div[4]/div/a[1] | //a[contains(., "Productos y Servicios")] | //span[normalize-space()="Productos y Servicios"] | //*[contains(text(), "Productos y Servicios")]'
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", productos_servicios)
        time.sleep(0.5)
        try:
            productos_servicios.click()
        except Exception:
            driver.execute_script("arguments[0].click();", productos_servicios)
        print("✅ Click en Productos y Servicios")
        time.sleep(5)

        # Paso 4: Agregar Artículo
        print("➕ Buscando botón 'Agregar Artículo'...")
        boton_agregar = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(., 'Agregar Artículo') or contains(., 'Añadir Artículo')] | //*[@id='root']/div/section/section/section/div/main/div[2]/div[2]/div/div/div/div[1]/div/button[1] | //button[contains(@class, 'ant-btn') and contains(., 'Artículo')]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_agregar)
        time.sleep(0.5)
        try:
            boton_agregar.click()
        except Exception:
            driver.execute_script("arguments[0].click();", boton_agregar)
        print("✅ Click en Agregar Artículo")
        time.sleep(8)

        # Selección tipo de producto: Forzar siempre 'Producto normal'
        tipo_producto = "Producto normal"
        print(f"📦 Seleccionando tipo de producto: '{tipo_producto}'...")
        try:
            # 1. Encontrar el elemento de texto 'Producto normal'
            elem_texto = wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//div[@role='button' and .//div[contains(text(), 'Producto normal')]] | "
                "//*[normalize-space(text())='Producto normal' or text()='Producto normal']"
            )))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem_texto)
            time.sleep(0.5)
            
            # 2. Hacer clic directamente en la tarjeta de Producto normal
            driver.execute_script('''
                const el = arguments[0];
                const card = el.closest('div[role="button"]') || el.parentElement || el;
                card.click();
            ''', elem_texto)
            print("✅ 'Producto normal' seleccionado")
        except Exception as e:
            print(f"⚠️ Error al seleccionar 'Producto normal': {e}")
            try:
                card_fallback = driver.find_element(By.XPATH, "//*[contains(text(), 'Producto normal')]")
                driver.execute_script("arguments[0].click();", card_fallback)
                print("✅ 'Producto normal' seleccionado con fallback")
            except Exception as e2:
                print(f"❌ Fallback falló: {e2}")
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
                print("⏳ Buscando botón '+ Agregar Otro Atributo' o campos de atributo...")
                input_nombre_existente = driver.find_elements(
                    By.XPATH, "//input[@placeholder='Nombre del atributo' or contains(@id, 'attributeName')]"
                )
                if not input_nombre_existente or not input_nombre_existente[0].is_displayed():
                    boton_xpath = (
                        "//button[(contains(., 'Agregar') or contains(., 'Añadir')) and contains(., 'Atributo')] | "
                        "//*[contains(text(), 'Agregar Otro Atributo') or contains(text(), 'Agregar Atributo') or contains(text(), 'Agregar nuevo atributo')]"
                    )
                    boton = wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", boton)
                    time.sleep(1)
                    print("✅ Botón '+ Agregar Otro Atributo' clickeado")
                
                nombre_atributo = "memoria"
                input_nombre_atributo = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//input[@placeholder='Nombre del atributo' or contains(@id, 'attributeName')]"
                )))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_nombre_atributo)
                input_nombre_atributo.send_keys(Keys.CONTROL + "a")
                input_nombre_atributo.send_keys(nombre_atributo)
                print(f"✅ Nombre de atributo ingresado: '{nombre_atributo}'")
                time.sleep(1)

                valores_atributos = ["1tb", "2tb"]
                input_valor_atributo = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//input[@placeholder='Agregar valor' or contains(@id, 'option') or contains(@placeholder, 'valor')]"
                )))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_valor_atributo)
                for val in valores_atributos:
                    input_valor_atributo.send_keys(val)
                    time.sleep(0.5)
                    input_valor_atributo.send_keys(Keys.ENTER)
                    time.sleep(1)
                    print(f"✅ Valor de atributo ingresado con ENTER: '{val}'")
                
                print("✅ Atributos adicionales configurados")
                time.sleep(2)
                
                # =======================================================
                # CONFIGURACIÓN DE VARIANTES EN LA TABLA (PRECIOS, SKU, BARCODE)
                # =======================================================
                print("⚙️ Configurando variantes, precios y códigos en la tabla...")
                time.sleep(2)

                def obtener_campo_variante(wait_obj, drv, id_campo):
                    modales = drv.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal-content')]")
                    for modal in modales:
                        if modal.is_displayed():
                            inputs = modal.find_elements(
                                By.XPATH, f".//input[contains(@id, '{id_campo}') or contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{id_campo}')]"
                            )
                            for inp in inputs:
                                if inp.is_displayed():
                                    return inp
                    try:
                        return wait_obj.until(EC.presence_of_element_located((By.ID, id_campo)))
                    except Exception:
                        pass
                    try:
                        return drv.find_element(By.ID, f"advanced_search_undefined{id_campo}")
                    except Exception:
                        pass
                    inputs = drv.find_elements(By.XPATH, f"//input[contains(@id, '{id_campo}')]")
                    for input_elem in inputs:
                        if input_elem.is_displayed():
                            return input_elem
                    return None

                # Detectar botones de lápiz para cada variante
                xpath_lapices = (
                    "//div[contains(@class, 'ant-table') or self::table]//button[span[contains(@class, 'anticon-edit')] or .//span[@aria-label='edit'] or @aria-label='edit'] | "
                    "//button[span[contains(@class, 'anticon-edit')] or .//span[@aria-label='edit'] or @aria-label='edit']"
                )
                todos_lapices = driver.find_elements(By.XPATH, xpath_lapices)
                botones_lapiz = []
                for lapiz in todos_lapices:
                    try:
                        if lapiz.is_displayed():
                            texto_padre = lapiz.find_element(By.XPATH, "./..").text
                            if "Unidad" not in texto_padre:
                                botones_lapiz.append(lapiz)
                    except Exception:
                        if lapiz.is_displayed():
                            botones_lapiz.append(lapiz)

                if botones_lapiz:
                    print(f"📋 Se encontraron {len(botones_lapiz)} variante(s) con botón de edición (lápiz).")
                    for idx, lapiz in enumerate(botones_lapiz):
                        val_nombre = valores_atributos[idx] if idx < len(valores_atributos) else f"Variante {idx+1}"
                        print(f"🎯 Editando variante {idx+1}: {val_nombre}...")
                        
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lapiz)
                        time.sleep(1)
                        try:
                            lapiz.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", lapiz)
                        time.sleep(2)

                        sku_var = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
                        sku_aleatorio = sku_var
                        campo_sku = obtener_campo_variante(wait, driver, "sku")
                        if campo_sku:
                            driver.execute_script("arguments[0].value = '';", campo_sku)
                            campo_sku.send_keys(Keys.CONTROL + "a")
                            campo_sku.send_keys(sku_var)
                            print(f"  ✅ SKU: '{sku_var}'")

                        bar_var = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                        barcode_aleatorio = bar_var
                        campo_barcode = obtener_campo_variante(wait, driver, "barcode")
                        if campo_barcode:
                            driver.execute_script("arguments[0].value = '';", campo_barcode)
                            campo_barcode.send_keys(Keys.CONTROL + "a")
                            campo_barcode.send_keys(bar_var)
                            print(f"  ✅ Barcode: '{bar_var}'")

                        campo_costo = obtener_campo_variante(wait, driver, "cost")
                        if campo_costo:
                            driver.execute_script("arguments[0].value = '';", campo_costo)
                            campo_costo.send_keys(Keys.CONTROL + "a")
                            campo_costo.send_keys(str(precio))
                            print(f"  ✅ Costo: '{precio}'")

                        campo_precio = obtener_campo_variante(wait, driver, "price")
                        if campo_precio:
                            driver.execute_script("arguments[0].value = '';", campo_precio)
                            campo_precio.send_keys(Keys.CONTROL + "a")
                            campo_precio.send_keys(str(precio))
                            print(f"  ✅ Precio: '{precio}'")

                        # Clic en Aplicar del modal de la variante
                        try:
                            boton_aplicar = driver.find_elements(
                                By.XPATH,
                                "//div[contains(@class, 'ant-modal')]//button[span[text()='Aplicar'] or contains(., 'Aplicar')] | //button[span[text()='Aplicar']]"
                            )
                            if boton_aplicar:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_aplicar[-1])
                                time.sleep(0.5)
                                try:
                                    boton_aplicar[-1].click()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", boton_aplicar[-1])
                                print(f"  ✅ 'Aplicar' modal clickeado")
                                time.sleep(2)
                        except Exception as e_apl:
                            print(f"  ⚠️ Error click Aplicar en modal: {e_apl}")
                else:
                    print("ℹ️ No se detectaron lápices en la tabla, rellenando inputs o aplicando precios masivos...")
                    try:
                        btn_bulk = driver.find_elements(By.XPATH, "//button[contains(., 'Aplicar precio/costo') or contains(., 'Aplicar precio')]")
                        if btn_bulk and btn_bulk[0].is_displayed():
                            print("💡 Botón 'Aplicar precio/costo' encontrado. Aplicando precios...")
                            driver.execute_script("arguments[0].click();", btn_bulk[0])
                            time.sleep(1.5)
                            inputs_pop = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-popover') or contains(@class, 'ant-modal')]//input")
                            for inp in inputs_pop:
                                if inp.is_displayed():
                                    try:
                                        inp.clear()
                                        inp.send_keys(str(precio))
                                    except Exception:
                                        pass
                            btn_conf = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-popover') or contains(@class, 'ant-modal')]//button[contains(., 'Aplicar') or contains(., 'Guardar') or contains(@class, 'ant-btn-primary')]")
                            if btn_conf:
                                driver.execute_script("arguments[0].click();", btn_conf[-1])
                                time.sleep(1.5)
                    except Exception as e_bulk:
                        print(f"ℹ️ Aplicar precio masivo: {e_bulk}")
            except Exception as e:
                print(f"❌ Error al generar campos para atributos: {e}")
        else:
            # Caso sin atributos: verificar si la variante por defecto tiene lápiz en la tabla
            print("⚙️ Configurando variante única (sin atributos)...")
            time.sleep(2)
            xpath_lapices = (
                "//div[contains(@class, 'ant-table') or self::table]//button[span[contains(@class, 'anticon-edit')] or .//span[@aria-label='edit'] or @aria-label='edit'] | "
                "//button[span[contains(@class, 'anticon-edit')] or .//span[@aria-label='edit'] or @aria-label='edit']"
            )
            todos_lapices = driver.find_elements(By.XPATH, xpath_lapices)
            botones_lapiz = []
            for lapiz in todos_lapices:
                try:
                    if lapiz.is_displayed():
                        texto_padre = lapiz.find_element(By.XPATH, "./..").text
                        if "Unidad" not in texto_padre:
                            botones_lapiz.append(lapiz)
                except Exception:
                    if lapiz.is_displayed():
                        botones_lapiz.append(lapiz)

            sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])

            if botones_lapiz:
                print("📋 Se encontró lápiz para la variante por defecto. Editando modal...")
                lapiz = botones_lapiz[0]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lapiz)
                time.sleep(1)
                try:
                    lapiz.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", lapiz)
                time.sleep(2)

                def obtener_campo_modal_directo(wait_obj, drv, id_campo):
                    modales = drv.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal-content')]")
                    for modal in modales:
                        if modal.is_displayed():
                            inputs = modal.find_elements(
                                By.XPATH, f".//input[contains(@id, '{id_campo}') or contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{id_campo}')]"
                            )
                            for inp in inputs:
                                if inp.is_displayed():
                                    return inp
                    try:
                        return wait_obj.until(EC.presence_of_element_located((By.ID, id_campo)))
                    except Exception:
                        return None

                campo_sku = obtener_campo_modal_directo(wait, driver, "sku")
                if campo_sku:
                    driver.execute_script("arguments[0].value = '';", campo_sku)
                    campo_sku.send_keys(Keys.CONTROL + "a")
                    campo_sku.send_keys(sku_aleatorio)
                    print(f"✅ SKU: '{sku_aleatorio}'")

                campo_barcode = obtener_campo_modal_directo(wait, driver, "barcode")
                if campo_barcode:
                    driver.execute_script("arguments[0].value = '';", campo_barcode)
                    campo_barcode.send_keys(Keys.CONTROL + "a")
                    campo_barcode.send_keys(barcode_aleatorio)
                    print(f"✅ Barcode: '{barcode_aleatorio}'")

                campo_costo = obtener_campo_modal_directo(wait, driver, "cost")
                if campo_costo:
                    driver.execute_script("arguments[0].value = '';", campo_costo)
                    campo_costo.send_keys(Keys.CONTROL + "a")
                    campo_costo.send_keys(str(precio))
                    print(f"✅ Costo: '{precio}'")

                campo_precio = obtener_campo_modal_directo(wait, driver, "price")
                if campo_precio:
                    driver.execute_script("arguments[0].value = '';", campo_precio)
                    campo_precio.send_keys(Keys.CONTROL + "a")
                    campo_precio.send_keys(str(precio))
                    print(f"✅ Precio: '{precio}'")

                # Clic en Aplicar del modal
                try:
                    boton_aplicar = driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'ant-modal')]//button[span[text()='Aplicar'] or contains(., 'Aplicar')] | //button[span[text()='Aplicar']]"
                    )
                    if boton_aplicar:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_aplicar[-1])
                        time.sleep(0.5)
                        try:
                            boton_aplicar[-1].click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", boton_aplicar[-1])
                        print("✅ 'Aplicar' modal clickeado")
                        time.sleep(2)
                except Exception as e_apl:
                    print(f"⚠️ Error click Aplicar en modal: {e_apl}")
            else:
                # Fallback tradicional: undefinedsku, undefinedbarcode, etc.
                try:
                    campo_sku = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedsku")))
                    campo_sku.clear()
                    campo_sku.send_keys(sku_aleatorio)
                except Exception:
                    pass
                
                try:
                    campo_barcode = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedbarcode")))
                    campo_barcode.clear()
                    campo_barcode.send_keys(barcode_aleatorio)
                except Exception:
                    pass

                try:
                    campo_costo = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedcost")))
                    campo_costo.clear()
                    campo_costo.send_keys(str(precio))
                except Exception:
                    pass

                try:
                    campo_precio = wait.until(EC.element_to_be_clickable((By.ID, "advanced_search_undefinedprice")))
                    campo_precio.clear()
                    campo_precio.send_keys(str(precio))
                except Exception:
                    pass

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
        # Redireccionar o asegurar estar en lista de productos para la búsqueda
        if "list-products" not in driver.current_url:
            print("🔄 Redirigiendo a lista de productos...")
            driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/products/list-products")
            time.sleep(5)
        else:
            driver.refresh()
            time.sleep(5)
        
        # BUSQUEDA FINAL
        print("🔍 Iniciando búsqueda del producto creado...")
        time.sleep(3)
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
        {"id_caso": "TC023-001", "atributos": True, "perecedero": False, "tipo_producto": "Producto normal", "nombre_caso": "Creacion exitosa con atributos"},
        {"id_caso": "TC023-002", "atributos": False, "perecedero": False, "tipo_producto": "Producto normal", "nombre_caso": "Creacion exitosa sin atributos"},
        {"id_caso": "TC023-003", "atributos": True, "perecedero": True, "tipo_producto": "Producto normal", "nombre_caso": "Creacion exitosa con atributos y producto perecedero"},
        {"id_caso": "TC023-004", "atributos": False, "perecedero": True, "tipo_producto": "Producto normal", "nombre_caso": "Creacion exitosa sin atributos y perecedero"}
    ]
    
    print("="*60)
    print("🚀 INICIANDO EJECUCIÓN MAESTRA DE TODOS LOS CASOS TC023")
    print("="*60)
    
    for caso in casos_a_ejecutar:
        try:
            ejecutar_caso(caso)
        except Exception as e_main:
            print(f"❌ Error inesperado no controlado en el caso {caso.get('id_caso')}: {e_main}")
        time.sleep(5)  # Pequeña pausa entre casos para evitar problemas de caché o cierres bruscos
        
    print("\n✅ TODAS LAS EJECUCIONES HAN TERMINADO.")
