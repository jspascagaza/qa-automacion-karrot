import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import random
import string

# =====================
# CONFIGURACIÓN GOOGLE SHEETS
# =====================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "automatizacion-karrot-1105a7349e3e.json", scope
)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"
)
sheet = spreadsheet.sheet1

# =====================
# PRUEBA CORREO ELECTRÓNICO - CICLO DE VALIDACIÓN
# =====================
id_caso = "TC006"

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

        # Actualiza en columnas M, N y O
        sheet.update_cell(fila, 11, automatizado)   # Columna K
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"✅ Caso {id_caso} actualizado -> {estado}")
    except Exception as e:
        print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")

def limpiar_campo_completamente(elemento):
    """Función para limpiar completamente un campo de entrada"""
    try:
        # Método 1: Clear normal
        elemento.clear()
        time.sleep(0.5)
        
        # Método 2: Seleccionar todo y borrar con BACKSPACE
        elemento.send_keys(Keys.CONTROL + 'a')
        elemento.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        
        # Método 3: JavaScript para asegurar
        driver.execute_script("arguments[0].value = '';", elemento)
        time.sleep(0.5)
        
        # Método 4: Disparar eventos de cambio
        driver.execute_script("""
            var element = arguments[0];
            element.value = '';
            var event = new Event('input', { bubbles: true });
            element.dispatchEvent(event);
            var changeEvent = new Event('change', { bubbles: true });
            element.dispatchEvent(changeEvent);
        """, elemento)
        
        print("✅ Campo limpiado completamente")
        
    except Exception as e:
        print(f"⚠️ Error al limpiar campo: {e}")

# --- Pedir datos al usuario ---
company_name =  "Empresa de Prueba S.A.S." 
first_names = ["Juan","Carlos","Luis","Ana","María","Laura","José","Miguel","Sofía","Valentina"]
last_names = ["Pérez","González","Rodríguez","López","Martínez","Sánchez","Gómez","Ramírez"]
first_name = (random.choice(first_names))
last_name = (random.choice(last_names))
user = (first_name[0] + last_name).lower().replace(" ", "")
email = f"{user}{random.randint(10,999)}@example.com"
phone_number = f"+57{random.randint(300000000,399999999)}"  # ajusta país/longitud según necesites
alphabet = string.ascii_letters + string.digits + "!@#$%&*"
password = ''.join(random.choice(alphabet) for _ in range(12))

# Inicializar navegador
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/register/es")

wait = WebDriverWait(driver, 20)

# Variable para controlar el éxito de la ejecución
exito = False
observaciones = ""
mensajes_error_encontrados = []

