import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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
# PRUEBA NOMBRE Y APELLIDO VACÍOS
# =====================
id_caso = "TC005"

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

        # Actualiza en columnas M, N y O
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"✅ Caso {id_caso} actualizado -> {estado}")
    except Exception as e:
        print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")

# --- Pedir datos al usuario (dejando nombre y apellido vacíos) ---
company_name = input("👉 Ingresa el nombre de tu negocio o tienda: ")
first_name = ""  # Nombre vacío para probar el error
last_name = ""   # Apellido vacío para probar el error
email = input("👉 Ingresa tu correo electrónico: ")
phone_number = input("👉 Ingresa tu número de celular: ")
password = input("👉 Ingresa tu contraseña: ")

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

    # Nombre persona (VACÍO - esta es la prueba)
    if first_name:
        wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
        print("✅ Nombre ingresado")
    else:
        print("⚠️ Nombre dejado vacío (esto es intencional para la prueba)")

    # Apellido persona (VACÍO - esta es la prueba)
    if last_name:
        wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
        print("✅ Apellido ingresado")
    else:
        print("⚠️ Apellido dejado vacío (esto es intencional para la prueba)")

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

    # Correo electrónico
    wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
    print("✅ Correo electrónico ingresado")

    # Número de celular
    wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
    print("✅ Número de celular ingresado")

    # Contraseña
    wait.until(EC.presence_of_element_located((By.ID, "register-form_password"))).send_keys(password)
    print("✅ Contraseña ingresada")

    # Hacer clic en el botón "¡Inicia tu prueba gratuita!"
    print("🔄 Haciendo clic en el botón de registro...")
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
    submit_button.click()
    print("✅ Botón de registro presionado")

    # Esperar a que aparezcan los mensajes de error
    print("🔄 Esperando mensajes de error...")
    time.sleep(2)  # Esperar a que se procese la validación

    # Buscar los mensajes de error específicos
    errores_encontrados = 0
    
    # Mensaje de error para nombre
    try:
        mensaje_error_nombre = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error') and contains(., 'Introduce tu nombre')]")))
        mensaje_nombre = mensaje_error_nombre.text
        mensajes_error_encontrados.append(f"Nombre: {mensaje_nombre}")
        print(f"✅ Mensaje de error para nombre encontrado: '{mensaje_nombre}'")
        errores_encontrados += 1
    except Exception as error_nombre:
        print("❌ No se encontró el mensaje de error para nombre")
        observaciones += f"Fallo - No se detectó mensaje de error para nombre. "
    
    # Mensaje de error para apellido
    try:
        mensaje_error_apellido = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error') and contains(., 'Ingresa tu apellido')]")))
        mensaje_apellido = mensaje_error_apellido.text
        mensajes_error_encontrados.append(f"Apellido: {mensaje_apellido}")
        print(f"✅ Mensaje de error para apellido encontrado: '{mensaje_apellido}'")
        errores_encontrados += 1
    except Exception as error_apellido:
        print("❌ No se encontró el mensaje de error para apellido")
        observaciones += f"Fallo - No se detectó mensaje de error para apellido. "

    # Verificar si se encontraron ambos mensajes de error
    if errores_encontrados == 2:
        exito = True
        observaciones = f"Prueba exitosa - Ambos mensajes de error detectados: {', '.join(mensajes_error_encontrados)}"
        print("✅ Ambos mensajes de error encontrados correctamente")
    else:
        observaciones = f"Fallo en la prueba - Solo se encontraron {errores_encontrados} de 2 mensajes de error. {observaciones}"
        print(f"❌ Solo se encontraron {errores_encontrados} de 2 mensajes de error esperados")

    # Tomar captura de pantalla del resultado
    if exito:
        driver.save_screenshot("errores_nombre_apellido_detectados.png")
        print("📸 Captura de errores guardada como 'errores_nombre_apellido_detectados.png'")
    else:
        driver.save_screenshot("errores_incompletos.png")
        print("📸 Captura de errores incompletos guardada como 'errores_incompletos.png'")

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
    print("\n" + "="*60)
    print("RESUMEN DE EJECUCIÓN - PRUEBA NOMBRE Y APELLIDO VACÍOS")
    print("="*60)
    print(f"ID Caso: {id_caso}")
    print(f"Estado: {estado}")
    print(f"Observaciones: {observaciones}")
    if mensajes_error_encontrados:
        print("Mensajes de error encontrados:")
        for mensaje in mensajes_error_encontrados:
            print(f"  - {mensaje}")
    print("="*60)