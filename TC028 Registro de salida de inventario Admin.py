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
id_caso = "TC028"

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
    
                    return {
                        'total_num': total_num,
                        'bogota_num': suma_sedes, # Usamos la suma como el valor comparativo principal
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
    time.sleep(3)  # Reducido de 5 a 3

    # Menú Inventario (Desplegable)
    print("📦 Desplegando menú Inventario...")
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
        print(f"   Total: '{valores.get('total', 'N/A')}'")
        print(f"   Sede Bogotá: '{valores.get('bogota', 'N/A')}'")
        print(f"   Total (num): {valores.get('total_num', 0)}")
        print(f"   Bogotá (num): {valores.get('bogota_num', 0)}")
        
        observaciones = f"Total: {valores.get('total', 'N/A')} | Bogotá: {valores.get('bogota', 'N/A')}"
        
        # Intentar seleccionar el checkbox del primer producto
        print("\n" + "="*50)
        print("SELECCIÓN DE CHECKBOX")
        print("="*50)
        
        checkbox_seleccionado = seleccionar_checkbox_primer_producto()
        
        if checkbox_seleccionado:
            observaciones += " | Checkbox seleccionado"
            print("✅ Checkbox seleccionado exitosamente")
            
            # --- NUEVO CÓDIGO INICIO ---
            try:
                print("⏳ Buscando botón 'Ajustar el inventario'...")
                btn_ajustar = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(normalize-space(.), 'Ajustar el inventario')] | //span[contains(normalize-space(.), 'Ajustar el inventario')]")
                ))
                btn_ajustar.click()
                print("✅ Click en 'Ajustar el inventario'")
                
                # Esperar a que la pantalla aparezca
                print("⏳ Esperando que aparezca la pantalla de ajuste...")
                # Asumiendo que aparece un modal o un nuevo header
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'ant-modal-content')] | //h2[contains(text(), 'Ajuste')]")
                ))
                print("✅ Pantalla de ajuste aparecida")
                observaciones += " | Botón Ajustar clickeado"

                # --- SELECCIÓN DE SEDE ---
                try:
                    print("⏳ Buscando selector de Sede...")
                    
                    # Estrategias para encontrar el dropdown de ubicación
                    estrat_dropdown = [
                        # 1. Por el label "Ubicación" (Más robusto)
                        "//label[contains(., 'Ubicación')]/../..//div[contains(@class, 'ant-select-selector')]",
                        # 2. Por clase de ant-modal y select
                        "//div[contains(@class, 'ant-modal-content')]//div[contains(@class, 'ant-select-selector')]",
                        # 3. XPath directo si los anteriores fallan (input)
                        "//input[contains(@id, 'rc_select')]",
                    ]
                    
                    dropdown = None
                    for xpath in estrat_dropdown:
                        try:
                            print(f"  Probando selector: {xpath}")
                            dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            if dropdown:
                                print(f"✅ Dropdown encontrado con: {xpath}")
                                break
                        except:
                            continue
                            
                    if not dropdown:
                        raise Exception("No se pudo encontrar el dropdown de ubicación con ninguna estrategia")
                    
                    # Click en el dropdown
                    dropdown.click()
                    print("✅ Dropdown de Ubicación clickeado")
                    
                    time.sleep(1) # Esperar animación de despliegue
                    
                    # Seleccionar la primera opción disponible
                    # Usamos un selector general para opciones de Ant Design
                    print("⏳ Buscando opciones...")
                    opcion = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[contains(@class, 'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]//div[contains(@class, 'ant-select-item-option') and not(contains(@class, 'ant-select-item-option-disabled'))]")
                    ))
                    
                    nombre_sede = opcion.text
                    print(f"✅ Opción encontrada: {nombre_sede}")
                    opcion.click()
                    print(f"✅ Sede seleccionada: {nombre_sede}")
                    observaciones += f" | Sede: {nombre_sede}"
                    
                    time.sleep(1) # Esperar actualización UI
                    
                except Exception as e:
                    print(f"⚠️ Error/Advertencia en selección de sede: {e}")
                    observaciones += " | Fallo Selección Sede"
                    # Captura de pantalla para debug
                    try:
                        driver.save_screenshot("error_sede_tc028.png")
                        print("📸 Screenshot error_sede_tc028.png guardado")
                    except: pass
                # --- FIN SELECCIÓN DE SEDE ---

                # --- SELECCIONAR TIPO DE MOVIMIENTO (SALIDA) ---
                try:
                    print("⏳ Seleccionando 'Movimientos de salida'...")
                    
                    # Estrategia 1: Click en selector y luego en opción
                    seleccionado = False
                    try:
                        # Intentar encontrar el dropdown por el label "Tipo de Movimiento"
                        dropdown_xpath = "//div[contains(@class, 'ant-row') and .//label[contains(text(), 'Tipo de Movimiento')]]//div[contains(@class, 'ant-select-selector')]"
                        # Si falla, intentar por el valor actual "Movimientos de entrada"
                        if not driver.find_elements(By.XPATH, dropdown_xpath):
                            dropdown_xpath = "//div[contains(@class, 'ant-select-selector') and .//span[contains(text(), 'Movimientos de entrada')]]"
                        
                        dropdown_movimiento = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
                        dropdown_movimiento.click()
                        time.sleep(1)
                        
                        # Intentar clickear la opción
                        opcion_xpath = "//div[contains(@class, 'ant-select-item-option') and .//div[contains(text(), 'Movimientos de salida')]]"
                        # Esperar a que sea visible
                        opcion_salida = wait.until(EC.visibility_of_element_located((By.XPATH, opcion_xpath)))
                        opcion_salida.click()
                        print("✅ Opción clickeada: Movimientos de salida")
                        seleccionado = True
                        
                    except Exception as e_click:
                        print(f"⚠️ Falló selección por click: {e_click}")
                        
                        # Estrategia 2: Teclado (Flecha Abajo + Enter)
                        try:
                            print("🔄 Intentando por teclado...")
                            # Asegurar foco en el dropdown de nuevo
                            dropdown_movimiento = driver.find_element(By.XPATH, dropdown_xpath)
                            dropdown_movimiento.click()
                            time.sleep(0.5)
                            
                            actions = ActionChains(driver)
                            actions.send_keys(Keys.DOWN).perform()
                            time.sleep(0.5)
                            actions.send_keys(Keys.ENTER).perform()
                            print("✅ Teclas enviadas (DOWN + ENTER)")
                            seleccionado = True
                        except Exception as e_key:
                             print(f"❌ Falló selección por teclado: {e_key}")  

                    # Verificar cambio
                    time.sleep(1)
                    if "Movimientos de salida" in dropdown_movimiento.text:
                         print("✅ Confirmado: El valor cambió a 'Movimientos de salida'")
                         observaciones += " | Tipo Salida OK"
                    else:
                         print(f"⚠️ El valor parece no haber cambiado. Actual: '{dropdown_movimiento.text}'")
                         observaciones += " | Tipo Salida DUDA"
                         
                except Exception as e:
                    print(f"❌ Error crítico seleccionando Tipo de Movimiento: {e}")
                    observaciones += " | Error Selección Tipo"
                # --- FIN SELECCION ---
                
                # --- NUEVO CÓDIGO INPUT ---
                try:
                    print("⏳ Buscando campo numérico...")
                    # Selector basado en el HTML proporcionado por el usuario
                    input_cantidad = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//input[contains(@class, 'ant-input-number-input') and @role='spinbutton']")
                    ))
                    
                    # Obtener el stock disponible (usando bogota_num que es la suma de sedes calculada)
                    stock_disponible = int(valores.get('bogota_num', 100))
                    print(f"   Stock disponible para salida: {stock_disponible}")
                    
                    # Asegurar que el límite sea al menos 1 para evitar errores en randint
                    limite_random = stock_disponible if stock_disponible > 0 else 1
                    
                    # Generar valor aleatorio entre 1 y el stock disponible
                    valor_a_ingresar = str(random.randint(1, limite_random))
                    
                    input_cantidad.click() # Asegurar foco
                    # Limpiar por si acaso
                    input_cantidad.send_keys(Keys.BACK_SPACE * 5) 
                    input_cantidad.send_keys(valor_a_ingresar)
                    
                    print(f"✅ Valor aleatorio ingresado: {valor_a_ingresar} (Limitado por stock: {stock_disponible})")
                    observaciones += f" | Valor {valor_a_ingresar} ingresado (Stock: {stock_disponible})"
                except Exception as e:
                    print(f"❌ Error al ingresar valor: {e}")
                    observaciones += " | Fallo al ingresar valor"
                # --- FIN NUEVO CÓDIGO INPUT ---
                
                # --- NUEVO CÓDIGO CONFIRMAR ---
                try:
                    print("⏳ Buscando botón Confirmar...")
                    # Buscamos por texto exacto 'Confirmar' en un span o button
                    btn_confirmar = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//span[normalize-space()='Confirmar'] | //button[contains(., 'Confirmar')]")
                    ))
                    btn_confirmar.click()
                    print("✅ Click en Confirmar")
                    observaciones += " | Confirmar clickeado"
                    
                    time.sleep(2) # Esperar a que se procese
                    
                except Exception as e:
                    print(f"❌ Error al clickear Confirmar: {e}")
                    observaciones += " | Fallo Confirmar"
                # --- FIN NUEVO CÓDIGO CONFIRMAR ---
                
                # --- VALIDACIÓN FINAL ---
                try:
                    print("⏳ Esperando actualización de inventario...")
                    time.sleep(5) # Dar tiempo para que se procese y actualice la tabla
                    
                    print("\n📊 EXTRAYENDO VALORES FINALES:")
                    valores_finales = extraer_valores_inventario_bogota()
                    
                    if valores_finales and 'valor_a_ingresar' in locals():
                        bogota_final = valores_finales.get('bogota_num', 0)
                        valor_salida_num = float(valor_a_ingresar)
                        
                        # Recalcular valor inicial desde el diccionario original por seguridad
                        bogota_inicial = valores.get('bogota_num', 0)
                        
                        print(f"\n🧮 VALIDACIÓN MATEMÁTICA:")
                        print(f"   Inicial: {bogota_inicial}")
                        print(f"   Salida: {valor_salida_num}")
                        print(f"   Esperado (Resta): {bogota_inicial - valor_salida_num}")
                        print(f"   Obtenido: {bogota_final}")
                        
                        # Usamos una pequeña tolerancia (VALIDACIÓN DE RESTA PARA SALIDA)
                        if abs((bogota_inicial - valor_salida_num) - bogota_final) < 0.01:
                            print("✅ VALIDACIÓN EXITOSA: El inventario se actualizó correctamente.")
                            observaciones += " | Validación Matemática OK"
                            # Sobreescribimos el éxito general basado en esta prueba crucial
                            exito = True
                        else:
                            print("❌ VALIDACIÓN FALLIDA: Los valores no coinciden.")
                            observaciones += f" | Fallo Matemático (Esp: {bogota_inicial - valor_salida_num}, Obt: {bogota_final})"
                            exito = False
                    else:
                         print("❌ No se pudo extraer el inventario final o falta el valor ingresado.")
                         observaciones += " | Fallo extracción final"
                except Exception as e:
                    print(f"❌ Error en validación final: {e}")
                    observaciones += " | Error Validacion"
                # --- FIN VALIDACIÓN FINAL ---
                
            except Exception as e:
                print(f"❌ Error al intentar ajustar inventario: {e}")
                observaciones += " | Fallo al clickear Ajustar"
            # --- NUEVO CÓDIGO FIN ---
        else:
            observaciones += " | Checkbox no seleccionado"
            print("⚠️  No se pudo seleccionar el checkbox")
        
        # Validar consistencia de inventario (FINAL)
        print("\n" + "="*50)
        print("VALIDACIÓN FINAL DE INVENTARIO")
        print("="*50)
        
        # Usar valores finales si existen, sino usar los iniciales
        if 'valores_finales' in locals() and valores_finales:
            print("ℹ️ Usando valores POST-AJUSTE para la validación final")
            valores_validacion = valores_finales
        else:
            print("⚠️ Usando valores INICIALES para la validación final (no hubo actualización)")
            valores_validacion = valores
            
        total_num = valores_validacion.get('total_num', 0)
        bogota_num = valores_validacion.get('bogota_num', 0)
        
        # Imprimir para depuración
        print(f"   Bogotá (Validación): {bogota_num}")
        print(f"   Total (Validación): {total_num}")
        
        if bogota_num == total_num:
            print(f"✅ VALIDACIÓN EXITOSA: Bogotá ({bogota_num}) == Total ({total_num})")
            observaciones += " | Validación Estructural OK"
            # Mantenemos el estado de éxito previo
        else:
            print(f"❌ VALIDACIÓN FALLIDA: Bogotá ({bogota_num}) != Total ({total_num}) -> Bug detectado")
            observaciones += " | Validación Estructural Fallida (Bug Front)"
            exito = False
            
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