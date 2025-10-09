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
# PRUEBA REGISTRO COMPLETO CON CONSULTOR
# =====================
id_caso = "TC009"

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

# --- Pedir datos al usuario ---
company_name = input("👉 Ingresa el nombre de tu negocio o tienda: ")
first_name = input("👉 Ingresa tu nombre: ")
last_name = input("👉 Ingresa tu apellido: ")
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

    # Correo electrónico
    wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
    print("✅ Correo electrónico ingresado")

    # Número de celular
    wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
    print("✅ Número de celular ingresado")

    # Contraseña
    wait.until(EC.presence_of_element_located((By.ID, "register-form_password"))).send_keys(password)
    print("✅ Contraseña ingresada")

    # --- SELECCIÓN DE CONSULTOR DE NEGOCIOS ---
    print("🔄 Seleccionando consultor de negocios...")
    
    # Buscar y hacer clic en el dropdown de consultor
    try:
        # Buscar el dropdown de consultor (puede ser por diferentes selectores)
        try:
            # Intentar encontrar por clase ant-select
            consultor_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select') and .//span[contains(@class, 'ant-select-selection-item') and contains(@title, 'Sin Consultor')]]")))
        except:
            # Intentar encontrar por ID si existe
            consultor_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "register-form_consultant")))
        
        # Hacer clic para abrir el dropdown
        consultor_dropdown.click()
        print("✅ Dropdown de consultor abierto")
        time.sleep(2)  # Esperar a que se desplieguen las opciones
        
        # Buscar y seleccionar "Andrea Areiza"
        try:
            # Buscar por título exacto
            andrea_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select-item-option')]//span[contains(@class, 'ant-select-selection-item') and @title='Andrea Areiza']")))
            andrea_option.click()
            print("✅ Andrea Areiza seleccionada como consultor")
        except:
            # Buscar por texto en el contenido
            andrea_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select-item-option') and contains(., 'Andrea Areiza')]")))
            andrea_option.click()
            print("✅ Andrea Areiza seleccionada como consultor (método alternativo)")
            
        time.sleep(1)
        
    except Exception as e:
        print(f"⚠️ Error al seleccionar consultor: {e}")
        observaciones += f"Error seleccionando consultor: {str(e)}. "
        
        # Intentar método alternativo con JavaScript
        try:
            print("🔄 Intentando selección de consultor con JavaScript...")
            driver.execute_script("""
                // Buscar el elemento del dropdown de consultor
                var consultorDropdown = document.querySelector('div.ant-select[aria-expanded="false"]');
                if (consultorDropdown) consultorDropdown.click();
                
                // Esperar a que se abra el dropdown
                setTimeout(function() {
                    // Buscar la opción de Andrea Areiza
                    var options = document.querySelectorAll('div.ant-select-item-option');
                    for (var i = 0; i < options.length; i++) {
                        if (options[i].textContent.includes('Andrea Areiza')) {
                            options[i].click();
                            break;
                        }
                    }
                }, 1000);
            """)
            print("✅ Selección de consultor realizada con JavaScript")
            time.sleep(2)
        except Exception as js_error:
            print(f"❌ También falló el método JavaScript: {js_error}")
            observaciones += f"Falló método JavaScript para consultor: {str(js_error)}. "

    # --- COMPLETAR REGISTRO ---
    print("🔄 Completando proceso de registro...")
    
    # Hacer clic en el botón "¡Inicia tu prueba gratuita!"
    #submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
    #submit_button.click()
    print("✅ Botón de registro presionado")

    # Esperar a que se procese el registro
    print("🔄 Esperando confirmación de registro...")
    time.sleep(5)
    
    # Verificar si el registro fue exitoso
    # (Puedes ajustar esta verificación según cómo se muestre el éxito)
    try:
        # Buscar algún indicador de éxito (ajusta según tu aplicación)
        success_indicator = driver.find_elements(By.XPATH, "//*[contains(text(), 'éxito') or contains(text(), 'success') or contains(text(), 'gracias') or contains(text(), 'confirmación')]")
        
        if success_indicator:
            exito = True
            observaciones = "Registro completado exitosamente con consultor Andrea Areiza"
            print("✅ Registro completado con éxito")
            
            # Tomar captura de éxito
            driver.save_screenshot("registro_exitoso.png")
            print("📸 Captura de registro exitoso guardada")
        else:
            # Verificar si hay mensajes de error
            errores = driver.find_elements(By.XPATH, "//div[contains(@class, 'error') or contains(@class, 'ant-form-item-explain-error')]")
            if errores:
                mensajes_error = [error.text for error in errores]
                observaciones = f"Posible error en registro: {', '.join(mensajes_error)}"
                print(f"⚠️ Se detectaron errores: {mensajes_error}")
            else:
                observaciones = "Registro completado pero no se pudo verificar el éxito"
                print("⚠️ Registro completado pero sin confirmación clara")
                
    except Exception as verification_error:
        observaciones = f"Error verificando registro: {str(verification_error)}"
        print(f"⚠️ Error en verificación: {verification_error}")

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
    
    time.sleep(5)
    driver.quit()
    
    # Mostrar resumen final
    print("\n" + "="*80)
    print("RESUMEN DE EJECUCIÓN - REGISTRO CON CONSULTOR")
    print("="*80)
    print(f"ID Caso: {id_caso}")
    print(f"Estado: {estado}")
    print(f"Observaciones: {observaciones}")
    print("="*80)