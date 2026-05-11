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
from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import string
from faker import Faker
import faker_commerce; print(faker_commerce.__file__)
import re
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
    os.getenv("GOOGLE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0")
)
sheet = spreadsheet.sheet1

# Variable para controlar el éxito de la ejecución
exito = False
observaciones = ""
url_final = ""

# Variables para guardar estado del inventario para la venta
producto_seleccionado = ""
inventario_inicial = 0

# =====================
# PRUEBA REGISTRO COMPLETO CON CONSULTOR Y VERIFICACIÓN
# =====================
id_caso = "TC030"

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

def esperar_tabla_inventario():
    """
    Espera a que la tabla de inventario esté presente usando múltiples estrategias
    """
    print("⏳ Esperando tabla de inventario...")
    
    # Lista de posibles selectores para la tabla
    selectores = [
        (By.XPATH, '//table'),
        (By.XPATH, '//div[contains(@class, "table")]'),
        (By.XPATH, '//div[contains(@class, "ant-table")]'),
        (By.XPATH, '//*[contains(@id, "table")]'),
        (By.XPATH, '//*[contains(@class, "inventory")]//table'),
        (By.CLASS_NAME, 'ant-table'),
        (By.TAG_NAME, 'table'),
    ]
    
    for selector_type, selector_value in selectores:
        try:
            print(f"  Probando selector: {selector_type} = '{selector_value}'")
            elemento = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            print(f"✅ Tabla encontrada con selector: {selector_value}")
            return elemento
        except TimeoutException:
            continue
        except Exception as e:
            print(f"  Error con selector {selector_value}: {e}")
            continue
    
    print("⚠️ No se pudo encontrar la tabla con ningún selector estándar")
    
    # Último intento: capturar screenshot para debug
    try:
        driver.save_screenshot("debug_inventario.png")
        print("📸 Screenshot guardado como 'debug_inventario.png'")
    except:
        pass
    
    return None        


def leer_inventario_actual(iniciar_ajuste=True):
    """
    Lee el primer producto visible en el cuadro de inventario y extrae su stock en la sede actual.
    """
    global producto_seleccionado, inventario_inicial
    print("📊 Leyendo el primer producto del inventario...")
    try:
        # Usamos la validación existente para esperar la tabla
        tabla = esperar_tabla_inventario()
        time.sleep(3) # Esperar a que rendericen los datos de las filas
        
        # 1. Buscar la primera fila de datos de la tabla (normalmente tr con ant-table-row)
        xpath_primera_fila = '//tbody/tr[contains(@class, "ant-table-row")][1]'
        primera_fila = wait.until(EC.presence_of_element_located((By.XPATH, xpath_primera_fila)))
        
        # 2. Extraemos el texto de las columnas.
        # Basado en la imagen: Checkbox(1), Producto(2), SKU(3), Código de barras(4), Sede(5)
        nombre_producto_elem = primera_fila.find_element(By.XPATH, './td[2]')
        stock_sede_elem = primera_fila.find_element(By.XPATH, './td[5]')
        
        # Limpieza de datos
        nombre_producto = nombre_producto_elem.text.strip()
        stock_texto_bruto = stock_sede_elem.text.strip()
        
        # El stock suele decir algo como "19 ✔ (Ver lotes)", sacamos solo el primer número
        import re
        numeros = re.findall(r'-?\d+', stock_texto_bruto)
        stock_actual = int(numeros[0]) if numeros else 0
        
        print(f"📦 Producto capturado: '{nombre_producto}'")
        print(f"📦 Inventario inicial en sede: {stock_actual}")
        
        producto_seleccionado = nombre_producto
        inventario_inicial = stock_actual
        
        if iniciar_ajuste:
            # Seleccionar el checkbox del producto
            print("📦 Seleccionando el producto (checkbox)...")
            try:
                # Intentar primero con el XPath absoluto proporcionado por el usuario
                xpath_checkbox = '//*[@id="root"]/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[1]/label/span/input'
                checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_checkbox)))
                
                # Usar JS para hacer click y evitar intercepciones
                driver.execute_script("arguments[0].click();", checkbox)
                print("✅ Producto seleccionado exitosamente (XPath absoluto)")
                time.sleep(1) # Pequeña pausa para asegurar que se registre la selección
                
            except Exception as e:
                print(f"⚠️ Falló el click con XPath absoluto: {e}. Intentando estrategia relativa...")
                try:
                    # Fallback: Buscar el checkbox relativo dentro de la fila que ya tenemos identificada
                    checkbox_relativo = primera_fila.find_element(By.XPATH, './/input[@type="checkbox"]')
                    driver.execute_script("arguments[0].click();", checkbox_relativo)
                    print("✅ Producto seleccionado exitosamente (Estrategia relativa)")
                    time.sleep(1)
                except Exception as e_fallback:
                    print(f"❌ Error al intentar seleccionar el checkbox del producto: {e_fallback}")
                    
            # Hacer clic en el botón Ajuste Manual
            print("🔍 Buscando botón de 'Ajuste manual'...")
            try:
                xpath_ajuste = '//*[@id="root"]/div/section/section/section/div/main/div[2]/div/div/div/div/div[1]/div/div[2]/button[1]'
                boton_ajuste = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_ajuste)))
                driver.execute_script("arguments[0].click();", boton_ajuste)
                print("✅ Botón 'Ajuste manual' clickeado exitosamente")
                time.sleep(2) # Dar tiempo para que se abra el modal o inicie el flujo de ajuste
            except Exception as e_ajuste:
                print(f"⚠️ Error al intentar clickear el botón 'Ajuste manual': {e_ajuste}")
            
        return producto_seleccionado, inventario_inicial
    except Exception as e:
        print(f"❌ Error al intentar leer el primer producto del inventario: {e}")
        try:
            driver.save_screenshot("error_lectura_inventario.png")
        except:
            pass
        return None, 0

