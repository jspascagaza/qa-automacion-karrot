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
from selenium.webdriver.support.relative_locator import locate_with

# =====================
# CONFIGURACIÓN GOOGLE SHEETS
# =====================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"C:\Users\karrot\Documents\qa-automacion\automatizacion-karrot-a72723f4eafb.json", 
    scope
)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"
)
sheet = spreadsheet.sheet1

# Variables de control
observaciones = ""
url_final = ""
estado = "PENDIENTE"

# =====================
# FUNCIÓN PARA REGISTRAR RESULTADOS
# =====================
def registrar_resultado(id_caso, estado, observaciones=""):
    try:
        celda = sheet.find(id_caso)
        if not celda:
            print(f"⚠️ No se encontró el ID {id_caso}")
            return False
        fila = celda.row
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        automatizado = "Sí"
        sheet.update_cell(fila, 11, automatizado)   # Columna K
        sheet.update_cell(fila, 13, fecha)          # Columna M
        sheet.update_cell(fila, 14, estado)         # Columna N
        sheet.update_cell(fila, 15, observaciones)  # Columna O
        print(f"✅ Caso {id_caso} actualizado -> {estado}")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")
        return False

# =====================
# CONFIGURACIÓN DEL DRIVER
# =====================
try:
    driver = webdriver.Chrome()
    driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
    driver.maximize_window()
    print("✅ Navegador iniciado correctamente")
except Exception as e:
    print(f"❌ Error al iniciar el navegador: {str(e)}")
    exit()

wait = WebDriverWait(driver, 40)
id_caso = "TC022"
#nombre_caja = input("Ingrese el nombre de la caja a crear: ")

try:
    # =====================
    # LOGIN
    # =====================
    print("🔐 Iniciando proceso de login...")
    
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys("js.pascagaza@karrotup.com")

    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys("P4sc4g4z42025#*")

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
    login_button.click()
    time.sleep(10)

    panel_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
    )
    panel_button.click()

    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]")))
    time.sleep(5)

    # =====================
    # NAVEGACIÓN A MODULO DE UBICACIONES
    # =====================
    ModuloUbicaciones = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/aside/div/ul/li[1]/ul/li[12]/div"))
    )
    ModuloUbicaciones.click()
    time.sleep(5)

    # Buscar las opciones del submenú dentro del menú de ubicaciones
    opciones_submenu = driver.find_elements(By.XPATH, "//ul[contains(@class, 'ant-menu-sub')]//li")
    opcion_encontrada = None
    for opcion in opciones_submenu:
        if "Actvidades" in opcion.text:
            opcion_encontrada = opcion
            break

    if opcion_encontrada:
        opcion_encontrada.click()
        print("✅ Click en 'Actividades'")
    else:
        print("❌ No se encontró la opción 'Actividades'")

    time.sleep(5)

    # Esperar a que la tabla esté visible (puedes esperar por el tbody o por el botón)
    boton_editar = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[4]/div/button[1]'))
    )
    # Hacer scroll al botón por si está fuera de vista
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_editar)
    time.sleep(1)
    boton_editar.click()
    print("✅ Click en el botón de editar de la primera fila")

    time.sleep(5)

    # Esperar el input del número de campos
    input_num_campos = wait.until(
        EC.presence_of_element_located((By.ID, "number_of_fields"))
    )
    # Quitar readonly y hacer visible el input con JS
    driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].style.opacity = 1;", input_num_campos)
    input_num_campos.clear()
    input_num_campos.send_keys("3")  # Cambia "3" por el número que desees
    input_num_campos.send_keys(Keys.ENTER)
    print("✅ Número de campos ingresado manualmente")

    time.sleep(10)

    # Espera a que los campos dinámicos estén presentes (espera el primero)
    total_campos = 3  # Cambia este valor según lo que seleccionaste antes
    for i in range(total_campos):
        # Esperar el input de nombre
        input_nombre = wait.until(
            EC.visibility_of_element_located((By.ID, f"name_{i}"))
        )
        input_nombre.clear()
        input_nombre.send_keys(f"Campo {i+1}")
        print(f"✅ Ingresado nombre para campo {i+1}")

        # Esperar el contenedor del selector del tipo
        selector_tipo = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//input[@id='type_{i}']/ancestor::div[contains(@class, 'ant-select')]//div[contains(@class, 'ant-select-selector')]"))
        )
        selector_tipo.click()
        time.sleep(0.5)

        # Esperar y seleccionar la opción deseada (ejemplo: "Hora")
        opciones_tipo = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-item-option')]"))
        )
        opcion_encontrada = None
        for opcion in opciones_tipo:
            if "Respuesta corta" in opcion.text:  # Cambia "Hora" por el tipo que desees
                opcion_encontrada = opcion
                break
        if opcion_encontrada:
            opcion_encontrada.click()
            print(f"✅ Seleccionado tipo para campo {i+1}")
        else:
            print(f"❌ No se encontró la opción de tipo para campo {i+1}")

        time.sleep(0.5)
    
    # Esperar a que el botón "Guardar" sea visible y clickeable usando el XPath absoluto
    boton_guardar = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/section/section/div/main/div[1]/div/div/div/button[2]'))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_guardar)
    time.sleep(1)
    try:
        boton_guardar.click()
        print("✅ Click normal en botón actualizar")
        observaciones += "✅ Actividad actualizada exitosamente.\n"
        estado = "EXITOSO"
        registrar_resultado(id_caso, estado, observaciones)
    except Exception as e:
        print(f"⚠️ Click normal falló: {e}, intentando con JavaScript...")
        driver.execute_script("arguments[0].click();", boton_guardar)
        print("✅ Click forzado con JavaScript en botón Guardar")
        observaciones += "✅ Actividad actualizada fallidamente (click JS).\n"
        estado = "FALLIDO"
        registrar_resultado(id_caso, estado, observaciones)
    time.sleep(5)
    
    
except Exception as e:    
    observaciones += f"❌ Error durante la ejecución: {str(e)}\n"
    estado = "FALLIDO"
    print(observaciones)
    registrar_resultado(id_caso, estado, observaciones)
