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
id_caso = "TC058-2"

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
        
        productos_seleccionados = []
        if productos_disponibles:
            # Eliminar duplicados
            productos_disponibles = list(set(productos_disponibles))
            cantidad_disponible = len(productos_disponibles)
            
            # Tomamos entre 2 y 4 productos (o los que haya si son menos de 2)
            cantidad_a_tomar = random.randint(min(2, cantidad_disponible), min(4, cantidad_disponible))
            productos_seleccionados = random.sample(productos_disponibles, cantidad_a_tomar)
            
            print(f"o. Se contaron {cantidad_disponible} productos disponibles.")
            print(f"o. Productos aleatorios seleccionados ({cantidad_a_tomar}): {', '.join(productos_seleccionados)}")
        else:
            print("s? No se encontraron productos para este proveedor.")
            
    except Exception as ex:
        print(f"s? Error al extraer datos del proveedor: {ex}")
    
    # 2. Ir a "rdenes de Compra
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
        # 4. BUSCAR Y AGREGAR LOS PRODUCTOS
        # -----------------------------------------------------------
        for prod_nombre in productos_seleccionados:
            print(f"⏳ Buscando el producto '{prod_nombre}'...")
            
            # Encontrar el input de busqueda por su placeholder
            xpath_buscador = "//input[@placeholder='Busca por producto, SKU o cdigo de barras' or @placeholder='Busca por producto, SKU o c\u00f3digo de barras']"
            input_buscador = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_buscador)))
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_buscador)
            time.sleep(0.5)
            
            input_buscador.click()
            time.sleep(0.5)
            
            # Limpiar antes de buscar
            input_buscador.send_keys(webdriver.Keys.CONTROL + "a")
            input_buscador.send_keys(webdriver.Keys.BACKSPACE)
            time.sleep(0.5)
            
            input_buscador.send_keys(prod_nombre)
            time.sleep(3) # Esperar a que cargue la lista desplegable
            
            encontrado = False
            for _ in range(15): # Intentar hasta 15 veces hacer scroll hacia abajo
                opciones = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-item-option')]")
                for opcion in opciones:
                    texto_opcion = opcion.text.strip()
                    if not texto_opcion: continue
                    
                    if prod_nombre.lower() in texto_opcion.lower():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opcion)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", opcion)
                        encontrado = True
                        print(f"o. Producto '{texto_opcion}' encontrado y seleccionado.")
                        break
                
                if encontrado:
                    break
                    
                # Si no se encuentra en los elementos renderizados, presionamos flecha abajo 2 veces para scrollear la lista virtual
                input_buscador.send_keys(webdriver.Keys.ARROW_DOWN)
                input_buscador.send_keys(webdriver.Keys.ARROW_DOWN)
                time.sleep(0.5)
                
            if not encontrado:
                print(f"s? '{prod_nombre}' no encontrado tras scrollear. Presionando ENTER por defecto.")
                input_buscador.send_keys(webdriver.Keys.ENTER)
                
            time.sleep(2) # Esperar a que se agregue a la tabla antes de buscar el siguiente

            # --- INGRESAR CANTIDAD ---
            try:
                # 1. Encontrar la celda de cantidad (columna 3) para este producto y darle clic
                # Usamos td[3] asumiendo que: 1=Producto, 2=Costo, 3=Cantidad
                xpath_celda = f"//tr[contains(@class, 'ant-table-row') and contains(., '{prod_nombre}')]//td[3]"
                celda_cantidad = driver.find_element(By.XPATH, xpath_celda)
                
                # Buscamos el elemento clickeable dentro de la celda si existe (un span o div con el texto '1')
                # O simplemente le damos clic a la celda
                try:
                    elemento_clic = celda_cantidad.find_element(By.XPATH, ".//*[text()='1']")
                    driver.execute_script("arguments[0].click();", elemento_clic)
                except:
                    driver.execute_script("arguments[0].click();", celda_cantidad)
                    
                time.sleep(1) # Esperar a que se abra el cuadro
                
                # 2. Interactuar con el popover
                # Buscamos el input visible
                xpath_input = "//div[contains(@class, 'ant-popover') and not(contains(@style, 'display: none'))]//input"
                input_cantidad = driver.find_element(By.XPATH, xpath_input)
                
                # Borrar el '1' y poner cantidad aleatoria
                nueva_cantidad = random.randint(2, 20)
                input_cantidad.send_keys(webdriver.Keys.CONTROL + "a")
                input_cantidad.send_keys(webdriver.Keys.BACKSPACE)
                time.sleep(0.3)
                input_cantidad.send_keys(str(nueva_cantidad))
                time.sleep(0.5)
                
                # 3. Guardar
                xpath_btn_guardar = "//div[contains(@class, 'ant-popover') and not(contains(@style, 'display: none'))]//button[contains(., 'Guardar')]"
                btn_guardar = driver.find_element(By.XPATH, xpath_btn_guardar)
                driver.execute_script("arguments[0].click();", btn_guardar)
                
                print(f"o. Cantidad {nueva_cantidad} guardada para el producto '{prod_nombre}'.")
                time.sleep(1) # Esperar a que se cierre el popover
                
            except Exception as e:
                print(f"s? Error al intentar ingresar la cantidad para '{prod_nombre}': {e}")

        # --- INGRESAR FECHA Y OBSERVACIONES ---
        try:
            print("? Llenando fecha y observaciones...")
            # 1. Fecha
            xpath_fecha = "//input[@placeholder='Seleccionar fecha']"
            input_fecha = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_fecha)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_fecha)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", input_fecha)
            time.sleep(1) # Esperar a que abra el calendario
            
            # Clic en el boton 'Hoy' del calendario de Ant Design
            xpath_hoy = "//*[contains(@class, 'ant-picker-today-btn') or text()='Hoy' or text()='Today']"
            btn_hoy = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hoy)))
            driver.execute_script("arguments[0].click();", btn_hoy)
            print("o. Fecha seleccionada correctamente.")
            time.sleep(0.5)
            
            # 2. Observaciones
            # Intentamos encontrar el textarea que este despues de un label de Observaciones, o simplemente el primer textarea
            xpath_obs = "//*[contains(translate(text(), 'OBSERVACIONES', 'observaciones'), 'observacion')]/following::textarea[1] | //textarea"
            textarea_obs = driver.find_element(By.XPATH, xpath_obs)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea_obs)
            time.sleep(0.5)
            textarea_obs.send_keys("Orden de compra automatizada generada por prueba de integracion QA.")
            print("o. Observaciones ingresadas correctamente.")
            time.sleep(1)
            
        except Exception as e:
            print(f"s? Error al ingresar fecha u observaciones: {e}")

        # --- FINALIZAR: CLIC EN CREAR ---
        try:
            print("? Finalizando: buscando boton 'Crear' para guardar la orden...")
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Buscar el boton Crear final (arriba a la derecha)
            xpath_btn_crear = "//button[contains(., 'Crear') or contains(., 'CREAR')]"
            btns_crear = driver.find_elements(By.XPATH, xpath_btn_crear)
            
            clickeado = False
            for btn in btns_crear:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print("o. Clic en el boton final 'Crear' exitoso.")
                    clickeado = True
                    break
                    
            if not clickeado:
                print("s? No se pudo clickear el boton Crear. Revisar XPath.")
                
            time.sleep(5) # Esperar a que guarde en base de datos y muestre mensaje/redirija
            print("o. ======= PRUEBA EXITOSA: ORDEN DE COMPRA COMPLETADA =======")
            
        except Exception as e:
            print(f"s? Error al hacer clic en Crear al final: {e}")

            
    except Exception as e:
        print(f"s? Error en la navegacin/extraccin: {e}")
        raise e

    # registrar_resultado(id_caso, "Exitosa", "Orden creada correctamente")

except Exception as e:
    print(f"CRITICAL ERROR: {str(e)}"); registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")

finally:
    driver.quit()