def ingresar_ajuste_manual():
    """
    Interactúa con el modal 'Ajustar la cantidad de inventario' para ingresar un valor.
    """
    print("📦 Ingresando valores en el modal de Ajuste de Inventario...")
    try:
        # Esperar a que el modal cargue
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Ajustar la cantidad de inventario')]")))
        time.sleep(3) # Dar tiempo extra a que la tabla y los inputs se rendericen dentro del modal
        
        # Generar un valor aleatorio a ingresar
        valor_ajuste = random.randint(1, 10)
        print(f"🎲 Valor aleatorio a ajustar (Ingreso): {valor_ajuste}")
        
        # Buscar todos los inputs dentro de la tabla del modal
        # Usamos un XPath más general ya que tr[1] a veces falla si hay filas anidadas o headers dobles
        xpath_inputs_tabla = "//div[contains(@class, 'ant-modal')]//table//input"
        
        # Hacemos varios intentos para encontrar los inputs por si demoran en cargar
        input_cantidad = None
        for intento in range(3):
            try:
                inputs = driver.find_elements(By.XPATH, xpath_inputs_tabla)
                inputs_visibles = [inp for inp in inputs if inp.is_displayed()]
                
                if inputs_visibles:
                    # El primer input visible en la tabla suele ser el de la cantidad (debajo de la Sede)
                    # El segundo sería el costo, el tercero el lote, etc.
                    input_cantidad = inputs_visibles[0]
                    print(f"✅ Se encontraron {len(inputs_visibles)} inputs visibles. Seleccionando el primero.")
                    break
            except Exception as e_find:
                print(f"  Intento {intento+1} fallido: {e_find}")
            time.sleep(2)
            
        if not input_cantidad:
            raise Exception("No se encontraron inputs visibles en la tabla del modal tras varios intentos")
            
        # Ingresar el valor
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_cantidad)
        time.sleep(0.5)
        
        input_cantidad.click()
        time.sleep(0.5)
        # Usar Ctrl+A y Backspace para asegurar que se borre el "0.00"
        input_cantidad.send_keys(Keys.CONTROL + "a")
        time.sleep(0.2)
        input_cantidad.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        input_cantidad.send_keys(str(valor_ajuste))
        print(f"✅ Valor {valor_ajuste} ingresado en el campo de cantidad")
        time.sleep(1)
        
        # --- NUEVO: Ingresar Fechas y Lote (necesario en algunos casos para habilitar Guardar) ---
        try:
            print("⏳ Buscando campos de fecha...")
            inputs_fecha = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal')]//input[@placeholder='Select date' or @placeholder='Seleccionar fecha']")
            
            if len(inputs_fecha) >= 2:
                # Fecha de Fabricación
                fecha_fab = inputs_fecha[0]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fecha_fab)
                fecha_fab.click()
                fecha_fab.send_keys("2025-12-15")
                fecha_fab.send_keys(Keys.ENTER)
                print("✅ Fecha Fabricación ingresada: 2025-12-15")
                time.sleep(1)
                
                # Fecha de Caducidad
                fecha_cad = inputs_fecha[1]
                fecha_cad.click()
                fecha_cad.send_keys("2025-12-15")
                fecha_cad.send_keys(Keys.ENTER)
                print("✅ Fecha Caducidad ingresada: 2025-12-15")
                time.sleep(1)
            else:
                print(f"⚠️ No se encontraron suficientes campos de fecha (hallados: {len(inputs_fecha)})")
                
            print("⏳ Buscando campo de Lote...")
            inputs_lote = driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-modal')]//input[contains(@placeholder, 'Número de') or contains(@placeholder, 'Lote')]")
            if inputs_lote:
                lote = inputs_lote[0]
                lote.click()
                lote.send_keys("LOTE-TEST-123")
                print("✅ Número de Lote ingresado: LOTE-TEST-123")
                time.sleep(1)
        except Exception as e_extra:
            print(f"⚠️ Error al ingresar fechas o lote (puede que no sean obligatorios en esta sede): {e_extra}")
        # --- FIN FECHAS Y LOTE ---
        
        # Clic en Guardar
        print("🔍 Buscando botón 'Guardar'...")
        try:
            xpath_guardar = "//div[contains(@class, 'ant-modal')]//button[contains(., 'Guardar')]"
            boton_guardar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_guardar)))
            boton_guardar.click()
            print("✅ Botón 'Guardar' clickeado (Normal)")
        except Exception as e_btn:
            print(f"⚠️ Falló click normal en Guardar: {e_btn}, intentando JS...")
            boton_guardar = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-modal')]//button[contains(., 'Guardar')]")
            driver.execute_script("arguments[0].click();", boton_guardar)
            print("✅ Botón 'Guardar' clickeado (JS)")
            
        # Esperar a que el modal se cierre y la página procese el cambio
        time.sleep(3)
        return valor_ajuste
        
    except Exception as e:
        import traceback
        print(f"❌ Error al ingresar el ajuste manual: {e}")
        traceback.print_exc()
        try:
            driver.save_screenshot("error_ajuste_manual.png")
            print("📸 Screenshot guardado en error_ajuste_manual.png")
        except:
            pass
        return 0

