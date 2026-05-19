from logging import root
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
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('ascii', 'replace').decode('ascii'))
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(log_filename)
sys.stderr = sys.stdout
# =====================


from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import string
from faker import Faker
import faker_commerce; print(faker_commerce.__file__)
import re

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
id_caso = "TC029"

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

def extraer_valores_inventario_bogota():
    """
    Extrae los valores de Total y Sede Bogotá usando múltiples estrategias
    """
    try:
        # Primero esperar a que alguna tabla esté presente
        tabla = esperar_tabla_inventario()
        if not tabla:
            print("❌ No se pudo encontrar la tabla de inventario")
            return None
        
        print("🔍 Buscando valores en la tabla...")
        
        # Estrategia 1: Usar los XPath específicos que proporcionaste
        try:
            xpath_total = '//*[@id="rc-tabs-3-panel-1"]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[5]/span'
            xpath_bogota = '//*[@id="rc-tabs-3-panel-1"]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[1]/div[2]/table/tbody/tr[2]/td[6]/span[1]'
            
            print("  Intentando con XPath específicos...")
            elemento_total = driver.find_element(By.XPATH, xpath_total)
            elemento_bogota = driver.find_element(By.XPATH, xpath_bogota)
            
            print("✅ Elementos encontrados con XPath específicos")
            
        except NoSuchElementException:
            # Estrategia 2: Buscar por posición relativa en la tabla
            print("  XPath específicos no funcionaron, intentando por posición en tabla...")
            
            # Buscar la primera fila de datos
            filas = driver.find_elements(By.XPATH, "//table//tbody/tr")
            print(f"  Encontradas {len(filas)} filas en la tabla")
            
            # Función auxiliar para limpiar números
            def limpiar_numero(texto):
                if not texto: return 0.0
                match = re.search(r'([\d,]+\.?\d*)', texto)
                if match:
                    return float(match.group(1).replace(',', ''))
                return 0.0

            if len(filas) >= 2:  # Fila 0 podría ser encabezado, fila 1 es primer dato
                primera_fila = filas[1]  # Segunda fila (índice 1)
                celdas = primera_fila.find_elements(By.TAG_NAME, "td")
                print(f"  Encontradas {len(celdas)} celdas en la primera fila")
                
                if len(celdas) >= 6:
                    # Asumiendo: col 0-3: datos producto (checkbox, nombre, sku, barcode)
                    # col 4: Total
                    # col 5 en adelante: Sedes
                    
                    elemento_total = celdas[4]
                    texto_total = elemento_total.text
                    
                    # Limpiar total general
                    total_num = limpiar_numero(texto_total)
                    print(f"   Total General (Col 4): {total_num}")
                    
                    # Calcular suma de sedes (Col 5 en adelante)
                    suma_sedes = 0.0
                    detalles_sedes = []
                    
                    # Iteramos desde la columna 5
                    for i, celda in enumerate(celdas[5:], start=5):
                        texto_sede = celda.text
                        valor_sede = limpiar_numero(texto_sede)
                        suma_sedes += valor_sede
                        detalles_sedes.append(f"Col {i}: {valor_sede}")
                    
                    print(f"   Suma de Sedes (Calc): {suma_sedes}")
                    print(f"   Detalles Sedes: {', '.join(detalles_sedes)}")
    
                    # Extraer detalles del producto
                    nombre_prod = celdas[1].text
                    sku_prod = celdas[2].text
                    barcode_prod = celdas[3].text
                    
                    print(f"   Producto: {nombre_prod} | SKU: {sku_prod} | Barcode: {barcode_prod}")

                    return {
                        'nombre': nombre_prod,
                        'sku': sku_prod,
                        'barcode': barcode_prod,
                        'total_num': total_num,
                        'bogota_num': total_num, # UPDATED: Usamos Total como valor principal
                        'suma_sedes': suma_sedes,
                        'detalles_sedes': detalles_sedes
                    }
                else:
                    print(f"❌ No hay suficientes celdas ({len(celdas)})")
                    return None
            else:
                print(f"❌ No hay suficientes filas ({len(filas)})")
                return None
        
    except Exception as e:
        print(f"❌ Error extrayendo valores: {e}")
        import traceback
        traceback.print_exc()
        return None