try:
    # Nombre de empresa
    wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
    print("✅ Nombre de empresa ingresado")

    # Nombre persona
    wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
    print("✅ Nombre ingresado")

    # Apellido persona
    wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
    print("✅ Apellido ingresado")

    # --- Seleccionar país: Colombia ---
    print("🔄 Intentando seleccionar país...")
    
    pais_seleccionado = False
    # Método 1: Intentar encontrar el dropdown de Ant Design
    try:
        # Buscar el elemento del selector de país
        country_selector = wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
        
        # Hacer clic para abrir el dropdown
        country_selector.click()
        print("✅ Click en el selector de país")
        time.sleep(2)  # Esperar a que se abra el dropdown
        
        # Buscar la opción de Colombia usando diferentes selectores
        try:
            # Intentar con selector por texto visible
            colombia_option = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
            colombia_option.click()
            print("✅ Colombia seleccionado desde dropdown (método 1)")
            pais_seleccionado = True
        except:
            # Intentar con selector por valor
            colombia_option = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
            colombia_option.click()
            print("✅ Colombia seleccionado desde dropdown (método 2)")
            pais_seleccionado = True
            
    except Exception as e:
        print(f"⚠️ Método dropdown falló: {e}")
        observaciones += f"Método dropdown falló: {str(e)}. "
        
        # Método 2: Intentar escribir directamente
        try:
            country_input = driver.find_element(By.ID, "register-form_mainCountry")
            country_input.clear()
            country_input.send_keys("Colombia")
            time.sleep(1)
            country_input.send_keys(Keys.ENTER)
            print("✅ Colombia ingresado manualmente")
            pais_seleccionado = True
        except Exception as e2:
            print(f"⚠️ Método escritura falló: {e2}")
            observaciones += f"Método escritura falló: {str(e2)}. "
            
            # Método 3: Usar JavaScript para establecer el valor
            try:
                driver.execute_script("""
                    var element = document.getElementById('register-form_mainCountry');
                    element.value = 'Colombia';
                    // Disparar eventos de cambio
                    var event = new Event('change', { bubbles: true });
                    element.dispatchEvent(event);
                """)
                print("✅ Valor establecido con JavaScript")
                pais_seleccionado = True
            except Exception as e3:
                print(f"⚠️ Método JavaScript falló: {e3}")
                observaciones += f"Método JavaScript falló: {str(e3)}. "
                print("❌ No se pudo seleccionar el país")
                raise Exception("No se pudo seleccionar el país después de todos los intentos")

    if not pais_seleccionado:
        raise Exception("No se pudo seleccionar el país")

    # Número de celular
    wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
    print("✅ Número de celular ingresado")

    # Contraseña
    wait.until(EC.presence_of_element_located((By.ID, "register-form_password"))).send_keys(password)
    print("✅ Contraseña ingresada")

    # --- CICLO DE VALIDACIÓN DEL CAMPO CORREO ELECTRÓNICO ---
    email_input = wait.until(EC.presence_of_element_located((By.ID, "register-form_email")))
    
    # Lista de pruebas a realizar en el ciclo
    pruebas_correo = [
        {
            "tipo": "CORREO_INCOMPLETO",
            "valor": "correoincompleto@",
            "mensaje_esperado": "¡Introduce un correo electrónico válido!",
            "encontrado": False
        },
        {
            "tipo": "CORREO_VACIO", 
            "valor": "",
            "mensaje_esperado": "Introduce tu dirección de correo electrónico",
            "encontrado": False
        }
    ]
    
    print("🔄 Iniciando ciclo de validación del campo correo...")
    
    for i, prueba in enumerate(pruebas_correo, 1):
        print(f"\n--- Prueba {i}: {prueba['tipo']} ---")
        
        # LIMPIAR COMPLETAMENTE el campo antes de cada prueba
        limpiar_campo_completamente(email_input)
        time.sleep(1)
        
        # Hacer clic en el campo para asegurar el foco
        email_input.click()
        time.sleep(0.5)
        
        # Ingresar valor según el tipo de prueba
        if prueba['valor']:
            email_input.send_keys(prueba['valor'])
            print(f"✅ Valor ingresado: '{prueba['valor']}'")
            time.sleep(1)
        
        # Activar validación cambiando el foco a otro campo
        driver.find_element(By.ID, "register-form_phoneNumber").click()
        print("✅ Foco cambiado para activar validación")
        
        # Esperar a que se procese la validación
        time.sleep(3)
        
        # Buscar el mensaje de error esperado
        try:
            mensaje_error = wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(@class, 'ant-form-item-explain-error') and contains(., '{prueba['mensaje_esperado']}')]")
            ))
            
            mensaje_texto = mensaje_error.text
            mensajes_error_encontrados.append(f"{prueba['tipo']}: {mensaje_texto}")
            prueba['encontrado'] = True
            print(f"✅ Mensaje de error encontrado: '{mensaje_texto}'")
            
            # Tomar captura de pantalla del mensaje
            driver.save_screenshot(f"error_{prueba['tipo'].lower()}_{i}.png")
            print(f"📸 Captura guardada como 'error_{prueba['tipo'].lower()}_{i}.png'")
            
        except Exception as e:
            print(f"❌ No se encontró el mensaje de error esperado: '{prueba['mensaje_esperado']}'")
            print(f"Error: {e}")
            observaciones += f"Fallo - No se detectó mensaje para {prueba['tipo']}. "
            
            # Tomar captura de pantalla para debug
            driver.save_screenshot(f"no_error_{prueba['tipo'].lower()}_{i}.png")
            print(f"📸 Captura de debug guardada como 'no_error_{prueba['tipo'].lower()}_{i}.png'")
        
        # Pequeña pausa entre pruebas
        time.sleep(1)
    
    # Verificar si se encontraron TODOS los mensajes de error esperados
    mensajes_encontrados = sum(1 for prueba in pruebas_correo if prueba['encontrado'])
    
    if mensajes_encontrados == len(pruebas_correo):
        exito = True
        observaciones = f"Prueba exitosa - Todos los mensajes de error detectados correctamente"
        print("✅ Todos los mensajes de error encontrados correctamente")
    else:
        observaciones = f"Fallo en la prueba - Solo {mensajes_encontrados} de {len(pruebas_correo)} mensajes encontrados. {observaciones}"
        print(f"❌ Solo se encontraron {mensajes_encontrados} de {len(pruebas_correo)} mensajes esperados")
    
    # Verificación final con el botón de registro
    print("\n🔄 Verificando validación final...")
    
    # Asegurarse de que el campo esté vacío para la prueba final
    limpiar_campo_completamente(email_input)
    time.sleep(1)
    
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
    submit_button.click()
    print("✅ Botón de registro presionado")
    time.sleep(3)
    
    # Tomar captura final
    if exito:
        driver.save_screenshot("validacion_completa_exitosa.png")
        print("📸 Captura final de validación exitosa guardada")
    else:
        driver.save_screenshot("validacion_completa_fallida.png")
        print("📸 Captura final de validación fallida guardada")

except Exception as e:
    print(f"❌ Error en el proceso: {e}")
    observaciones += f"Error final: {str(e)}"
    
    # Tomar captura de pantalla del error
    driver.save_screenshot("error_proceso.png")
    print("📸 Captura de error guardada como 'error_proceso.png'")

finally:
    # Registrar resultado en Google Sheets
    estado = "EXITOSO" if exito else "FALLIDO"
    registrar_resultado(id_caso, estado, observaciones)
    
    time.sleep(3)
    driver.quit()
    
    # Mostrar resumen final
    print("\n" + "="*80)
    print("RESUMEN DE EJECUCIÓN - CICLO DE VALIDACIÓN DE CORREO")
    print("="*80)
    print(f"ID Caso: {id_caso}")
    print(f"Estado: {estado}")
    print(f"Observaciones: {observaciones}")
    
    print("\nDetalle de pruebas realizadas:")
    for i, prueba in enumerate(pruebas_correo, 1):
        status = "✅" if prueba['encontrado'] else "❌"
        print(f"  {i}. {prueba['tipo']}: {status} - {prueba['mensaje_esperado']}")
    
    if mensajes_error_encontrados:
        print("\nMensajes de error encontrados:")
        for mensaje in mensajes_error_encontrados:
            print(f"  • {mensaje}")
    print("="*80)