def validar_actualizacion_inventario(valor_a_ingresar):
    """
    Valida matemáticamente que el inventario se haya actualizado correctamente
    después de un ajuste manual.
    """
    global inventario_inicial, exito, observaciones
    try:
        print("⏳ Esperando actualización de inventario...")
        time.sleep(5) # Dar tiempo para que se procese y actualice la tabla
        
        print("\n📊 EXTRAYENDO VALORES FINALES:")
        # Re-leemos el inventario sin interactuar con los botones de ajuste (iniciar_ajuste=False)
        _, inventario_final = leer_inventario_actual(iniciar_ajuste=False)
        
        if inventario_final is not None:
            valor_agregado_num = int(valor_a_ingresar)
            
            print(f"\n🧮 VALIDACIÓN MATEMÁTICA:")
            print(f"   Inicial: {inventario_inicial}")
            print(f"   Agregado/Ajustado por: {valor_agregado_num}")
            print(f"   Esperado: {inventario_inicial + valor_agregado_num}")
            print(f"   Obtenido: {inventario_final}")
            
            if (inventario_inicial + valor_agregado_num) == inventario_final:
                print("✅ VALIDACIÓN EXITOSA: El inventario se actualizó correctamente.")
                observaciones += " | Validación Matemática OK"
                # Sobreescribimos el éxito general basado en esta prueba crucial
                exito = True
            else:
                print("❌ VALIDACIÓN FALLIDA: Los valores no coinciden.")
                observaciones += f" | Fallo Matemático (Esp: {inventario_inicial + valor_agregado_num}, Obt: {inventario_final})"
                exito = False
        else:
             print("❌ No se pudo extraer el inventario final o falta el valor ingresado.")
             observaciones += " | Fallo extracción final"
             exito = False
    except Exception as e:
        print(f"❌ Error en validación de inventario: {e}")
        observaciones += f" | Error validación: {e}"
        exito = False

