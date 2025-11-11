import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
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
# PRUEBA REGISTRO COMPLETO CON CONSULTOR Y VERIFICACIÓN
# =====================
id_caso = "TC011"

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

wait = WebDriverWait(driver, 30)

# Variable para controlar el éxito de la ejecución
exito = False
observaciones = ""
url_final = ""

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
        time.sleep(2)
        
        # Buscar la opción de Colombia
        try:
            colombia_option = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
            colombia_option.click()
            print("✅ Colombia seleccionado desde dropdown (método 1)")
            pais_seleccionado = True
        except:
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
            
            # Método 3: Usar JavaScript
            try:
                driver.execute_script("""
                    var element = document.getElementById('register-form_mainCountry');
                    element.value = 'Colombia';
                    var event = new Event('change', { bubbles: true });
                    element.dispatchEvent(event);
                """)
                print("✅ Valor establecido con JavaScript")
                pais_seleccionado = True
            except Exception as e3:
                print(f"⚠️ Método JavaScript falló: {e3}")
                observaciones += f"Método JavaScript falló: {str(e3)}. "
                raise Exception("No se pudo seleccionar el país")

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

    # --- COMPLETAR REGISTRO ---
    print("🔄 Completando proceso de registro...")
    
    # Hacer clic en el botón "¡Inicia tu prueba gratuita!"
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
    submit_button.click()
    print("✅ Botón de registro presionado")
    time.sleep(6)

    # Esperar a que aparezcan los 4 inputs del OTP
    otp_inputs = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.ant-input.ant-input-lg[maxlength='1']"))
    )

    # =====================
    # VALIDACIÓN DE OTP CON REINTENTOS
    # =====================
    max_intentos = 3
    intento = 1
    otp_exitoso = False

    while intento <= max_intentos and not otp_exitoso:
        print(f"\n--- Intento {intento} de {max_intentos} ---")
        
        # Obtener el código OTP
        otp_code = input("👉 Ingresa el código OTP recibido (4 dígitos): ")
        
        # Limpiar los campos OTP antes de cada intento (incluyendo el primero)
        print("🔄 Limpiando campos OTP...")
        for input_field in otp_inputs:
            # Métodos robustos para limpiar el campo
            input_field.clear()
            time.sleep(0.2)
            # Enviar BACKSPACE para asegurar que esté vacío
            input_field.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
        
        time.sleep(1)
        
        # Ingresar cada dígito
        for i, digit in enumerate(otp_code):
            otp_inputs[i].send_keys(digit)
            time.sleep(0.5)

        print("✅ OTP ingresado")

        # Hacer clic en el botón Continuar
        boton = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continuar')]")))
        boton.click()
        print("✅ Botón Continuar presionado")

        # Esperar y validar si hay error
        time.sleep(3)
        
        # Verificar si aparece el mensaje de error
        try:
            mensaje_error = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'text-danger') and contains(., 'no es válido')]"))
            )
            
            if mensaje_error.is_displayed():
                print("❌ ERROR: El código introducido no es válido")
                intento += 1
                if intento <= max_intentos:
                    print("🔄 Por favor, ingresa un nuevo código OTP")
                    # Volver a obtener los inputs OTP por si la página se recargó
                    try:
                        otp_inputs = wait.until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.ant-input.ant-input-lg[maxlength='1']"))
                        )
                    except:
                        print("⚠️ No se pudieron re-obtener los inputs OTP")
                continue
                
        except:
            # No se encontró error, OTP es correcto
            print("✅ OTP válido - Continuando normalmente")
            otp_exitoso = True
            break

    # Verificar si se agotaron los intentos
    if not otp_exitoso:
        raise Exception("Máximo de intentos de OTP alcanzado. No se pudo validar el código.")

    # --- VERIFICAR ÉXITO DEL REGISTRO ---
    print("🔄 Verificando éxito del registro...")
    
    # Esperar a que se complete el proceso de registro
    time.sleep(8)
    
    # Verificar que estamos en el dashboard
    try:
        # Buscar el texto esperado en el dashboard
        elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Selecciona una ubicación y una caja para comenzar tu turno')]"))
        )
        print("✅ Registro exitoso - Texto encontrado en dashboard")
        exito = True
        url_final = driver.current_url
        observaciones += "Registro y redirección exitosos. "
        
    except Exception as e:
        print(f"⚠️ No se encontró el texto esperado: {e}")
        observaciones += "No se encontró el texto esperado en dashboard. "
        # Verificar si al menos estamos en una URL diferente
        if "auth" not in driver.current_url:
            print("✅ Parece que el registro fue exitoso (URL cambiada)")
            exito = True
            url_final = driver.current_url
        else:
            raise Exception("Registro falló - No se redirigió al dashboard")

except Exception as e:
    print(f"❌ Error en el proceso: {e}")
    observaciones += f"Error final: {str(e)}"
    driver.save_screenshot("error_proceso.png")
    print("📸 Captura de error guardada")

finally:
    # Registrar resultado en Google Sheets
    estado = "EXITOSO" if exito else "FALLIDO"
    registrar_resultado(id_caso, estado, observaciones)
    
    # Mostrar información final
    print(f"\nURL final: {driver.current_url}")
    print(f"Título de la página: {driver.title}")
    
    time.sleep(3)
    driver.quit()
    
    # Mostrar resumen final
    print("\n" + "="*80)
    print("RESUMEN DE EJECUCIÓN - REGISTRO CON REDIRECCIÓN")
    print("="*80)
    print(f"ID Caso: {id_caso}")
    print(f"Estado: {estado}")
    print(f"URL Final: {url_final}")
    print(f"Observaciones: {observaciones}")
    print("="*80)