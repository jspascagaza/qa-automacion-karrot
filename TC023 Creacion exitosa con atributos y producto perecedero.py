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
import subprocess
import sys

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
id_caso = "TC023-003"

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
def pantalla_login(nombre_producto, reintentar=True):
    """
    Función principal que ejecuta todo el flujo
    Si reintentar=True y se crea una categoría, se reinicia la ejecución
    """
    
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
            texto_agregar_categoria = driver.find_element(By.XPATH, "//*[text()=' Añadir Categoría']")            
            if texto_agregar_categoria:
                print("🔍 Botón 'añadir categoria' encontrado, procediendo a crear categoría...")
                script_path = "Agregar categoria.py"
                # Ejecutar el script
                result = subprocess.run([sys.executable, script_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=120)
                time.sleep(2)
                
                # Si se creó una categoría, reiniciar la ejecución
                if reintentar:
                    print("🔄 Categoría creada, reiniciando ejecución...")
                    driver.quit()
                    pantalla_login(nombre_producto, reintentar=False)
                    return True
                return True
        except TimeoutException:
            # El botón no existe, continuar con el flujo normal
            print("ℹ️ No se encontró el botón 'añadir categoria', continuando con el flujo normal")
            return False
        except Exception as e:
            print(f"⚠️ Error al verificar/crear categoría: {e}")
            return False

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

    def manejar_atributos_adicionales(driver, agregar_atributos=False, timeout=10):
        """
        Maneja los campos de atributo e ingresa valores confirmando con ENTER
        """
        try:
            if not agregar_atributos:
                print("⏭️  No se agregarán atributos adicionales")
                return None, None
        
            wait = WebDriverWait(driver, timeout)
        
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
            return nombre_atributo, valores_atributos
        except Exception as e:
            print(f"❌ Error al configurar atributos adicionales: {e}")
            return None, None
        
    nombre_atributo, valores_atributos = manejar_atributos_adicionales(driver, agregar_atributos=activar_atributos)
    time.sleep(2)
    
    def generar_campos_por_atributo(driver, nombre_atributo, valores_atributos, timeout=10, agregar_atributos=False):
        if not agregar_atributos:
            print("⏭️  generar_campos_por_atributo: agregar_atributos=False, no se ejecuta")
            return False

        try:
            print("⏳ Buscando botones de edición de variante (lápiz)...")
            todos_lapices = driver.find_elements(By.XPATH, "//button[span[contains(@class, 'anticon-edit')] or .//span[@aria-label='edit']]")
            botones_lapiz = []
            for lapiz in todos_lapices:
                try:
                    texto_padre = lapiz.find_element(By.XPATH, "./..").text
                    if "Unidad" not in texto_padre:
                        botones_lapiz.append(lapiz)
                except Exception:
                    botones_lapiz.append(lapiz)
            
            if not botones_lapiz:
                print("❌ No se encontraron botones de variante.")
                return False
                
            def obtener_campo(wait_obj, drv, id_campo):
                try:
                    return wait_obj.until(EC.presence_of_element_located((By.ID, id_campo)))
                except Exception:
                    inputs = drv.find_elements(By.XPATH, f"//input[contains(@id, '{id_campo}')]")
                    for input_elem in inputs:
                        if input_elem.is_displayed():
                            return input_elem
                    raise Exception(f"No se pudo localizar el campo {id_campo}")
            
            # Recorrer cada lápiz (uno por variante)
            for idx, lapiz in enumerate(botones_lapiz):
                if idx >= len(valores_atributos):
                    break
                valor_atributo = valores_atributos[idx]
                print(f"\n🎯 Procesando variante {idx+1}: {nombre_atributo} - {valor_atributo}")
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lapiz)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", lapiz)
                time.sleep(3)
                
                # Llenar datos en el modal
                sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
                try:
                    campo_sku = obtener_campo(wait, driver, "sku")
                    driver.execute_script("arguments[0].value = '';", campo_sku)
                    campo_sku.send_keys(Keys.CONTROL + "a")
                    campo_sku.send_keys(sku_aleatorio)
                    print(f"✅ SKU para {valor_atributo}: '{sku_aleatorio}'")
                except Exception as e:
                    print(f"❌ Error SKU: {e}")
                    
                barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                try:
                    campo_barcode = obtener_campo(wait, driver, "barcode")
                    driver.execute_script("arguments[0].value = '';", campo_barcode)
                    campo_barcode.send_keys(Keys.CONTROL + "a")
                    campo_barcode.send_keys(barcode_aleatorio)
                    print(f"✅ Barcode para {valor_atributo}: '{barcode_aleatorio}'")
                except:
                    pass

                valor_costo = precio            
                try:
                    campo_costo = obtener_campo(wait, driver, "cost")
                    driver.execute_script("arguments[0].value = '';", campo_costo)
                    campo_costo.send_keys(Keys.CONTROL + "a")
                    campo_costo.send_keys(str(valor_costo))
                    print(f"✅ Costo para {valor_atributo}: '{valor_costo}'")
                except:
                    pass

                try:
                    campo_precio = driver.find_elements(By.ID, "price")
                    if campo_precio and campo_precio[0].is_displayed():
                        driver.execute_script("arguments[0].value = '';", campo_precio[0])
                        campo_precio[0].send_keys(Keys.CONTROL + "a")
                        campo_precio[0].send_keys(str(precio))
                        print(f"✅ Precio para {valor_atributo}: '{precio}'")
                except:
                    pass
                    
                # Aplicar
                try:
                    boton_aplicar = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal')]//button[span[text()='Aplicar'] or contains(., 'Aplicar')] | //button[span[text()='Aplicar']]")
                    if boton_aplicar and len(boton_aplicar) > 0:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_aplicar[-1])
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", boton_aplicar[-1])
                        time.sleep(2)
                except Exception as e:
                    print(f"⚠️ No se encontró botón 'Aplicar' del modal: {e}")
                    
            return True
        except Exception as e:
            print(f"❌ Error general en generar_campos_por_atributo: {e}")
            import traceback
            traceback.print_exc()
            return False

        resultado = generar_campos_por_atributo(driver, nombre_atributo, valores_atributos, timeout=10, agregar_atributos=activar_atributos)
        # Capturar los valores de barcode y sku
        if activar_atributos and resultado:
            barcode_aleatorio, sku_aleatorio = resultado
        else:
            barcode_aleatorio = None
            sku_aleatorio = None
        print(f"✅ Barcode: {barcode_aleatorio}, SKU: {sku_aleatorio}")
        
        boton_anadir = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='advanced_search']/div[1]/div/div/div/button[2]")))
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
                print("🔄 El producto ya existe o hubo un error. Generando nuevo nombre y reintentando...")
                driver.quit()
                sufijo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                nuevo_nombre = f"{nombre_producto} {sufijo}"
                return pantalla_login(nuevo_nombre, reintentar=reintentar)
        except TimeoutException:
            # Si no hay mensaje o no pudimos capturarlo, esperamos un poco más
            time.sleep(5)
            pass
            
        time.sleep(5)
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
                    registrar_resultado(id_caso, estado, observaciones)
            else:
                print("❌ No se encontró la opción de búsqueda 'Buscar '")
                observaciones = "No se encontró la opción de búsqueda 'Buscar por Nombre'"
                estado = "FALLIDO"
                registrar_resultado(id_caso, estado, observaciones)
        except Exception as e:
            print(f"❌ Error al abrir el dropdown: {e}")
            print("Opciones de busqueda encontradas:")
            observaciones = f"Error al abrir el dropdown: {e}"
            estado = "FALLIDO"
            registrar_resultado(id_caso, estado, observaciones)

        registrar_resultado(id_caso, estado, observaciones)

    except Exception as e:
        print(f"❌ Error durante la ejecución: {str(e)}")
        observaciones = f"Error durante la ejecución: {str(e)}"
        estado = "FALLIDO"
        registrar_resultado(id_caso, estado, observaciones)

# Ejecutar la función principal
pantalla_login(nombre_producto)