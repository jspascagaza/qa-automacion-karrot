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
id_caso = "TC017"
#nombre_caja = input("Ingrese el nombre de la caja a crear: ")

try:
    # =====================
    # LOGIN
    # =====================
    print("🔐 Iniciando proceso de login...")
    
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
    email_input.click()
    email_input.send_keys("karrotdev@outlook.com")

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
    # NAVEGACIÓN A UBICACIONES
    # =====================
    ModuloUbicaciones = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/aside/div/ul/li[1]/ul/li[12]/div"))
    )
    ModuloUbicaciones.click()
    time.sleep(5)

    segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
    driver.get(segundopath.get_attribute("href"))
    time.sleep(5)

    listado_editar = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/table/tbody/tr[2]/td[7]/div/button[2]")))
    listado_editar.click()
    editar_caja = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ver Cajas']"))
    )
    editar_caja.click()
    print("✅ Click en Borrar producto")
    time.sleep(5)
    
    boton_agregar_caja = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div[2]/button")))
    boton_agregar_caja.click()
    time.sleep(10)

    try:
     
        nombre_caja = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Nombre de caja' or contains(@class, 'input')]"))
        )
        nombre_caja.clear() 
        nombre_caja.send_keys("C2")
        time.sleep(4)

        boton_agregar_caja = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='ant-btn ant-btn-primary ant-btn-sm w-100' and contains(text(), 'Añadir Caja')]"))
        )
        boton_agregar_caja.click()
        time.sleep(10)
        elemento = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[text()='C2']"))
        )
        observaciones = "Caja creada exitosamente"
        print("✅ Caja creada exitosamente")
        estado = "EXITOSO"
        registrar_resultado(id_caso, estado, observaciones)
    except Exception as e:
        print(f"❌ Error al crear la caja: {str(e)}")
        driver.quit()
        estado = "FALLIDO"
        observaciones = f"Error al crear la caja: {str(e)}"
        registrar_resultado(id_caso, estado, observaciones)
        exit()
except Exception as e:
    print(f"❌ Error: {str(e)}")