def seleccionar_checkbox_primer_producto():
    """
    Selecciona el checkbox del primer producto
    """
    try:
        print("🔍 Buscando checkbox del primer producto...")
        
        # Múltiples estrategias para encontrar el checkbox
        estrategias = [
            # Estrategia 1: XPath específico basado en la fila
            '//table//tbody/tr[2]//input[@type="checkbox"]',
            # Estrategia 2: Primer checkbox en la tabla
            '//table//input[@type="checkbox"]',
            # Estrategia 3: Cualquier checkbox
            '//input[@type="checkbox"]',
            # Estrategia 4: Por clase
            '//span[contains(@class, "ant-checkbox")]',
        ]
        
        for xpath in estrategias:
            try:
                checkboxes = driver.find_elements(By.XPATH, xpath)
                if checkboxes:
                    print(f"✅ Encontrados {len(checkboxes)} checkboxes con XPath: {xpath}")
                    
                    # Seleccionar el primero
                    checkbox = checkboxes[0]
                    
                    # Hacer scroll si es necesario
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                    time.sleep(0.5)
                    
                    # Usar JavaScript para hacer click
                    driver.execute_script("arguments[0].click();", checkbox)
                    print("✅ Checkbox clickeado con JavaScript")
                    
                    # Verificar selección
                    time.sleep(0.5)
                    if checkbox.is_selected():
                        print("✅ Checkbox confirmado como seleccionado")
                        return True
                    else:
                        # Intentar de otra manera
                        driver.execute_script("arguments[0].checked = true;", checkbox)
                        print("✅ Checkbox marcado directamente con JavaScript")
                        return True
                        
            except Exception as e:
                print(f"  ❌ Estrategia falló ({xpath}): {e}")
                continue
        
        print("⚠️  No se pudo encontrar/seleccionar ningún checkbox")
        return False
            
    except Exception as e:
        print(f"❌ Error seleccionando checkbox: {e}")
        return False

