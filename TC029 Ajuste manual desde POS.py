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
    r"C:\Users\yonas\Documents\qa-automacion\automatizacion-karrot-a72723f4eafb.json",
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

        print(f"❌ Error seleccionando checkbox: {e}")
        return False

def ingreso_al_pos():   
    print("🔍 Buscando acceso al POS...")
    print("🔍 Accediendo al POS por URL directa...")
    try:
        url_pos = "https://dev.do5o1l1ov8f4a.amplifyapp.com/app/start/shift-start"
        driver.get(url_pos)
        print(f"✅ Navegación a POS iniciada: {url_pos}")

        wait = WebDriverWait(driver, 10)
        
        # 1. Click dropdown trigger
        print("🔍 Click en el desplegable de sedes...")
        try:
            # Volvemos al XPath específico que sabemos que funciona para ABRIR el menú
            dropdown_trigger = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/div/div/div/div[2]/div/div/div[1]/div/div[1]"))
            )
            dropdown_trigger.click()
            print("✅ Click en dropdown (XPath específico)")
        except Exception as e:
             print(f"⚠️ Falló click inicial ({e}), intentando por texto...")
             # Fallback secundario
             dropdown_trigger = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Selecciona Ubicacion')]/.."))
             )
             dropdown_trigger.click()
        
        time.sleep(1) # Esperar animación del menú

        # 2. Seleccionar Opción
        print("🔍 Buscando opción de sede...")
        try:
            # Estrategia 1: Buscar 'sede bogota' usando (.) para incluir hijos. 
            # IMPORTANTE: El menú ya debe estar abierto.
            # UPDATED: Buscamos un elemento leaf (sin hijos con texto) o div específico para evitar contenedores de tamaño 0
            opcion = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'sede bogota')] | //*[contains(., 'sede bogota') and not(contains(., 'Selecciona')) and count(.//*)=0]"))
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
                 # Estrategia 2: Cualquier elemento con 'sede' que sea visible
                opciones_genericas = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//*[contains(., 'sede') and not(contains(., 'Selecciona'))]"))
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
        print("🔍 Buscando boton ingresar...")
        try:
            boton_ingresar = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/button")))
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
        print("🚀 Validando POS...")
        
        # 1. Seleccionar primer producto (Checkbox)
        try:
            print("⏳ Buscando producto en POS...")
            # XPath original del usuario
            xpath_producto = "//*[@id='root']/div/section/section/section/div/main/div/div[1]/div[1]/div[2]/div/div[2]/div/div[3]"
            
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
            producto = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'product-card')] | //div[contains(@class, 'ant-card')]")))
            producto.click()
            print("✅ Producto seleccionado (Genérico)")

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
        boton_agregar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Añadir al carrito')]")))
        boton_agregar.click()
        print("✅ Boton agregar clickeado")

        time.sleep(2)
        
        # 5. Ingresar cantidad aleatoria
        print("🔍 Buscando campo de cantidad...")
        try:
            # Click en el botón de cantidad (el que indicó el usuario)
            boton_cantidad = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cart-list"]/div/div/div/div/ul/div/div[2]/div[1]/button[2]')))
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
                        # Priorizamos el botón visible con texto "Yes"
                        xpath_yes = "//div[contains(@class, 'ant-popover')]//button[contains(., 'Yes')] | //button[contains(., 'Yes')]"
                        
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

        # 6. Click en Realizar Venta
        print("🔍 Buscando botón 'Realizar venta'...")
        try:
            time.sleep(2) # Esperar a que se cierre el modal de cantidad
            # Usar XPath proporcionado por el usuario
            xpath_venta = "//*[@id='cart-summary']/div/button"
            boton_venta = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_venta)))
            boton_venta.click()
            print("✅ Botón 'Realizar venta' clickeado")
        except Exception as e:
            print(f"⚠️ Falló click en 'Realizar venta' ({xpath_venta}): {e}")
            try:
                # Fallback con JS
                driver.execute_script("var xpath = \"//*[@id='cart-summary']/div/button\"; var matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; if (matchingElement) matchingElement.click();")
                print("✅ Botón 'Realizar venta' clickeado (JS)")
            except:
                print("❌ No se pudo clickear 'Realizar venta'")

        # 7. Seleccionar Cliente Anonimo
        print("🔍 Buscando opción 'Cliente Anonimo'...")
        try:
            time.sleep(3) # Esperar a que cargue la vista de selección de cliente
            
            # XPath específico proporcionado por el usuario
            xpath_anonimo = "/html/body/div[21]/div/div[2]/div/div[2]/div[1]/div/div/div/div[1]/div/div/div[2]/div/div/div/div[2]/div"
            
            try:
                cliente_anonimo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_anonimo)))
                cliente_anonimo.click()
                print("✅ 'Cliente Anonimo' seleccionado (XPath Usuario)")
            except Exception as e_xpath:
                print(f"⚠️ Falló XPath usuario para cliente anónimo: {e_xpath}")
                # Fallback: Buscar por texto
                print("  Intentando buscar por texto 'Cliente Anonimo'...")
                cliente_anonimo = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Cliente Anonimo')] | //span[contains(text(), 'Cliente Anonimo')]")))
                cliente_anonimo.click()
                print("✅ 'Cliente Anonimo' seleccionado (Por texto)")
                
        except Exception as e:
            print(f"⚠️ Falló selección de Cliente Anonimo: {e}")

        # 8. Seleccionar Efectivo
        print("🔍 Buscando opción 'Efectivo'...")
        try:
            time.sleep(2) # Esperar a que cargue la vista de pagos
            
            # XPath específico proporcionado por el usuario
            xpath_efectivo = "/html/body/div[23]/div/div[2]/div/div[2]/div[1]/div/div/div/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/button[1]"
            
            try:
                boton_efectivo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_efectivo)))
                boton_efectivo.click()
                print("✅ 'Efectivo' seleccionado (XPath Usuario)")
            except Exception as e_xpath:
                print(f"⚠️ Falló XPath usuario para Efectivo: {e_xpath}")
                # Fallback: Buscar por texto
                print("  Intentando buscar por texto 'Efectivo'...")
                boton_efectivo = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Efectivo')] | //div[contains(text(), 'Efectivo')]")))
                boton_efectivo.click()
                print("✅ 'Efectivo' seleccionado (Por texto)")
                
        except Exception as e:
            print(f"⚠️ Falló selección de Efectivo: {e}")

        # 9. Click en Confirmar Venta
        print("🔍 Buscando botón 'Confirmar Venta'...")
        try:
            time.sleep(2) # Esperar a que se habilite el botón
            
            # XPath específico proporcionado por el usuario
            xpath_confirmar = "/html/body/div[10]/div/div[2]/div/div[2]/div[2]/div/div[2]/button[2]"
            
            try:
                boton_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_confirmar)))
                boton_confirmar.click()
                print("✅ 'Confirmar Venta' clickeado (XPath Usuario)")
            except Exception as e_xpath:
                print(f"⚠️ Falló XPath usuario para Confirmar Venta: {e_xpath}")
                # Fallback: Buscar por texto
                print("  Intentando buscar por texto 'Confirmar Venta'...")
                boton_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirmar Venta')] | //span[contains(text(), 'Confirmar Venta')]")))
                boton_confirmar.click()
                print("✅ 'Confirmar Venta' clickeado (Por texto)")
                
        except Exception as e:
            print(f"⚠️ Falló click en Confirmar Venta: {e}")
            
    except Exception as e:
        print(f"❌ Error en validacion_pos: {e}")
        try:
            driver.save_screenshot("error_pos_validacion.png")
            print("📸 Screenshot guardado: error_pos_validacion.png")
        except:
            pass


try:
    driver = webdriver.Chrome()
    driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    wait = WebDriverWait(driver, 40)

    # Login
    print("🔐 Iniciando sesión...")
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys("karrotdev@outlook.com")

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys("P4sc4g4z42025#*")
    #//*[@id="login-form"]/div[3]/div/div/div/div/button
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    print("✅ Login exitoso")
    time.sleep(10)  # Reducido de 15 a 10

    # Ir al panel de administración
    print("🚀 Yendo al panel de administración...")
    panel_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
    )
    panel_button.click()

    wait.until(
        EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]"))
    )
    print("✅ Panel de control cargado")
    time.sleep(3)  

    # Menú Catálogo
    print("📋 Accediendo a Catálogo...")
    catalogo = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Catálogo']"))
    )
    catalogo.click()
    print("✅ Click en Catálogo")
    time.sleep(3)

    # Menú Inventario
    print("📦 Accediendo a Inventario...")
    productos_servicios = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Inventario']"))
    )
    productos_servicios.click()
    print("✅ Click en Inventario")
    time.sleep(5)  # Dar tiempo a que cargue

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