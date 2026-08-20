import time
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# =====================
# CONFIGURACI"N DE LOGS
# =====================
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
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('ascii', 'ignore').decode('ascii'))
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(log_filename)
sys.stderr = sys.stdout

# =====================
# CONFIGURACI"N GOOGLE SHEETS
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

def registrar_resultado(id_caso, estado, observaciones=""):
    try:
        celda = sheet.find(id_caso)
        if not celda:
            print(f"s? No se encontr el ID {id_caso}")
            return
        fila = celda.row
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        automatizado = "S"
        sheet.update_cell(fila, 11, automatizado)   # Columna K
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"o. Caso {id_caso} actualizado -> {estado}")
    except Exception as e:
        print(f"?O Error al actualizar el caso {id_caso}: {str(e)}")


# =====================
# PRUEBA AUTOMATIZADA
# =====================
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")

wait = WebDriverWait(driver, 40)
id_caso = "TC055"

try:
    print("⏳ Iniciando sesin...")
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    print("o. Login exitoso")

    print("⏳ Esperando navegacin al dashboard / panel principal...")
    time.sleep(10)
    print("Ys Fin de la parte de login. Pendiente de continuar con el flujo especfico.")

    # -----------------------------------------------------------------------------------
    # EXTRACCION DE DATOS DEL PROVEEDOR Y NAVEGACI"N A ORDENES DE COMPRA
    # -----------------------------------------------------------------------------------
    try:
        print("⏳ Navegando a Proveedores para extraer datos...")
        submenu_proveedores = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space()='Proveedores'] | //a[normalize-space()='Proveedores']")
        ))
        submenu_proveedores.click()
        time.sleep(1)
        
        opcion_lista_proveedores = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space()='Lista de proveedores'] | //a[normalize-space()='Lista de proveedores']")
        ))
        opcion_lista_proveedores.click()
        print("o. Click en Lista de proveedores")
        time.sleep(5)
        
        # Click en Mas info del primer proveedor de la tabla
        boton_mas_info = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//table/tbody/tr[contains(@class, 'ant-table-row')])[1]//button | (//table/tbody/tr[contains(@class, 'ant-table-row')])[1]//a[contains(text(), 'Ms informacin')]")
        ))
        
        # Extraer el nombre del proveedor
        celda_nombre = driver.find_element(By.XPATH, "(//table/tbody/tr[contains(@class, 'ant-table-row')])[1]/td[2]")
        proveedor_nombre = celda_nombre.text.strip()
        print(f"o. Proveedor seleccionado: {proveedor_nombre}")
        
        boton_mas_info.click()
        time.sleep(5)
        
        # Ahora estamos en la pantalla de detalles.
        # Extraer productos. Buscamos en todas las filas de todas las tablas
        filas_productos = driver.find_elements(By.XPATH, "//table/tbody/tr[contains(@class, 'ant-table-row')]")
            
        productos_disponibles = []
        import random
        for fila in filas_productos:
            celdas_prod = fila.find_elements(By.TAG_NAME, "td")
            if len(celdas_prod) > 0:
                try:
                    # Los productos y materias primas tienen su nombre real en un div con clase 'ml-2' en la primera celda
                    nombre_div = celdas_prod[0].find_element(By.XPATH, ".//div[contains(@class, 'ml-2')]")
                    texto_limpio = nombre_div.text.strip()
                    if texto_limpio and texto_limpio != "-":
                        productos_disponibles.append(texto_limpio)
                except:
                    pass
        
        if productos_disponibles:
            producto_nombre = random.choice(productos_disponibles)
            print(f"o. Producto aleatorio seleccionado: {producto_nombre}")
        else:
            print("s? No se encontraron productos para este proveedor.")
            
    except Exception as ex:
        print(f"s? Error al extraer datos del proveedor: {ex}")
    
    # 2. Ir a "Ordenes de Compra
    try:
        print("⏳ Navegando a Ordenes de Compra...")
        submenu_ordenes = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space()='Ordenes de Compra'] | //a[normalize-space()='Ordenes de Compra']")
        ))
        submenu_ordenes.click()
        print("o. Click en Ordenes de Compra")
        time.sleep(5)
        
        # Click en el botn especificado
        print("⏳ Buscando botn de Crear/Agregar (especificado)...")
        boton_xpath = '//*[@id="root"]/div/section/section/section/div/main/div[5]/div/div[1]/div[2]/div/button[1]'
        boton = wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath)))
        boton.click()
        print("o. Click en el botn especificado")
        time.sleep(3)
        
        # Llenar el input con el proveedor extrado
        if proveedor_nombre:
            print(f"⏳ Ingresando el proveedor '{proveedor_nombre}' en el selector...")
            # Seleccionar estrictamente el input dentro del contenedor del label 'Proveedor'
            xpath_input = "//div[contains(@class, 'ant-form-item') and .//label[contains(text(), 'Proveedor')]]//input[not(@readonly)]"
            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_input)))
            
            # Scroll to element to avoid interception
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_proveedor)
            time.sleep(0.5)
            
            input_proveedor.click()
            time.sleep(1)
            
            # Limpiamos usando ctrl+a / backspace en vez de .clear() que a veces falla en selectores React
            input_proveedor.send_keys(webdriver.Keys.CONTROL + "a")
            input_proveedor.send_keys(webdriver.Keys.BACKSPACE)
            
            input_proveedor.send_keys(proveedor_nombre)
            time.sleep(2)
            
            # Seleccionar la opcin del dropdown
            # Buscamos un elemento en el popup del dropdown que contenga el nombre
            xpath_opcion = f"//div[contains(@class, 'ant-select-item-option-content') and contains(text(), '{proveedor_nombre}')]"
            try:
                opcion = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion)))
                opcion.click()
                print("o. Proveedor seleccionado en el dropdown")
            except:
                print("s? No se pudo clickear la opcin por texto, intentando seleccionar la primera opcin activa...")
                input_proveedor.send_keys(webdriver.Keys.ENTER)
            time.sleep(2)

        # -----------------------------------------------------------
        # 3. SELECCIONAR EL LUGAR DE ENTREGA
        # -----------------------------------------------------------
        print("⏳ Seleccionando el Lugar de Entrega...")
        
        # Buscar el input correcto basndonos en su Label
        xpath_ubicacion = "//div[contains(@class, 'ant-form-item') and .//label[contains(text(), 'Lugar de Entrega')]]//input[not(@readonly)]"
        input_ubicacion = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_ubicacion)))
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_ubicacion)
        time.sleep(0.5)
        
        # Forzar clic para abrir el men
        driver.execute_script("arguments[0].click();", input_ubicacion)
        time.sleep(1)
        
        # Usar el teclado para seleccionar la primera opcin (infalible en React)
        input_ubicacion.send_keys(webdriver.Keys.ARROW_DOWN)
        time.sleep(0.5)
        input_ubicacion.send_keys(webdriver.Keys.ENTER)
        
        print("o. Lugar de Entrega seleccionado correctamente.")
        time.sleep(1)
        
        # -----------------------------------------------------------
        # 4. BUSCAR Y AGREGAR EL PRODUCTO
        # -----------------------------------------------------------
        print(f"⏳ Buscando el producto '{producto_nombre}'...")
        
        # Encontrar el input de busqueda por su placeholder
        xpath_buscador = "//input[@placeholder='Busca por producto, SKU o cdigo de barras' or @placeholder='Busca por producto, SKU o código de barras']"
        input_buscador = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_buscador)))
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_buscador)
        time.sleep(0.5)
        
        input_buscador.click()
        time.sleep(0.5)
        input_buscador.send_keys(producto_nombre)
        time.sleep(3) # Esperar a que cargue la lista desplegable
        
        # Seleccionar el producto del listado desplegable
        # Buscamos la opcion exacta
        xpath_opcion_prod = f"//div[contains(@class, 'ant-select-item-option-content') and contains(text(), '{producto_nombre}')]"
        try:
            opcion_prod = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion_prod)))
            opcion_prod.click()
            print("o. Producto seleccionado de la lista desplegable.")
        except:
            print("s? No se encontro la opcion exacta por texto. Seleccionando la primera opcion con el teclado...")
            input_buscador.send_keys(webdriver.Keys.ARROW_DOWN)
            time.sleep(0.5)
            input_buscador.send_keys(webdriver.Keys.ENTER)
            print("o. Producto seleccionado con teclado.")
            
        time.sleep(2) # Esperar a que se agregue a la tabla

            
    except Exception as e:
        print(f"s? Error en la navegacin/extraccin: {e}")
        raise e

    # registrar_resultado(id_caso, "Exitosa", "Orden creada correctamente")

except Exception as e:
    print(f"CRITICAL ERROR: {str(e)}"); registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")

finally:
    driver.quit()
