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


def ingreso_al_pos():   
    try:
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

        # --- NAVEGACIÓN A INVENTARIO ---
        print("📦 Accediendo a opción Inventario via Popup...")
        try:
            xpath_submenu = '//*[@id="rc-menu-uuid-17907-7-inventory-popup"]/li[1]/span'
            submenu_inventario = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_submenu)))
            submenu_inventario.click()
            print("✅ Click en Submenú Inventario (Estrategia Popup)")
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
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
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
    
    # Asegurar tiempo de carga
    time.sleep(3)
        
    # Validar enlace del POS (Solicitud adicional)
    ingreso_al_pos()
    # validacion_pos(valores.get('bogota_num', 0))




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