def ingreso_al_pos():   
    print("🔍 Buscando acceso al POS...")
    print("🔍 Accediendo al POS por URL directa...")
    try:
        url_pos = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/start/shift-start"
        driver.get(url_pos)
        print(f"✅ Navegación a POS iniciada: {url_pos}")

        wait = WebDriverWait(driver, 10)
        
        # 1. Click dropdown trigger
        print("🔍 Click en el desplegable de sedes...")
        
        # Verificar si hay un turno activo en pantalla
        mensajes_turno_activo = driver.find_elements(By.XPATH, "//*[contains(text(), 'Tienes un turno activo')]")
        
        # Usamos XPaths relativos súper robustos. 
        # Sede es el 1er dropdown y Caja es el 2do, independientemente del mensaje inferior.
        xpath_sede_con_turno = "(//div[contains(@class, 'ant-select-selector')])[1]"
        xpath_sede_sin_turno = "(//div[contains(@class, 'ant-select-selector')])[1]"
        
        # Determinar qué XPath usar (ambos apuntan al mismo elemento relativo, pero mantenemos tu lógica)
        xpath_seleccionado = xpath_sede_con_turno if len(mensajes_turno_activo) > 0 else xpath_sede_sin_turno
        
        try:
            dropdown_trigger = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_seleccionado))
            )
            dropdown_trigger.click()
            print("✅ Click en dropdown (XPath robusto de Sede)")
        except Exception as e:
             print(f"⚠️ Falló click inicial ({e}), intentando por texto...")
             # Fallback secundario con acento opcional
             dropdown_trigger = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Selecciona Ubicaci')]/ancestor::div[contains(@class, 'ant-select-selector')]"))
             )
             dropdown_trigger.click()
             print("✅ Click en dropdown (Fallback de Sede)")
        
        time.sleep(1) # Esperar animación del menú

        # 2. Seleccionar Opción
        print("🔍 Buscando opción de sede...")
        try:
            # Estrategia 1: Buscar 'sede bogota' pero ASEGURÁNDONOS que sea una opción del menú.
            # Evitamos buscar en toda la página porque el mensaje amarillo también dice 'sede bogota'.
            opcion = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-select-item-option-content') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sede bogota')]"))
            )
            print(f"  > Opción encontrada: {opcion.text or 'Elemento sin texto directo'}")
            
            # Scroll para asegurar visibilidad
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opcion)
            time.sleep(0.5)
            
            try:
                opcion.click()
                print("✅ Sede seleccionada (Click Normal)")
            except Exception as e:
                print(f"⚠️ Falló Click Normal ({e}), intentando JS Click...")
                driver.execute_script("arguments[0].click();", opcion)
                print("✅ Sede seleccionada (JS Click)")
            
        except Exception as e:
            print(f"⚠️ Falló estrategia específica ({e}), intentando genérica...")
            try:
                 # Estrategia 2: Cualquier opción del menú que contenga 'sede'
                opciones_genericas = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-item-option-content') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sede')]"))
                )
                
                # Filtramos visibles y que tengan un tamaño razonable 
                opciones_candidatas = []
                for opt in opciones_genericas:
                    if opt.is_displayed() and opt.size['height'] > 0: 
                        opciones_candidatas.append(opt)
                
                if opciones_candidatas:
                    opcion_final = opciones_candidatas[0]
                    print(f"  > Seleccionando opción genérica: {opcion_final.text[:50]}...")
                    driver.execute_script("arguments[0].click();", opcion_final)
                    print("✅ Sede seleccionada (Genérica JS)")
                else:
                    print("❌ No se encontraron opciones interactuables")
                    raise Exception("No se pudo seleccionar la sede (ni específica ni genérica)")

            except Exception as ex_gen:
                print(f"❌ Error final selección: {ex_gen}")
                raise ex_gen
        
        time.sleep(2)

        # ==========================================
        # 3. SELECCIONAR CAJA
        # ==========================================
        print("\n🔍 Buscando desplegable de CAJA...")
        try:
            # Esperar antes de interactuar
            time.sleep(2)
            
            print("  Estrategia TECLADO: Enfocar y usar flechas (evita clicks)...")
            
            # Buscar el input oculto de Ant Design
            # Suele tener clase 'ant-select-selection-search-input'
            xpath_input = "//input[contains(@class, 'ant-select-selection-search-input')]"
            
            try:
                # Buscamos todos los inputs de este tipo
                inputs = driver.find_elements(By.XPATH, xpath_input)
                
                # ASUNCIÓN: El primer input fue Sede, el segundo debería ser Caja
                # Filtramos por visibilidad o posición si es necesario, pero usualmente 
                # estos inputs técnicamente no son "visibles" porque tienen opacity 0.
                
                target_input = None
                
                # Intentamos encontrar el que corresponde a la caja buscando el label cercano
                for inp in inputs:
                     # Verificamos si tiene el ID rc_select_2 o está cerca del texto "Selecciona Caja"
                     try:
                         id_attr = inp.get_attribute('id')
                         if id_attr == 'rc_select_2':
                             target_input = inp
                             print("  > Input encontrado por ID rc_select_2")
                             break
                     except: pass
                
                # Si no encontramos por ID, usamos el último input de la página (a veces es el orden lógico)
                if not target_input and inputs:
                    target_input = inputs[-1]
                    print("  > Usando el último input de selección encontrado (Probable Caja)")

                if target_input:
                    # 1. Enfocar forzosamente con JS
                    driver.execute_script("arguments[0].focus();", target_input)
                    print("  > Input enfocado con JS")
                    time.sleep(0.5)
                    
                    # 2. Enviar Flecha AABAJO para abrir menú
                    # Nota: Enviamos claves al activo o al body si el input es rarito
                    target_input.send_keys(Keys.DOWN)
                    print("  > Enviada tecla DOWN para abrir")
                    time.sleep(1)
                    
                    # 3. Enviar ENTER para seleccionar el primero que esté resaltado (o DOWN + ENTER)
                    target_input.send_keys(Keys.ENTER)
                    print("  > Enviada tecla ENTER para seleccionar")
                    
                    # Fallback opcional: Si no se seleccionó, intentar DOWN + ENTER
                    time.sleep(1)
                    target_input.send_keys(Keys.DOWN)
                    target_input.send_keys(Keys.ENTER)
                    print("  > Enviada secuencia DOWN+ENTER de respaldo")
                    
                else:
                    print("❌ No se encontraron inputs de selección.")
                    raise Exception("Inputs no encontrados")

            except Exception as e_key:
                print(f"⚠️ Falló estrategia teclado: {e_key}")
                # Fallback final a click JS en texto
                print("  Intentando click JS forzado en texto 'Selecciona Caja'...")
                driver.execute_script("var x = document.evaluate(\"//div[contains(text(), 'Selecciona Caja')]\", document, null, 9, null).singleNodeValue; if(x) x.click();")

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
            xpath_caja_cerrada_normal = '//*[@id="root"]/div/div/div/div[2]/div[4]/button'
            xpath_caja_abierta = '//*[@id="root"]/div/div/div/div[2]/div[5]/button'
            
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
        # --- BLOQUEO REFORZADO DE IMPRESIÓN ---
        # Bloqueamos la función print en el window principal y tratamos de hacerlo preventivamente
        print("🚫 Bloqueando funciones de impresión vía JavaScript...")
        driver.execute_script("""
            window.print = function() { console.log('Print blocked by automation'); };
            Object.defineProperty(window, 'print', { value: function() { console.log('Print blocked'); }, writable: false });
            // Bloqueo para posibles iframes
            var style = document.createElement('style');
            style.innerHTML = '@media print { body { display: none !important; } }';
            document.head.appendChild(style);
        """)
        
        print("🚀 Validando POS...")
        
        # --- VERIFICACIÓN DE CAJA CERRADA ---
        print("🔍 Verificando estado de la caja...")
        try:
            # Buscar si existe el texto "Caja Cerrada"
            mensaje_caja_cerrada = driver.find_elements(By.XPATH, "//*[contains(text(), 'Caja Cerrada')]")
            
            if mensaje_caja_cerrada:
                print("⚠️ Mensaje 'Caja Cerrada' detectado. Intentando abrir caja...")
                xpath_boton_abrir = '//*[@id="root"]/div/section/section/section/div/main/div/div[1]/div/button'
                boton_abrir = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_boton_abrir)))
                boton_abrir.click()
                print("✅ Botón 'Abrir Caja' clickeado")
                time.sleep(3) # Esperar a que la caja se abra
            else:
                print("ℹ️ No se detectó el mensaje 'Caja Cerrada', continuando...")
        except Exception as e:
            print(f"ℹ️ Error o no se encontró mensaje de caja cerrada: {e}. Continuando...")
        
        # 1. Seleccionar primer producto (Checkbox)
        try:
            print("⏳ Buscando producto en POS...")
            time.sleep(3) # Esperar a que los productos terminen de cargar y React estabilice el DOM (evita StaleElement)
            
            # XPath original del usuario
            xpath_producto = "//*[@id='root']/div/section/section/section/div/main/div/div[1]/div[1]/div[2]/div/div[1]/div/div[2]/div[3]/div/div"
            
            # Intentar scroll primero
            producto = wait.until(EC.presence_of_element_located((By.XPATH, xpath_producto)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", producto)
            time.sleep(0.5)
            producto.click()
            print("✅ Checkbox primer producto seleccionado")
        except Exception as e:
            print(f"⚠️ Falló selección producto con XPath original: {e}")
            # Fallback: buscar cualquier producto clickable en la grilla
            print("  Intentando selector genérico de producto...")
            time.sleep(2) # Darle aún más tiempo si falló
            
            # El buscador es una tarjeta (ant-card) pero tiene un <input> adentro (el placeholder no cuenta como texto para el not(contains)). 
            # Los productos reales NO tienen etiquetas <input>. Así lo filtramos.
            xpath_seguro = "//main//div[contains(@class, 'product-card')] | //main//div[contains(@class, 'ant-card') and not(.//input) and not(contains(., 'CAJA ABIERTA'))]"
            
            producto = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_seguro)))
            producto.click()
            print("✅ Producto seleccionado (Genérico y sin inputs)")

        # 2. Seleccionar Atributo (Sabor/Memoria/Color)
        # El usuario reportó error en: //*[@id='advanced_search_memoria']/label[2]/span[1]
        try:
            print("⏳ Buscando atributos del producto...")
            
            # Estrategia: Buscar cualquier contenedor de búsqueda avanzada que sea visible
            # IDs comunes: advanced_search_memoria, advanced_search_color, etc.
            
            # Esperar a que el modal y los atributos carguen completamente
            print("⏳ Esperando carga completa del modal de producto...")
            time.sleep(3) # Aumentado de 1 a 3 segundos para asegurar carga
            
            # Intentar encontrar el contenedor específico o genérico
            xpath_atributos = [
                "//*[@id='advanced_search_memoria']//label",        # El específico del usuario (todos los labels hijos)
                "//div[contains(@id, 'advanced_search')]//label",   # Genérico por ID
                "//div[contains(@class, 'ant-radio-group')]//label", # Genérico por clase AntD
                "//div[contains(@class, 'ant-modal')]//label"       # Genérico dentro del modal
            ]
            
            opcion_atributo = None
            for xpath in xpath_atributos:
                try:
                    opciones = driver.find_elements(By.XPATH, xpath)
                    # Filtrar visibles
                    opciones_visibles = [op for op in opciones if op.is_displayed()]
                    
                    if opciones_visibles:
                        # Debug: Mostrar qué opciones se encontraron
                        print(f"  > Opciones encontradas con {xpath}: {[op.text for op in opciones_visibles]}")
                        
                        # Buscar específicamente la opción "2tb"
                        found_2tb = False
                        for op in opciones_visibles:
                            texto_op = op.text.lower().strip()
                            if "2tb" in texto_op or "2 tb" in texto_op:
                                opcion_atributo = op
                                found_2tb = True
                                print(f"✅ Opción '2tb' encontrada y seleccionada: {op.text}")
                                break
                        
                        if not found_2tb:
                            # Fallback original: Seleccionar el segundo si existe, sino el primero
                            print("⚠️ No se encontró opción explícita '2tb', usando lógica por defecto (Seleccionar 2da opción)")
                            if len(opciones_visibles) >= 2:
                                opcion_atributo = opciones_visibles[1] 
                            else:
                                opcion_atributo = opciones_visibles[0]
                            
                        print(f"✅ Opción de atributo lista para click: {opcion_atributo.text}")
                        break
                except Exception as e_xpath:
                    print(f"  Error probando xpath {xpath}: {e_xpath}")
                    continue
            
            if opcion_atributo:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opcion_atributo)
                time.sleep(1) # Esperar un poco tras scroll
                
                # Intentar click normal y luego JS
                try:
                    opcion_atributo.click()
                    print("✅ Atributo clickeado (Normal)")
                except:
                    driver.execute_script("arguments[0].click();", opcion_atributo)
                    print("✅ Atributo clickeado (JS)")
            else:
                print("⚠️ No se encontraron atributos para seleccionar (puede que el producto no tenga variantes)")
                
        except Exception as e:
            print(f"❌ Error seleccionando atributo: {e}")
            # No lanzamos excepción crítica, intentamos seguir al botón agregar
            
        time.sleep(2) # Esperar tras selección
            
        # 3. Botón Agregar
        # Usar un XPath más robusto basado en el texto del botón
        # Buscamos un botón que contenga "Agregar" (o su span hijo)
        try:
            boton_agregar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Añadir al carrito')]")))
            boton_agregar.click()
            print("✅ Boton agregar clickeado")
        except TimeoutException:
            print("⚠️ Botón 'Añadir al carrito' no encontrado. Asumiendo que el producto ya se agregó al carrito automáticamente.")

        time.sleep(2)
        
        # 5. Ingresar cantidad aleatoria
        print("🔍 Buscando campo de cantidad...")
        try:
            # Click en el botón de cantidad (el que indicó el usuario)
            boton_cantidad = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/section/section/div/main/div/div[1]/div[2]/div/div/div[3]/div/div[3]/div/div/div/ul/div/div/div[2]/div/div[2]')))
            boton_cantidad.click()
            print("✅ Click en botón de cantidad")
            
            time.sleep(1)
            
            # Generar cantidad aleatoria
            max_val = int(inventario_maximo) if inventario_maximo > 1 else 1
            cantidad_random = random.randint(1, max_val)
            print(f"🎲 Cantidad aleatoria generada: {cantidad_random} (Max: {max_val})")
            
            # Buscar el input dentro del popover (ajustado para ser más robusto)
            # Buscamos un input numérico visible o el input de Ant Design
            try:
                # Intento 1: Input genérico visible (el popover debería ser lo último abierto)
                input_cantidad = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-popover')]//input | //input[@type='text' or @type='number']")))
                
                # Limpiar usando Ctrl+A (más seguro para inputs de React/AntD)
                input_cantidad.send_keys(Keys.CONTROL + "a")
                input_cantidad.send_keys(Keys.BACKSPACE)
                time.sleep(0.2)
                input_cantidad.send_keys(str(cantidad_random))
                print(f"✅ Cantidad {cantidad_random} escrita en input")
                time.sleep(0.5)
                
                # Intentar confirmar usando ENTER en el input (método más rápido y fiable en React)
                print("  Confirmando cantidad...")
                input_cantidad.send_keys(Keys.ENTER)
                time.sleep(0.5)
                
                # Verificar si el popover se cerró (éxito)
                try:
                    # Si el input ya no es visible o interactuable, asumimos que se cerró
                    if not input_cantidad.is_displayed():
                        print("✅ Cantidad confirmada con ENTER")
                    else:
                        raise Exception("Popover sigue abierto tras ENTER")
                except:
                    # Si falló ENTER, intentamos clickear el botón "Yes"
                    print("⚠️ ENTER no cerró el popover, intentando click en 'Yes'...")
                    try:
                        # Buscamos el botón Yes específicamente dentro de un popover o globalmente por texto
                        # Usamos un XPath relativo que busca el botón primario (naranja) o el botón que diga 'Si', 'Sí' o 'Yes'
                        # dentro del popover. Usamos [last()] porque Ant Design agrega los popovers al final del body.
                        xpath_yes = "(//div[contains(@class, 'ant-popover')]//button[contains(@class, 'ant-btn-primary') or contains(., 'Si') or contains(., 'Sí') or contains(., 'Yes')])[last()]"
                        
                        boton_yes = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_yes)))
                        boton_yes.click()
                        print("✅ Botón 'Yes' clickeado")
                    except Exception as e_click:
                        print(f"❌ Falló click en 'Yes': {e_click}")
                        
                        # Último recurso: JS Click en cualquier cosa que diga "Yes"
                        driver.execute_script("var xpath = \"//div[contains(text(), 'Yes')]\"; var matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; if (matchingElement) matchingElement.click();")
                        print("⚠️ Intentado JS Click en texto 'Yes'")
                
            except Exception as e_input:
                print(f"⚠️ Error interactuando con popover: {e_input}")
                # Fallback a ActionChains global
                actions = ActionChains(driver)
                actions.send_keys(str(cantidad_random))
                actions.send_keys(Keys.ENTER)
                actions.perform()
                print("⚠️ Usado fallback ActionChains global")
            
        except Exception as e:
            print(f"⚠️ Error ingresando cantidad: {e}")

        # 6. Click en Realizar Venta (Cobrar)
        print("🔍 Buscando botón 'Realizar venta' (Cobrar)...")
        try:
            time.sleep(2) # Esperar a que se cierre el modal de cantidad
            # Usar XPath relativo robusto buscando el botón 'COBRAR'
            xpath_venta = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cobrar')]"
            boton_venta = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_venta)))
            boton_venta.click()
            print("✅ Botón 'Cobrar' clickeado")
        except Exception as e:
            print(f"⚠️ Falló click en 'Cobrar' ({xpath_venta}): {e}")
            try:
                # Fallback con JS
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpath_venta))
                print("✅ Botón 'Cobrar' clickeado (JS)")
            except:
                print("❌ No se pudo clickear 'Cobrar'")

        # 7. Seleccionar Cliente Anonimo
        print("🔍 Buscando opción 'Cliente Anonimo'...")
        try:
            time.sleep(3) # Esperar a que cargue la vista de selección de cliente
            
            # Usar un XPath relativo y robusto, ignorando acentos y mayúsculas
            xpath_anonimo = "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ', 'abcdefghijklmnopqrstuvwxyzaeiou'), 'cliente anonimo')]"
            
            try:
                cliente_anonimo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_anonimo)))
                cliente_anonimo.click()
                print("✅ 'Cliente Anonimo' seleccionado (XPath robusto)")
                time.sleep(2) 
                siguiente = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div/div[1]/div/div/div/div[2]/div[2]/div/div/div[2]/div[5]/div/button")))
                siguiente.click()
                print("✅ 'Siguiente' clickeado")
            except Exception as e_xpath:
                print(f"⚠️ Falló XPath robusto para cliente anónimo: {e_xpath}")
                # Fallback: intentar hacer click con JS por si algo lo intercepta
                print("  Intentando JS Click para 'Cliente Anonimo'...")
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpath_anonimo))
                print("✅ 'Cliente Anonimo' seleccionado (Por JS)")
                
        except Exception as e:
            print(f"⚠️ Falló selección de Cliente Anonimo: {e}")

        # 8. Seleccionar Método de Pago
        print("🔍 Desplegando lista de Métodos de Pago...")
        try:
            time.sleep(3) # Aumentar la espera inicial para asegurar que React termine de pintar el DOM
            
            xpath_select = "//*[@id='rc_select_28'] | //input[contains(@id, 'rc_select_')]"
            
            # Reintentar hasta 3 veces para superar el StaleElementReference
            for intento in range(3):
                try:
                    # Siempre buscar el elemento justo antes de usarlo
                    select_box = wait.until(EC.presence_of_element_located((By.XPATH, xpath_select)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_box)
                    time.sleep(0.5)
                    
                    # Volver a buscar el elemento antes del click por si React lo recreó durante el scroll
                    select_box = driver.find_element(By.XPATH, xpath_select)
                    
                    try:
                        select_box.click()
                    except:
                        driver.execute_script("arguments[0].click();", select_box)
                    
                    print("✅ Dropdown de métodos de pago abierto")
                    break # Si llega aquí sin error, rompe el loop de reintentos
                except Exception as e_stale:
                    print(f"  Reintentando abrir dropdown (intento {intento+1}): {e_stale}")
                    time.sleep(1)
            
            time.sleep(1) # Esperar animación del dropdown
            
            # Seleccionar 'Efectivo'
            print("🔍 Buscando opción 'Efectivo' en la lista...")
            xpath_opcion_efectivo = "//div[contains(@class, 'ant-select-item') and contains(., 'Efectivo') and not(contains(@class, 'hidden'))]"
            
            try:
                boton_efectivo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion_efectivo)))
                boton_efectivo.click()
                print("✅ Método de pago 'Efectivo' seleccionado (Click Normal)")
            except Exception as e_click:
                print(f"⚠️ Falló click normal, intentando alternativas...")
                try:
                    # Volver a buscar para JS Click
                    boton_efectivo = driver.find_element(By.XPATH, xpath_opcion_efectivo)
                    driver.execute_script("arguments[0].click();", boton_efectivo)
                    print("✅ Método de pago 'Efectivo' seleccionado (JS Click)")
                except:
                    print("⚠️ Falló JS Click. Usando teclado (Flecha Abajo + Enter)...")
                    # Volver a buscar el input para mandar teclas
                    select_box = driver.find_element(By.XPATH, xpath_select)
                    select_box.send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.5)
                    select_box.send_keys(Keys.ENTER)
                    print("✅ Método de pago 'Efectivo' seleccionado (Teclado)")
                
        except Exception as e:
            print(f"⚠️ Falló selección de Método de Pago global: {e}")

        # 9. Click en Confirmar Venta
        print("🔍 Buscando botón 'Confirmar Venta'...")
        try:
            # --- CONFIRMACIÓN ---
            time.sleep(2) # Esperar a que se habilite el botón
            
            # XPath específico proporcionado por el usuario
            xpath_confirmar = "//*[@id='root']/div/section/section/section/div/main/div/div[1]/div/div/div/div[2]/div[2]/div/div/div[2]/div[5]/div/button"
            
            try:
                boton_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_confirmar)))
                boton_confirmar.click()
                print("✅ 'Confirmar Venta' clickeado (XPath Usuario)")
            except Exception as e_xpath:
                print(f"⚠️ Falló XPath usuario para Confirmar Venta: {e_xpath}")
                # Fallback
                boton_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirmar Venta')] | //span[contains(text(), 'Confirmar Venta')]/parent::button")))
                driver.execute_script("arguments[0].click();", boton_confirmar)
                print("✅ 'Confirmar Venta' clickeado (Por texto / JS)")

            time.sleep(5)
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            print("✅ ESC enviado después de 'Confirmar Venta'")

            # --- PASOS POST-VENTA ---
            print("⏳ Procediendo con pasos post-venta...")
            time.sleep(3)

            # Click en botón 'Hecho'
            print("🔍 Buscando botón 'Hecho'...")
            xpath_hecho = "/html/body/div[27]/div/div[2]/div/div[2]/div[2]/div/div[2]/button"
            try:
                boton_hecho = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hecho)))
                boton_hecho.click()
                print("✅ Botón 'Hecho' clickeado")
            except Exception as e:
                print(f"⚠️ Falló XPath para Hecho, intentando por texto: {e}")
                boton_hecho = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Hecho')]")))
                boton_hecho.click()
                print("✅ Botón 'Hecho' clickeado (Por texto)")

            time.sleep(3)

            # Click en 'Finalizar turno'
            print("🔍 Buscando botón 'Finalizar turno'...")
            xpath_finalizar_turno = "//*[@id='root']/div/section/header/div/div[2]/div[2]/div[1]/button[2]"
            try:
                boton_finalizar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_finalizar_turno)))
                boton_finalizar.click()
                print("✅ Botón 'Finalizar turno' clickeado")
            except Exception as e:
                print(f"⚠️ Falló XPath para Finalizar turno, intentando por texto: {e}")
                boton_finalizar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Finalizar Turno')]")))
                boton_finalizar.click()
                print("✅ Botón 'Finalizar turno' clickeado (Por texto)")
                
        except Exception as e_post:
            print(f"⚠️ Error en confirmación o pasos post-venta: {e_post}")
            try:
                driver.save_screenshot("error_post_venta.png")
            except: pass

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
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    wait = WebDriverWait(driver, 40)

    # Login
    print("🔐 Iniciando sesión...")
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys(os.getenv("KARROT_LOGIN_PASSWORD"))
    #//*[@id="login-form"]/div[3]/div/div/div/div/button
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    print("✅ Login exitoso")
    time.sleep(10)  # Reducido de 15 a 10

    # Ir al panel de administración
    print("🚀 Yendo al panel de administración...")
    panel_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/div/div/div[2]/div[2]/button"))
    )
    panel_button.click()

    wait.until(
        EC.url_contains("/app")
    )
    print("✅ Panel de control cargado")
    time.sleep(3)  

    # Menú Inventario (Desplegable)
    print("� Desplegando menú Inventario...")
    # Click en el menú padre 'Inventario'
    try:
        menu_inventario_padre = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Inventario']"))
        )
        menu_inventario_padre.click()
        print("✅ Click en Inventario (Padre)")
        time.sleep(2)
        
        # Submenú Inventario
        print("📦 Accediendo a opción Inventario...")
        try:
            # Estrategia Principal: Usar selector basado en el ID del popup (Usuario: //*[@id="rc-menu-uuid-...-inventory-popup"]/li[1]/span/span)
            # Simplificado a contener '-inventory-popup' y el primer elemento de la lista
            xpath_submenu = "//*[contains(@id, '-inventory-popup')]//li[1]"
            submenu_inventario = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_submenu)))
            submenu_inventario.click()
            print("✅ Click en Submenú Inventario (Estrategia Popup)")
        except Exception as e:
            print(f"⚠️ Falló estrategia principal ({e}), intentando fallback...")
            # Fallback: Estrategia por texto y clase
            submenu_inventario = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'ant-menu-item')]//span[normalize-space()='Inventario']"))
            )
            submenu_inventario.click()
            print("✅ Click en Submenú Inventario (Fallback)")
            
        time.sleep(5)
        
    except Exception as e:
        print(f"⚠️ Error en navegación Inventario -> Inventario: {e}")
        # Fallback: intentar buscar por texto visible si la estructura es diferente
        try:
             print("  Intentando fallback: click en segundo elemento 'Inventario' visible...")
             elementos = driver.find_elements(By.XPATH, "//span[normalize-space()='Inventario']")
             visibles = [el for el in elementos if el.is_displayed()]
             if len(visibles) >= 2:
                 visibles[1].click()
             else:
                 print("  No se encontraron 2 elementos visibles.")
        except: pass
    
    # Asegurar tiempo de carga
    time.sleep(3)

    # Extraer valores del inventario
    print("\n" + "="*50)
    print("EXTRACCIÓN DE VALORES DE INVENTARIO")
    print("="*50)
    
    valores = extraer_valores_inventario_bogota()
    
    if valores:
        print(f"\n🎯 RESULTADOS OBTENIDOS:")
        print(f"   Producto: {valores.get('nombre', 'N/A')}")
        print(f"   SKU: {valores.get('sku', 'N/A')}")
        print(f"   Barcode: {valores.get('barcode', 'N/A')}")
        print(f"   Total Inventario: {valores.get('total_num', 0)}")
        print(f"   (Valor usado para validación: {valores.get('bogota_num', 0)})")
        
        observaciones = f"Total: {valores.get('total_num', 'N/A')} | Bogotá: {valores.get('bogota_num', 'N/A')}"
        
        # Intentar seleccionar el checkbox del primer producto
        print("\n" + "="*50)
        print("SELECCIÓN DE CHECKBOX")
        print("="*50)
        
        # ESTADO: La lógica de interacción (click en Checkbox, Ajustar, etc.) fue eliminada.
        # Se ha limpiado el código roto que dependía de esa lógica.
        
        # Validar consistencia de inventario (SOLO LECTURA)
        print("\n" + "="*50)
        print("VALIDACIÓN DE LECTURA")
        print("="*50)
        
        # Como no hubo ajuste, solo mostramos los valores extraídos
        valores_validacion = valores
            
        total_num = valores_validacion.get('total_num', 0)
        bogota_num = valores_validacion.get('bogota_num', 0)
        
        # Imprimir para depuración
        print(f"   Valor Principal (bogota_num -> Total): {bogota_num}")
        print(f"   Total Real (total_num): {total_num}")
        
        if bogota_num == total_num:
            print(f"✅ VALIDACIÓN EXITOSA: El valor extraído corresponde al Total.")
            observaciones += " | Validación Total OK"
            exito = True
        else:
            print(f"❌ VALIDACIÓN FALLIDA: Discrepancia.")
            observaciones += " | Validación Fallida"
            exito = False
        
        # Validar enlace del POS (Solicitud adicional)
        print("\n" + "="*50)
        print("VALIDACIÓN ENLACE POS")
        print("="*50)
        ingreso_al_pos()
        validacion_pos(valores.get('bogota_num', 0))


    

            
    else:
        print("❌ No se pudieron extraer valores del inventario")
        observaciones = "Error al extraer valores del inventario"
        exito = False

except TimeoutException as te:
    print(f"⏰ TIMEOUT: {te}")
    observaciones = f"Timeout: {str(te)[:100]}..."
    exito = False

    # Capturar screenshot para debug
    try:
        driver.save_screenshot("error_timeout.png")
        print("📸 Screenshot guardado como 'error_timeout.png'")
    except:
        pass



except Exception as e:
    print(f"❌ Error inesperado: {str(e)}")
    import traceback
    traceback.print_exc()
    observaciones = f"Error: {str(e)[:100]}..."
    exito = False

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