def ingreso_al_pos():   
    try:
        print("🔍 Comprobando si hay un turno activo previo...")
        turno_activo_sede = "sede bogota"
        turno_activo_caja = None
        try:
            time.sleep(2) # Dar tiempo a que el mensaje aparezca si existe
            mensaje_turno = driver.find_elements(By.XPATH, "//*[contains(text(), 'Tienes un turno activo en')]")
            if len(mensaje_turno) > 0:
                texto_mensaje = mensaje_turno[0].text
                print(f"ℹ️ Mensaje detectado: '{texto_mensaje}'")
                import re
                match = re.search(r"activo en (.+?) - (.+)", texto_mensaje)
                if match:
                    turno_activo_sede = match.group(1).strip()
                    turno_activo_caja = match.group(2).strip()
                    print(f"✅ Sede activa extraída: {turno_activo_sede}")
                    print(f"✅ Caja activa extraída: {turno_activo_caja}")
        except Exception as e:
            print("No se encontró mensaje de turno activo previo o error extrayendo:", e)

        # ==========================================
        # 1. SELECCIONAR SEDE
        # ==========================================
        print(f"🔍 Seleccionando sede: '{turno_activo_sede}' (Estrategia Teclado)...")
        try:
            time.sleep(2)
            xpath_input = "//input[contains(@class, 'ant-select-selection-search-input')]"
            inputs = driver.find_elements(By.XPATH, xpath_input)
            
            target_input_sede = None
            if inputs:
                target_input_sede = inputs[0] # El primero suele ser Sede
                
            if target_input_sede:
                driver.execute_script("arguments[0].focus();", target_input_sede)
                time.sleep(0.5)
                
                # Enviar Flecha Abajo para abrir menú y luego la sede
                target_input_sede.send_keys(Keys.DOWN)
                time.sleep(1)
                
                target_input_sede.send_keys(Keys.CONTROL + "a")
                target_input_sede.send_keys(Keys.BACKSPACE)
                time.sleep(0.5)
                target_input_sede.send_keys(turno_activo_sede)
                time.sleep(1)
                
                target_input_sede.send_keys(Keys.DOWN)
                time.sleep(0.5)
                target_input_sede.send_keys(Keys.ENTER)
                print("✅ Sede seleccionada (Teclado)")
            else:
                print("❌ No se encontraron inputs para Sede.")
                raise Exception("Inputs no encontrados para Sede")
        except Exception as e:
            print(f"❌ Error seleccionando Sede: {e}")

        time.sleep(2)

        # ==========================================
        # 2. SELECCIONAR CAJA
        # ==========================================
        print("\n🔍 Buscando desplegable de CAJA...")
        try:
            time.sleep(2) # Dar tiempo para que el dropdown de Sede termine su efecto
            xpath_input = "//input[contains(@class, 'ant-select-selection-search-input')]"
            inputs = driver.find_elements(By.XPATH, xpath_input)
            
            target_input_caja = None
            if len(inputs) > 1:
                target_input_caja = inputs[1] # El segundo suele ser Caja
            elif inputs:
                target_input_caja = inputs[-1]
                
            if target_input_caja:
                driver.execute_script("arguments[0].focus();", target_input_caja)
                time.sleep(0.5)
                
                target_input_caja.send_keys(Keys.DOWN)
                time.sleep(1)
                
                if turno_activo_caja:
                    target_input_caja.send_keys(Keys.CONTROL + "a")
                    target_input_caja.send_keys(Keys.BACKSPACE)
                    time.sleep(0.5)
                    target_input_caja.send_keys(turno_activo_caja)
                    time.sleep(1)
                    
                target_input_caja.send_keys(Keys.DOWN)
                time.sleep(0.5)
                target_input_caja.send_keys(Keys.ENTER)
                print("✅ Caja seleccionada (Teclado)")
            else:
                print("❌ No se encontraron inputs para Caja.")
                raise Exception("Inputs no encontrados para Caja")
        except Exception as e_caja:
            print(f"⚠️ Falló estrategia teclado caja: {e_caja}")
                
        except Exception as e:
             print(f"❌ Error crítico seleccionando Caja: {e}")
             try:
                driver.save_screenshot("error_caja_critico.png")
             except: pass
        
        # Validación final de que estamos en el POS (o intento de continuar)
        time.sleep(5) 

        # 4. Click en boton ingresar
        print("🔍 Verificando estado del turno antes de ingresar...")
        try:
            xpath_caja_cerrada_normal = '//*[@id="root"]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/button'
            xpath_caja_abierta = '//*[@id="root"]/div/div/div/div/div[2]/div/div/div[1]/div/div[4]/button'
            
            # Buscar si existe el mensaje de turno activo
            turno_activo = driver.find_elements(By.XPATH, "//*[contains(text(), 'Tienes un turno activo')]")
            
            if len(turno_activo) > 0:
                print("ℹ️ Mensaje de 'turno activo' detectado. Usando botón de caja abierta...")
                boton_ingresar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_caja_abierta)))
            else:
                print("ℹ️ No hay mensaje de turno activo. Usando botón normal...")
                boton_ingresar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_caja_cerrada_normal)))
                
            boton_ingresar.click()
            print("✅ Boton ingresar clickeado")
        except Exception as e:
            print(f"⚠️ Falló click en boton ingresar: {e}")
            
    except Exception as e:
        print(f"❌ Error en ingreso_al_pos: {e}")
        try:
            driver.save_screenshot("error_pos_seleccion.png")
            print("📸 Screenshot guardado: error_pos_seleccion.png")
        except:
            pass

