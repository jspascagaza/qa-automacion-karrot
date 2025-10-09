import csv
import datetime
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
# DATOS DE ENTRADA
# =====================
nombre = input("Ingrese el nombre de la sede: ")
direccion = input("Ingrese la dirección de la sede: ")
usuario = input("Ingrese el correo del usuario: ")

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

# Variable para controlar el éxito de la ejecución
exito = False
observaciones = ""
url_final = ""

# =====================
# FUNCIÓN PARA REGISTRAR RESULTADOS
# =====================
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
            return False
        fila = celda.row
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Actualiza en columnas M, N y O
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
id_caso = "TC014"

try:
    # =====================
    # LOGIN
    # =====================
    print("🔐 Iniciando proceso de login...")
    
    # Esperar campo de correo
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys("js.pascagaza@karrotup.com")
    print("✅ Correo electrónico ingresado")

    # Esperar campo de contraseña
    password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
    password_input.click()
    password_input.send_keys("P4sc4g4z42025#*")
    print("✅ Contraseña ingresada")

    # Click en el botón "Iniciar sesión"
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Iniciar sesión')]")))
    login_button.click()
    print("✅ Botón de login clickeado")
    time.sleep(10)

    # =====================
    # IR AL PANEL DE ADMINISTRACIÓN
    # =====================
    panel_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
    )
    panel_button.click()
    print("✅ Click en 'Ir al panel de administración'")

    # Esperar a que cargue el Panel de control
    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]")))
    print("✅ Panel de control cargado correctamente")
    time.sleep(5)

    # =====================
    # NAVEGACIÓN A UBICACIONES
    # =====================
    print("📍 Navegando al módulo de Ubicaciones...")
    
    ModuloUbicaciones = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/aside/div/ul/li[1]/ul/li[12]/div"))
    )
    ModuloUbicaciones.click()
    print("✅ Click en Ubicaciones")
    time.sleep(5)

    # Obtener y seguir el enlace de ubicaciones
    #segunda parte ubicaciones
    segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
    print(segundopath.text)
    print(segundopath.get_attribute("href"))
    driver.get(segundopath.get_attribute("href"))
    print("✅ dirigiendo a Ubicaciones")
    time.sleep(10)

    # Navegar directamente a la URL de agregar ubicación
    url_agregar = "https://dev.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
    driver.get(url_agregar)
    time.sleep(5)

    # =====================
    # LLENAR FORMULARIO
    # =====================
    print("📝 Llenando formulario de ubicación...")

    # Ingresar nombre
    #nombre = input("Ingrese el nombre de la sede: ")
    nombre_input = wait.until(EC.presence_of_element_located((By.ID, "advanced_search_name")))
    nombre_input.clear()
    nombre_input.send_keys(nombre)
    time.sleep(3)
    #nombre_input.send_keys(Keys.CONTROL, "a")
    #nombre_input.send_keys(Keys.DELETE)
    print("✅ Nombre de sede ingresado")

    # Ingresar tipo de local
    tipo_tienda = driver.find_element(By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
    tipo_tienda.click()
    time.sleep(5)
    opciones = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
    ))

    for opcion in opciones:
        print(opcion.text)

    for opcion in opciones:
     if opcion.text.strip() == "Tienda":
        opcion.click()
        break

    time.sleep(5)
    print("✅ Tipo de tienda ingresado")

    # Ingresar dirección
    direccion_input = wait.until(EC.presence_of_element_located((By.ID, "advanced_search_address")))
    direccion_input.clear()
    direccion_input.send_keys(direccion)
    ActionChains(driver).move_by_offset(0, 0).click().perform()
    time.sleep(15)
    print("✅ Dirección ingresada")

    driver.execute_script("window.scrollBy(0, 500);")
    print("🔍 Buscando campo de usuario...")
    time.sleep(15)
    # Buscar campo de usuario usando relative locator
    tipo_usuario = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/form/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[5]/div[1]/div[2]/div[1]/div/div")
    tipo_usuario.click()
    time.sleep(15)
    opciones = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
    ))

    # 3. Imprimir todas las opciones que aparecen
    for opcion in opciones:
        print(opcion.text)

    # 4. Seleccionar por texto (ejemplo: "Tienda")
    for opcion in opciones:
        if opcion.text.strip() == usuario:
            opcion.click()
            break
    
    #tipo_usuario.send_keys(usuario)
    print("✅ Campo de usuario encontrado")

    try:
        boton_anadir = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[@type='submit' and contains(text(), 'Añadir')]"
        ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
        time.sleep(2)
        boton_anadir.click()
        print("✅ Botón 'Añadir' clickeado")

        time.sleep(5)

    # =====================
    # VALIDACIÓN: Mensaje de dirección vacía
    # =====================
        try:
            mensaje_error = wait.until(
                EC.presence_of_element_located((
                    By.XPATH, "//*[contains(text(), 'Introduce una dirección de ubicación válida')]"
                ))
            )
            if mensaje_error.is_displayed():
                exito = True
                estado = "ÉXITOSO"
                observaciones = "Se validó correctamente: aparece el mensaje 'Introduce una dirección de ubicación válida'"
            else:
                exito = False
                estado = "FALLIDO"
                observaciones = "No apareció el mensaje esperado de validación de dirección"
        except TimeoutException:
            exito = False
            estado = "FALLIDO"
            observaciones = "No apareció el mensaje 'Introduce una dirección de ubicación válida' en el tiempo esperado"

    except TimeoutException:
        observaciones = "Timeout: No se pudo encontrar o hacer click en el botón 'Añadir'"
        exito = False
        estado = "FALLIDO"
        print("❌ No se pudo encontrar el botón 'Añadir'")

    except Exception as e:
        observaciones = f"Error al intentar guardar la ubicación: {str(e)}"
        exito = False
        estado = "FALLIDO"
        print(f"❌ Error al guardar la ubicación: {str(e)}")

finally:
# Registrar resultado en Google Sheets
    if registrar_resultado(id_caso, estado, observaciones):
        print("✅ Resultado registrado en Google Sheets")
    else:
        print("❌ No se pudo registrar el resultado en Google Sheets")
    
    # Mostrar información final
    print(f"\n🌐 URL final: {driver.current_url}")
    print(f"📄 Título de la página: {driver.title}")
    
    time.sleep(3)
    driver.quit()
    print("✅ Navegador cerrado")

# =====================
# RESUMEN FINAL
# =====================
print("\n" + "="*80)
print("RESUMEN DE EJECUCIÓN - REGISTRO SEDE CON TODOS LOS DATOS")
print("="*80)
print(f"📋 ID Caso: {id_caso}")
print(f"✅ Estado: {estado}")
print(f"🔗 URL Final: {url_final}")
print(f"📝 Observaciones: {observaciones}")
print("="*80)