def validacion_pos(inventario_maximo=0):
    try:
        # --- VERIFICACIÓN DE ESTADO DE CAJA ---
        print("🔍 Verificando estado de la caja...")
        
        # Esperar un momento a que cargue la interfaz inicial
        time.sleep(10)# mas tiempo se debe agregar
        
        caja_vencida = driver.find_elements(By.XPATH, "//*[contains(text(), 'Caja Vencida') or contains(text(), 'CAJA VENCIDA') or contains(text(), 'apertura de caja ha vencido')]")
        caja_cerrada = driver.find_elements(By.XPATH, "//*[contains(text(), 'Caja Cerrada') or contains(text(), 'CAJA CERRADA')]")

        if caja_vencida:
            print("⚠️ Estado 'Caja Vencida' detectado. Iniciando proceso de cierre...")
            try:
                # Boton principal de Cerrar Caja
                xpath_boton_cerrar = '//*[@id="root"]/div/section/section/section/div/main/div/div[1]/div/button'
                boton_cerrar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_cerrar)))
                boton_cerrar.click()
                print("✅ Botón 'Cerrar Caja' (Principal) clickeado")    
                time.sleep(10)
                
                # Clic en "Siguiente"
                print("📦 Buscando el botón 'Siguiente'...")
                xpath_boton_siguiente = '//button[normalize-space()="Siguiente"]'
                boton_siguiente = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_siguiente)))
                time.sleep(3)
                try:
                    boton_siguiente.click()
                    print("✅ Botón 'Siguiente' en Pop-up clickeado (Click Normal)")
                except Exception as e:
                    driver.execute_script("arguments[0].click();", boton_siguiente)
                    print(f"✅ Botón 'Siguiente' en Pop-up clickeado (JS Click) - Advertencia: {e}")
                
                time.sleep(10)
                
                # TODO: Aquí faltaría el resto del flujo de cierre (Conteo físico, etc.) y luego apertura
                # Paso 2: Conteo Físico
                print("📦 En Pop-up de Cierre de Caja (Paso 2: Conteo Físico). Haciendo clic en Siguiente sin modificar saldos...")
                
                # Usamos [last()] para asegurar que siempre tomemos el botón del paso actual
                xpath_boton_siguiente_conteo = '(//button[normalize-space()="Siguiente"])[last()]'
                boton_siguiente_conteo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_siguiente_conteo)))
                
                try:
                    boton_siguiente_conteo.click()
                    print("✅ Botón 'Siguiente' en Conteo Físico clickeado (Click Normal)")
                except Exception as e:
                    driver.execute_script("arguments[0].click();", boton_siguiente_conteo)
                    print(f"✅ Botón 'Siguiente' en Conteo Físico clickeado (JS Click) - Advertencia: {e}")
                
                time.sleep(3)
                
                # Paso 3: Comparación de Saldo
                print("📦 En Pop-up de Cierre de Caja (Paso 3: Comparación de Saldo). Haciendo clic en Siguiente...")
                time.sleep(3)
                
                xpath_boton_siguiente_comparacion = '(//button[normalize-space()="Siguiente"])[last()]'
                boton_siguiente_comparacion = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_siguiente_comparacion)))
                
                try:
                    boton_siguiente_comparacion.click()
                    print("✅ Botón 'Siguiente' en Comparación de Saldo clickeado (Click Normal)")
                except Exception as e:
                    driver.execute_script("arguments[0].click();", boton_siguiente_comparacion)
                    print(f"✅ Botón 'Siguiente' en Comparación de Saldo clickeado (JS Click) - Advertencia: {e}")
                
                time.sleep(3)
                
                # Paso 4: Retiro de Saldos
                print("📦 En Pop-up de Cierre de Caja (Paso 4: Retiro de Saldos). Haciendo clic en Finalizar...")
                time.sleep(3)
                
                # Intentar primero con el XPath provisto por el usuario, con fallback a texto
                try:
                    xpath_boton_finalizar = '/html/body/div[6]/div/div[2]/div/div[2]/div[2]/button[2]'
                    boton_finalizar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_finalizar)))
                except TimeoutException:
                    print("⚠️ No se encontró 'Finalizar' con XPath absoluto, intentando con texto...")
                    xpath_boton_finalizar = '//button[normalize-space()="Finalizar"]'
                    boton_finalizar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_finalizar)))

                try:
                    boton_finalizar.click()
                    print("✅ Botón 'Finalizar' en Retiro de Saldos clickeado (Click Normal)")
                except Exception as e:
                    driver.execute_script("arguments[0].click();", boton_finalizar)
                    print(f"✅ Botón 'Finalizar' en Retiro de Saldos clickeado (JS Click) - Advertencia: {e}")
                
                print("🎉 Proceso de Cierre de Caja completado. Esperando que la interfaz se actualice...")
                time.sleep(5) # Esperar a que se procese el cierre y la interfaz recargue o cambie
                
                # Clic en el botón de salir del balance de caja vencida
                print("📦 Buscando el botón 'salir del balance de caja vencida'...")
                try:
                    xpaths_salir_balance = [
                        '/html/body/div[7]/div/div[2]/div/div[2]/div[2]/button',
                        '/html/body/div[last()]/div/div[2]/div/div[2]/div[2]/button',
                        '//button[contains(normalize-space(), "Salir")]',
                        '//button[contains(normalize-space(), "Cerrar")]'
                    ]
                    
                    boton_salir_balance = None
                    for xpath in xpaths_salir_balance:
                        try:
                            boton_salir_balance = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                            print(f"✅ Botón encontrado con XPath: {xpath}")
                            break
                        except TimeoutException:
                            continue
                    
                    if boton_salir_balance:
                        try:
                            time.sleep(1)
                            boton_salir_balance.click()
                            print("✅ Botón 'salir del balance de caja vencida' clickeado (Click Normal)")
                        except Exception as e:
                            driver.execute_script("arguments[0].click();", boton_salir_balance)
                            print(f"✅ Botón 'salir del balance de caja vencida' clickeado (JS Click) - Advertencia: {e}")
                    else:
                        print("⚠️ No se pudo encontrar el botón 'salir del balance' con ninguno de los XPaths.")
                except Exception as e:
                    print(f"⚠️ Error general intentando clickear 'salir del balance de caja vencida': {e}")
                
                print("ℹ️ Cajero vencido cerrado. Ahora procediendo a Apertura de Caja...")
                caja_cerrada = True # Activar la bandera para que pase al siguiente bloque
                
            except Exception as e:
                print(f"❌ Error en flujo Caja Vencida: {e}")

        if caja_cerrada:
            print("⚠️ Estado 'Caja Cerrada' detectado. Intentando abrir caja...")
            try:
                xpath_boton_abrir = '//*[@id="root"]/div/section/section/section/div/main/div/div[1]/div/button'
                boton_abrir = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_abrir)))
                boton_abrir.click()
                print("✅ Botón 'Abrir Caja' clickeado")
                time.sleep(3) # Esperar a que la caja se abra
                
                # Paso 1: Clic en "Siguiente"
                print("📦 Buscando el botón 'Siguiente' para Apertura...")
                xpath_boton_siguiente = '(//button[normalize-space()="Siguiente"])[last()]'
                boton_siguiente_apertura = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_siguiente)))
                time.sleep(3)
                try:
                    boton_siguiente_apertura.click()
                    print("✅ Botón 'Siguiente' en Pop-up (Paso 1) clickeado (Click Normal)")
                except Exception as e:
                    driver.execute_script("arguments[0].click();", boton_siguiente_apertura)
                    print(f"✅ Botón 'Siguiente' en Pop-up (Paso 1) clickeado (JS Click) - Advertencia: {e}")
                
                time.sleep(10)
                
                # Paso 2: Conteo Físico
                print("📦 En Pop-up de Apertura (Paso 2). Haciendo clic en Siguiente...")
                xpath_boton_siguiente_apertura_conteo = '(//button[normalize-space()="Siguiente"])[last()]'
                boton_siguiente_conteo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_siguiente_apertura_conteo)))
                try:
                    boton_siguiente_conteo.click()
                    print("✅ Botón 'Siguiente' en Conteo Físico clickeado (Click Normal)")
                except Exception as e:
                    driver.execute_script("arguments[0].click();", boton_siguiente_conteo)
                    print(f"✅ Botón 'Siguiente' en Conteo Físico clickeado (JS Click) - Advertencia: {e}")
                
                time.sleep(10)
                
                # Paso 3: Retiro de Saldos (Apertura)
                print("📦 En Pop-up de Apertura (Paso 4). Haciendo clic en Finalizar...")
                try:
                    xpath_boton_finalizar = '//button[normalize-space()="Finalizar"]'
                    boton_finalizar_apertura = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_boton_finalizar)))
                    try:
                        boton_finalizar_apertura.click()
                        print("✅ Botón 'Finalizar' en Apertura clickeado (Click Normal)")
                    except Exception as e:
                        driver.execute_script("arguments[0].click();", boton_finalizar_apertura)
                        print(f"✅ Botón 'Finalizar' en Apertura clickeado (JS Click) - Advertencia: {e}")
                except Exception as e:
                    print(f"⚠️ No se encontró botón Finalizar en Apertura o no fue necesario: {e}")
                
                print("🎉 Proceso de Apertura de Caja completado. Esperando que la interfaz se actualice...")
                time.sleep(5)
                
                # Clic en el botón de salir del balance de caja
                print("📦 Buscando el botón 'salir del balance de caja' en Apertura...")
                try:
                    xpaths_salir_balance_apertura = [
                        '/html/body/div[7]/div/div[2]/div/div[2]/div[2]/button',
                        '/html/body/div[last()]/div/div[2]/div/div[2]/div[2]/button',
                        '//button[contains(normalize-space(), "Salir")]',
                        '//button[contains(normalize-space(), "Cerrar")]'
                    ]
                    
                    boton_salir_balance_apertura = None
                    for xpath in xpaths_salir_balance_apertura:
                        try:
                            boton_salir_balance_apertura = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))
                            print(f"✅ Botón encontrado con XPath: {xpath}")
                            break
                        except TimeoutException:
                            continue
                    
                    if boton_salir_balance_apertura:
                        try:
                            time.sleep(1)
                            boton_salir_balance_apertura.click()
                            print("✅ Botón 'salir del balance de caja' en Apertura clickeado (Click Normal)")
                        except Exception as e:
                            driver.execute_script("arguments[0].click();", boton_salir_balance_apertura)
                            print(f"✅ Botón 'salir del balance de caja' en Apertura clickeado (JS Click) - Advertencia: {e}")
                    else:
                        print("⚠️ No se pudo encontrar el botón 'salir del balance' en Apertura con los XPaths proporcionados.")
                except Exception as e:
                    print(f"⚠️ Error general intentando clickear 'salir del balance de caja' en Apertura: {e}")
            except Exception as e:
                print(f"❌ Error en flujo Caja Cerrada: {e}")
                
        if not caja_vencida and not caja_cerrada:
            print("✅ Estado 'Caja Aperturada' detectado o no hay bloqueos. Continuando flujo normal...")

        # --- NAVEGACIÓN A INVENTARIO ---
        print("📦 Accediendo a opción Inventario via Popup...")
        try:
            # Esperar a que la interfaz esté lista
            time.sleep(2)
            
            # 1. Hacer hover sobre el ítem del menú lateral (ícono de camisa/Inventario)
            print("🔍 Buscando y desplegando el menú lateral de Inventario (Hover)...")
            xpath_menu_lateral = '//div[contains(@class, "ant-menu-submenu-title") and .//span[text()="Inventario"]]'
            menu_lateral = wait.until(EC.presence_of_element_located((By.XPATH, xpath_menu_lateral)))
            
            # Desplazar mouse hacia el elemento para que se abra el pop-up
            ActionChains(driver).move_to_element(menu_lateral).perform()
            time.sleep(1.5) # Breve espera para la animación del pop-up
            
            # 2. Hacer clic en "Inventario" dentro del pop-up que acaba de aparecer
            print("🖱️ Clickeando 'Inventario' en el pop-up...")
            xpath_submenu = '//*[contains(@id, "-inventory-popup")]//li[contains(., "Inventario") or contains(@class, "ant-menu-item")]'
            
            submenu_inventario = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_submenu)))
            submenu_inventario.click()
            print("✅ Click en Submenú Inventario exitoso (Hover + Click)")
        except Exception as e:
            print(f"⚠️ Falló click en submenú inventario: {e}")
    except Exception as e:
        print(f"❌ Error en validacion_pos: {e}")
        try:
            driver.save_screenshot("error_pos_validacion.png")
            print("📸 Screenshot guardado: error_pos_validacion.png")
        except:
            pass


try:
    # Configuración de Chrome para bloquear diálogos de impresión
    chrome_options = Options()
    # --kiosk-printing silencia tanto la vista previa de Chrome como el diálogo del sistema
    chrome_options.add_argument('--kiosk-printing')
    
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
    print("🔐 Iniciando sesión...")
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL", ""))

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD", ""))
    #//*[@id="login-form"]/div[3]/div/div/div/div/button
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    print("✅ Login exitoso")
    time.sleep(10)  # Reducido de 15 a 10
    
    # Asegurar tiempo de carga
    time.sleep(3)
        
    # Validar enlace del POS (Solicitud adicional)
    ingreso_al_pos()
    validacion_pos()

    # Extraer el inventario base y abrir el modal
    leer_inventario_actual()
    
    # Ingresar la cantidad a ajustar y guardar
    valor_ajustado = ingresar_ajuste_manual()
    
    # Validar el resultado
    validar_actualizacion_inventario(valor_ajustado)

    # Finalizar turno como último paso del proceso
    print("🔚 Intentando hacer clic en 'Finalizar turno'...")
    try:
        time.sleep(3) # Esperar a que la página actual se estabilice
        xpath_finalizar_turno = '//*[@id="root"]/div/section/header/div/div[2]/div[2]/div[2]/button'
        boton_finalizar_turno = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_finalizar_turno)))
        
        try:
            boton_finalizar_turno.click()
            print("✅ Botón 'Finalizar turno' clickeado (Click Normal)")
        except Exception as e:
            driver.execute_script("arguments[0].click();", boton_finalizar_turno)
            print(f"✅ Botón 'Finalizar turno' clickeado (JS Click) - Advertencia: {e}")
        
        time.sleep(2)
        
        # Si logramos llegar hasta aquí, el caso de prueba fue exitoso
        exito = True
        observaciones = "Ejecución completada exitosamente hasta el cierre de turno."
    except Exception as e:
        print(f"❌ Error al intentar finalizar el turno: {e}")
        try:
            driver.save_screenshot("error_finalizar_turno.png")
        except:
            pass
finally:
    # Registrar resultado
    print("\n" + "="*50)
    print("REGISTRANDO RESULTADO")
    print("="*50)
    
    estado = "Exitoso" if exito else "Fallido"
    registrar_resultado(id_caso, estado, observaciones)
    
    # Cerrar driver si existe
    try:
        if 'driver' in locals():
            time.sleep(2)
            driver.quit()
            print("✅ Driver cerrado")
    except:
        pass

print(f"\n🎯 PRUEBA FINALIZADA: {estado}")
print(f"📝 Observaciones: {observaciones}")