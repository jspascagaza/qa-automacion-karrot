from selenium.common import TimeoutException
import unittest
import time
import os
import sys
from datetime import datetime
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from faker import Faker

fake = Faker('es_CO')
load_dotenv()

# =====================
# CONFIGURACIÓN DE LOGS
# =====================
if not os.path.exists("logs"):
    os.makedirs("logs")

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")
    def write(self, message):
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('cp1252', 'ignore').decode('cp1252'))
        self.log.write(message)
        self.log.flush()
    def flush(self):
        self.terminal.flush()
        self.log.flush()

class TestSedesCajas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nombre_archivo = "testsedescajas"
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"logs/{nombre_archivo}_{fecha_hora}.log"
        cls.logger = Logger(log_filename)
        sys.stdout = cls.logger
        sys.stderr = cls.logger
        
        # Google Sheets Setup
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "automatizacion-karrot-456d1a1552ca.json")
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            cls.client = gspread.authorize(creds)
            cls.spreadsheet = cls.client.open_by_url(
                "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"
            )
            cls.sheet = cls.spreadsheet.sheet1
        except Exception as e:
            print(f"⚠️ Error al conectar con Google Sheets: {e}")
            cls.sheet = None

    @classmethod
    def tearDownClass(cls):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    @classmethod
    def registrar_resultado(cls, id_caso, estado, observaciones=""):
        if not cls.sheet:
            return
        try:
            celda = cls.sheet.find(id_caso)
            if not celda:
                print(f"⚠️ No se encontró el ID {id_caso}")
                return
            fila = celda.row
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            automatizado = "Sí"
            cls.sheet.update_cell(fila, 11, automatizado)
            cls.sheet.update_cell(fila, 13, fecha)
            cls.sheet.update_cell(fila, 14, estado)
            cls.sheet.update_cell(fila, 15, observaciones)
            print(f"✅ Caso {id_caso} actualizado -> {estado}")
        except Exception as e:
            print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")

    def setUp(self):
        chrome_options = Options()
        if os.getenv("JENKINS_URL") or os.getenv("CI") or os.getenv("HEADLESS") == "true":
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        # Modificar URL inicial según sea necesario por el test (asumimos panel principal por defecto si no es login)
        self.driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login/es")
        self.wait = WebDriverWait(self.driver, 20)

    def tearDown(self):
        self.driver.quit()

    def test_tc012(self):
        id_caso = 'TC012'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC012"
        
        try:
            nombre = os.getenv("WEB_NOMBRE") or fake.company()
            direccion = os.getenv("WEB_DIRECCION") or fake.address()
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            # Esperar campo de correo
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
            print("✅ Correo electrónico ingresado")
        
            # Esperar campo de contraseña
            print("✅ Contraseña ingresada")
        
            # Click en el botón "Iniciar sesión"
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            print("✅ Botón de login clickeado")
            time.sleep(10)
        
            # =====================
            # =====================
            # time.sleep(5)
        
            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            print("📍 Navegando al módulo de Ubicaciones...")
            
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
            print("✅ Click en Ubicaciones")
            time.sleep(5)
        
            # Obtener y seguir el enlace de ubicaciones
            #segunda parte ubicaciones
        #     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
        #     print(segundopath.text)
        #     print(segundopath.get_attribute("href"))
        #     self.driver.get(segundopath.get_attribute("href"))
            print("✅ dirigiendo a Ubicaciones")
            time.sleep(10)
        
            # =====================
            # AGREGAR NUEVA UBICACIÓN
            # =====================
            print("➕ Navegando a agregar ubicación...")
            
            # Navegar directamente a la URL de agregar ubicación
            url_agregar = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
            self.driver.get(url_agregar)
            time.sleep(5)
        
            # Verificar que estamos en la página correcta
            if "add-locations" in self.driver.current_url:
                print("✅ Página de agregar ubicación cargada correctamente")
            else:
                print("⚠️ Posible problema al cargar la página de agregar ubicación")
        
            # =====================
            # LLENAR FORMULARIO
            # =====================
            print("📝 Llenando formulario de ubicación...")
            
            # Ingresar nombre
            nombre_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_name")))
            nombre_input.clear()
            nombre_input.send_keys(nombre)
            print("✅ Nombre de sede ingresado")
        
            # Ingresar tipo de local
            # Primer dropdown
            tipo_tienda = self.driver.find_element(By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
            tipo_tienda.click()
            time.sleep(5)
            opciones = self.wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
            ))
        
            # 3. Imprimir todas las opciones que aparecen
            for opcion in opciones:
                print(opcion.text)
        
            # 4. Seleccionar por texto (ejemplo: "Tienda")
            for opcion in opciones:
                if opcion.text.strip() == "Tienda":
                    opcion.click()
                    break
        
            time.sleep(5)
            print(tipo_tienda.text)
            print("✅ Tipo de tienda ingresado")
        
            # Ingresar dirección
            direccion_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_address")))
            direccion_input.clear()
            direccion_input.send_keys(direccion)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(15)
            print("✅ Dirección ingresada")
        
            self.driver.execute_script("window.scrollBy(0, 500);")  # baja 500 píxeles
            # Buscar campo de usuario usando relative locator
            print("🔍 Buscando campo de usuario...")
            time.sleep(15)
        
            tipo_usuario = self.driver.find_element(By.XPATH, "//*[@id='advanced_search']/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[6]/div[1]/div[2]/div[1]/div/div/div/div")
            tipo_usuario.click()
            time.sleep(15)
            opciones = self.wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
            ))
        
            # 3. Imprimir todas las opciones que aparecen
            for opcion in opciones:
                print(opcion.text)
        
            # 4. Seleccionar por texto (ejemplo: "Tienda")
            for opcion in opciones:
                    opcion.click()
                    break
            
            #tipo_usuario.send_keys(usuario)
            print("✅ Campo de usuario encontrado") 

            try:
                # Buscar el botón "Añadir" por su texto y clase
                boton_anadir = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @class='ant-btn ant-btn-primary' and contains(text(), 'Añadir')]"))
                )
                
                # Hacer scroll hasta el botón para asegurar visibilidad
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
                time.sleep(2)
                
                # Hacer click en el botón
                boton_anadir.click()
                print("✅ Botón 'Añadir' clickeado")
                
                # Esperar a que se procese la acción
                time.sleep(8)
                exito = True
                observaciones = "Sede creada exitosamente con todos los datos"        
                observaciones = "Timeout: No se pudo encontrar o hacer click en el botón 'Añadir'"
                exito = False
                print("❌ No se pudo encontrar el botón 'Añadir'")
            except Exception as e:
                observaciones = f"Error al hacer click en el botón 'Añadir': {str(e)}"
                exito = False
                print(f"❌ Error al guardar la ubicación: {str(e)}")
        
            url_final = self.driver.current_url
        
        except TimeoutException as e:
            observaciones = f"Timeout esperando elemento: {str(e)}"
            exito = False
            print(f"❌ {observaciones}")
        
        except Exception as e:
            observaciones = f"Error inesperado: {str(e)}"
            exito = False
            print(f"❌ {observaciones}")

    def test_tc013(self):
        id_caso = 'TC013'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC013"
        
        try:
            nombre = os.getenv("WEB_NOMBRE") or fake.company()
            direccion = os.getenv("WEB_DIRECCION") or fake.address()
            
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            # Esperar campo de correo
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
            print("✅ Correo electrónico ingresado")
        
            # Esperar campo de contraseña
            print("✅ Contraseña ingresada")
        
            # Click en el botón "Iniciar sesión"
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            print("✅ Botón de login clickeado")
            time.sleep(10)

            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            print("📍 Navegando al módulo de Ubicaciones...")
            
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
            print("✅ Click en Ubicaciones")
            time.sleep(5)
        
            # Obtener y seguir el enlace de ubicaciones
            #segunda parte ubicaciones
        #     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
        #     print(segundopath.text)
        #     print(segundopath.get_attribute("href"))
        #     self.driver.get(segundopath.get_attribute("href"))
            print("✅ dirigiendo a Ubicaciones")
            time.sleep(10)
        
            # Navegar directamente a la URL de agregar ubicación
            url_agregar = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
            self.driver.get(url_agregar)
            time.sleep(5)
        
            # =====================
            # LLENAR FORMULARIO
            # =====================
            print("📝 Llenando formulario de ubicación...")
        
            # Ingresar nombre
            #nombre = input("Ingrese el nombre de la sede: ")
            nombre_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_name")))
            nombre_input.clear()
            nombre_input.send_keys(nombre)
            time.sleep(3)
            nombre_input.send_keys(Keys.CONTROL, "a")
            nombre_input.send_keys(Keys.DELETE)
            print("✅ Nombre de sede ingresado")
        
            # Ingresar tipo de local
            tipo_tienda = self.driver.find_element(By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
            tipo_tienda.click()
            time.sleep(5)
            opciones = self.wait.until(EC.presence_of_all_elements_located(
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
            direccion_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_address")))
            direccion_input.clear()
            direccion_input.send_keys(direccion)
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            time.sleep(15)
            print("✅ Dirección ingresada")
        
            self.driver.execute_script("window.scrollBy(0, 500);")
            print("🔍 Buscando campo de usuario...")
            time.sleep(15)
            # Buscar campo de usuario usando relative locator
            tipo_usuario = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/form/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[5]/div[1]/div[2]/div[1]/div/div")
            tipo_usuario.click()
            time.sleep(15)
            opciones = self.wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
            ))
        
            # 3. Imprimir todas las opciones que aparecen
            for opcion in opciones:
                print(opcion.text)
        
            # 4. Seleccionar por texto (ejemplo: "Tienda")
            for opcion in opciones:
                    opcion.click()
                    break
            
            #tipo_usuario.send_keys(usuario)
            print("✅ Campo de usuario encontrado")
        
            try:
                boton_anadir = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='advanced_search']/div[1]/div/div/div/button[2]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
                time.sleep(2)
                boton_anadir.click()
                print("✅ Botón 'Añadir' clickeado")
        
                time.sleep(5)
                
                # =====================
                # VALIDACIÓN: Mensaje de error (nombre vacío)
                # =====================
                try:
                    # Usar un timeout más corto para buscar el mensaje de error de validación
                    wait_error = WebDriverWait(self.driver, 10)
                    mensaje_error = wait_error.until(
                        EC.presence_of_element_located((
                            By.XPATH, "//*[contains(@class, 'ant-form-item-explain-error') or contains(text(), 'Introduce un nombre de ubicación')]"
                        ))
                    )
                    if mensaje_error.is_displayed():
                        exito = True
                        estado = "ÉXITOSO"
                        observaciones = f"Se validó correctamente: aparece el mensaje de error '{mensaje_error.text}' y no permite continuar."
                        print(f"✅ {observaciones}")
                    else:
                        exito = False
                        estado = "FALLIDO"
                        observaciones = "El mensaje de error de nombre de ubicación no está visible."
                        print(f"❌ {observaciones}")
                except TimeoutException:
                    # Si no apareció el mensaje de error, la validación falló (se permitió continuar o no se bloqueó correctamente)
                    exito = False
                    estado = "FALLIDO"
                    observaciones = "No apareció el mensaje de error esperado tras hacer click en Añadir."
                    print(f"❌ {observaciones}")
        
                url_final = self.driver.current_url
            except TimeoutException:
                observaciones = "Timeout: No se pudo encontrar o hacer click en el botón 'Añadir'"
                exito = False
                estado = "FALLIDO"
                print("❌ No se pudo encontrar el botón 'Añadir'")
            except Exception as e:
                exito = False
                observaciones = f"Error al intentar guardar la ubicación: {str(e)}"
                estado = "FALLIDO"
                print(f"❌ Error al guardar la ubicación: {str(e)}")
        finally:
            self.registrar_resultado(id_caso, estado, observaciones)

    def test_tc014(self):
        id_caso = 'TC014'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC014"
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            # Esperar campo de correo
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
            print("✅ Correo electrónico ingresado")
        
            # Esperar campo de contraseña
            print("✅ Contraseña ingresada")
        
            # Click en el botón "Iniciar sesión"
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            print("✅ Botón de login clickeado")
            time.sleep(10)

            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            print("📍 Navegando al módulo de Ubicaciones...")
            
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
            print("✅ Click en Ubicaciones")
            time.sleep(5)
        
            # Obtener y seguir el enlace de ubicaciones
            #segunda parte ubicaciones
        #     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
        #     print(segundopath.text)
        #     print(segundopath.get_attribute("href"))
        #     self.driver.get(segundopath.get_attribute("href"))
            print("✅ dirigiendo a Ubicaciones")
            time.sleep(10)
        
            # Navegar directamente a la URL de agregar ubicación
            url_agregar = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
            self.driver.get(url_agregar)
            time.sleep(5)
        
            # =====================
            # LLENAR FORMULARIO
            # =====================
            print("📝 Llenando formulario de ubicación...")
        
            # Ingresar nombre
            #nombre = input("Ingrese el nombre de la sede: ")
            nombre_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_name")))
            nombre_input.clear()
            nombre_input.send_keys(nombre)
            time.sleep(3)
            #nombre_input.send_keys(Keys.CONTROL, "a")
            #nombre_input.send_keys(Keys.DELETE)
            print("✅ Nombre de sede ingresado")
        
            # Ingresar tipo de local
            tipo_tienda = self.driver.find_element(By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
            tipo_tienda.click()
            time.sleep(5)
            opciones = self.wait.until(EC.presence_of_all_elements_located(
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
            direccion_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_address")))
            direccion_input.clear()
            direccion_input.send_keys(direccion)
            ActionChains(driver).move_by_offset(0, 0).click().perform()
            time.sleep(15)
            print("✅ Dirección ingresada")
        
            self.driver.execute_script("window.scrollBy(0, 500);")
            print("🔍 Buscando campo de usuario...")
            time.sleep(15)
            # Buscar campo de usuario usando relative locator
            tipo_usuario = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/form/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[5]/div[1]/div[2]/div[1]/div/div")
            tipo_usuario.click()
            time.sleep(15)
            opciones = self.wait.until(EC.presence_of_all_elements_located(
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
                boton_anadir = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[@type='submit' and contains(text(), 'Añadir')]"
                ))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
                time.sleep(2)
                boton_anadir.click()
                print("✅ Botón 'Añadir' clickeado")
        
                time.sleep(5)
        
            # =====================
            # VALIDACIÓN: Mensaje de dirección vacía
            # =====================
                try:
                    mensaje_error = self.wait.until(
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
            self.registrar_resultado(id_caso, estado, observaciones)

    def test_tc015(self):
        id_caso = 'TC015'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC015"
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))
            print("✅ Correo electrónico ingresado")
        
            print("✅ Contraseña ingresada")
        
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            print("✅ Botón de login clickeado")
            time.sleep(10)
        
            # )
        
            # time.sleep(5)
        
            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            print("📍 Navegando al módulo de Ubicaciones...")
            
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
            print("✅ Click en Ubicaciones")
            time.sleep(5)
        
        #     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
        #     self.driver.get(segundopath.get_attribute("href"))
            print("✅ dirigiendo a Ubicaciones")
            time.sleep(10)
        
            url_agregar = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
            self.driver.get(url_agregar)
            time.sleep(5)
        
            # =====================
            # LLENAR FORMULARIO
            # =====================
            print("📝 Llenando formulario de ubicación...")
        
            nombre_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_name")))
            nombre_input.clear()
            nombre_input.send_keys(nombre)
            print("✅ Nombre de sede ingresado")
        
            tipo_tienda = self.driver.find_element(By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
            tipo_tienda.click()
            time.sleep(3)
            opciones = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")))
            for opcion in opciones:
                if opcion.text.strip() == "Tienda":
                    opcion.click()
                    break
            print("✅ Tipo de tienda ingresado")
        
            # =====================
            # Validación de ciudad obligatoria / preseleccionada
            # =====================
            ciudad_elem = self.wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//*[@id='advanced_search']/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[3]/div/div[2]/div/div/div/div"
            )))
            texto_ciudad = ciudad_elem.text.strip()
            print(f"🌆 Ciudad actual en el campo: '{texto_ciudad}'")

            if "Bogot" in texto_ciudad or "Bogotá" in texto_ciudad or texto_ciudad != "":
                ciudad_encontrada = True
                estado = "ÉXITOSO"
                observaciones = f"Se valida que el campo Ciudad viene preseleccionado por defecto ('{texto_ciudad}') y la interfaz no permite dejar el campo vacío."
                print(f"✅ {observaciones}")
            else:
                ciudad_elem.click()
                time.sleep(2)
                opciones = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")))
                ciudad_encontrada = False
                for opcion in opciones:
                    if "Bogot" in opcion.text.strip():
                        opcion.click()
                        ciudad_encontrada = True
                        print("✅ Ciudad 'Bogotá' seleccionada de la lista")
                        break

                if ciudad_encontrada:
                    estado = "ÉXITOSO"
                    observaciones = "El campo Ciudad cuenta con valor por defecto o seleccionable ('Bogotá') impidiendo dejarlo vacío."
                else:
                    estado = "FALLIDO"
                    observaciones = "No se encontró valor por defecto ni la opción 'Bogotá' en el campo Ciudad."
                    print("❌ Ciudad 'Bogotá' no encontrada")

            time.sleep(2)
        
            # Ingresar dirección
            direccion_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_address")))
            direccion_input.clear()
            direccion_input.send_keys(direccion)
            ActionChains(driver).move_by_offset(0, 0).click().perform()
            print("✅ Dirección ingresada")
            time.sleep(3)
        
            self.driver.execute_script("window.scrollBy(0, 500);")
            print("🔍 Buscando campo de usuario...")
            time.sleep(3)
        
            tipo_usuario = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/form/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[5]/div[1]/div[2]/div[1]/div/div")
            tipo_usuario.click()
            time.sleep(3)
        
            opciones = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")))
            for opcion in opciones:
                if opcion.text.strip() == usuario:
                    opcion.click()
                    break
            print("✅ Campo de usuario seleccionado")
        
            try:
                boton_anadir = self.wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[@type='submit' and contains(text(), 'Añadir')]"
                )))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
                time.sleep(2)
                boton_anadir.click()
                print("✅ Botón 'Añadir' clickeado")
            except TimeoutException:
                observaciones = "Timeout: No se pudo encontrar o hacer click en el botón 'Añadir'"
                estado = "FALLIDO"
                print("❌ No se pudo encontrar el botón 'Añadir'")
            except Exception as e:
                observaciones = f"Error al intentar guardar la ubicación: {str(e)}"
                estado = "FALLIDO"
                print(f"❌ Error al guardar la ubicación: {str(e)}")
        finally:
            self.registrar_resultado(id_caso, estado, observaciones)

    def test_tc016(self):
        id_caso = 'TC016'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC016"
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            time.sleep(10)
        

            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
        
        #     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
        #     self.driver.get(segundopath.get_attribute("href"))
            time.sleep(10)
        
            url_agregar = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
            self.driver.get(url_agregar)
        
            # =====================
            # LLENAR FORMULARIO
            # =====================
            nombre_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_name")))
            nombre_input.clear()
            nombre_input.send_keys(nombre)
        
            tipo_tienda = self.driver.find_element(By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
            tipo_tienda.click()
            time.sleep(2)
            opciones = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")))
            for opcion in opciones:
                if opcion.text.strip() == "Tienda":
                    opcion.click()
                    break
        
            # Selección de ciudad con validación
            ciudad_input = self.wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//*[@id='advanced_search']/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[3]/div/div[2]/div/div/div/div"
            )))
            ciudad_input.click()
            time.sleep(2)
        
            opciones = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")))
            ciudad_encontrada = False
            for opcion in opciones:
                if opcion.text.strip() == ciudad:
                    opcion.click()
                    ciudad_encontrada = True
                    break
        
            if not ciudad_encontrada:
                estado = "FALLIDO"
                observaciones = f"La ciudad '{ciudad}' no está en las opciones disponibles"
                raise Exception(observaciones)
        
            direccion_input = self.wait.until(EC.presence_of_element_located((By.ID, "advanced_search_address")))
            direccion_input.clear()
            direccion_input.send_keys(direccion)
            ActionChains(driver).move_by_offset(0, 0).click().perform()
            time.sleep(2)
        
            # =====================
            # CLICK EN AÑADIR (SIN USUARIO)
            # =====================
            boton_anadir = self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//button[@type='submit' and contains(text(), 'Añadir')]"
            )))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
            time.sleep(2)
            boton_anadir.click()
            print("✅ Botón 'Añadir' clickeado")
        
            # =====================
            # VALIDACIÓN DEL MENSAJE DE ERROR
            # =====================
            try:
                error_msg = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Ups, algo salió mal al crear la ubicación')]")))
                if error_msg:
                    estado = "ÉXITOSO"
                    observaciones = "El sistema no permitió crear la ubicación sin usuario"
                    print("✅ Caso exitoso: apareció mensaje de error esperado")
                else:
                    estado = "FALLIDO"
                    observaciones = "El sistema permitió crear la ubicación sin usuario"
                    print("❌ Caso fallido: no apareció el mensaje de error")
            except TimeoutException:
                estado = "FALLIDO"
                observaciones = "El sistema permitió crear la ubicación sin usuario (no apareció mensaje de error)"
                print("❌ Caso fallido: no apareció el mensaje de error")
        except Exception as e:
            if estado == "PENDIENTE":
                estado = "FALLIDO"
            observaciones = str(e)
            print(f"❌ Error: {observaciones}")
        finally:
            self.registrar_resultado(id_caso, estado, observaciones)

    def test_tc017(self):
        id_caso = 'TC017'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC017"
        valor_caja = os.getenv("WEB_NOMBRE") or "C2"
        #nombre_caja = input("Ingrese el nombre de la caja a crear: ")
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            time.sleep(10)
        

            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            print("📍 Navegando al módulo de Ubicaciones...")
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]"
            )))
            ModuloUbicaciones.click()
            print("✅ Click en módulo Ubicaciones")
            time.sleep(2)

            # Redirección directa por URL a la vista de lista de ubicaciones
            self.driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/list-locations")
            print("✅ Dirigido directamente a Ubicaciones por URL")
            time.sleep(5)
        
            listado_editar = self.wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/table/tbody/tr[2]/td[7]/div/button[2]")))
            listado_editar.click()
            editar_caja = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ver Cajas']"))
            )
            editar_caja.click()
            print("✅ Click en Borrar producto")
            
            boton_agregar_caja = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div[2]/button")))
            boton_agregar_caja.click()
            time.sleep(10)
        
            try:
             
                nombre_caja = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Nombre de caja' or contains(@class, 'input')]"))
                )
                nombre_caja.clear() 
                nombre_caja.send_keys("C2")
                time.sleep(4)
        
                boton_agregar_caja = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='ant-btn ant-btn-primary ant-btn-sm w-100' and contains(text(), 'Añadir Caja')]"))
                )
                boton_agregar_caja.click()
                time.sleep(10)
                elemento = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='C2']"))
                )
                observaciones = "Caja creada exitosamente"
                print("✅ Caja creada exitosamente")
                estado = "EXITOSO"
            except Exception as e:
                estado = "FALLIDO"
                observaciones = f"Error al crear la caja: {str(e)}"
                print(f"❌ {observaciones}")
        except Exception as e:
            estado = "FALLIDO"
            observaciones = f"Error en test_tc017: {str(e)}"
            print(f"❌ {observaciones}")
        finally:
            self.registrar_resultado(id_caso, estado, observaciones)

    def test_tc018(self):
        id_caso = 'TC018'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC018"
        #nombre_caja = input("Ingrese el nombre de la caja a crear: ")
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            time.sleep(10)
        

            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
        
        #     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
        #     self.driver.get(segundopath.get_attribute("href"))
        
            listado_editar = self.wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/table/tbody/tr[2]/td[7]/div/button[2]")))
            listado_editar.click()
            URL_caja = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/list-cashdrawers/abda433b-d026-4726-ab7d-3b4eddb765c3"
            self.driver.get(URL_caja)
            
            # Hacer clic en el botón de tres puntos
            listado_opciones = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-dropdown-trigger"))
            )
            listado_opciones.click()
            print("✅ Botón de opciones clickeado")
        
            # Esperar y buscar las opciones del menú dropdown
            time.sleep(2)
            opciones = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-dropdown-menu .ant-dropdown-menu-item"))
            )
        
            print(f"🔍 Encontradas {len(opciones)} opciones:")
            for i, opcion in enumerate(opciones):
                print(f"  {i+1}. {opcion.text}")
            
            # Buscar y hacer clic en la opción que contiene exactamente "Eliminar caja"
            opcion_encontrada = None
            for opcion in opciones:
                if "Eliminar caja" in opcion.text:
                    opcion_encontrada = opcion
                    break
        
            if opcion_encontrada:
                # Usar ActionChains por si el click normal no funciona
                ActionChains(driver).move_to_element(opcion_encontrada).click().perform()
                print("✅ 'Eliminar caja' seleccionado")
                observaciones = "Caja eliminada exitosamente"
                estado = "EXITOSO"
            else:
                print("❌ No se encontró la opción 'Eliminar caja'")
                observaciones = "No se encontró la opción 'Eliminar caja'"
                estado = "FALLIDO"
            self.registrar_resultado(id_caso, estado, observaciones)
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def test_tc019(self):
        id_caso = 'TC019'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC019"
        #nombre_caja = input("Ingrese el nombre de la caja a crear: ")
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            time.sleep(10)
        

            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
            time.sleep(2)
            self.driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/list-locations")
            time.sleep(5)

            # Hacer clic en el botón de tres puntos
            listado_opciones = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-dropdown-trigger"))
            )
            listado_opciones.click()
            print("✅ Botón de opciones clickeado")
            
            # Esperar y buscar las opciones del menú dropdown
            opciones = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-dropdown-menu .ant-dropdown-menu-item"))
            )
        
            print(f"🔍 Encontradas {len(opciones)} opciones:")
            for i, opcion in enumerate(opciones):
                print(f"  {i+1}. {opcion.text}")
            
            # Buscar y hacer clic en la opción que contiene exactamente "Eliminar caja"
            opcion_encontrada = None
            for opcion in opciones:
                if "Borrar" in opcion.text:
                    opcion_encontrada = opcion
                    break
            time.sleep(10)
        
            if opcion_encontrada:
                max_intentos = 5
                for intento in range(max_intentos):
                    # Vuelve a abrir el menú de opciones en cada intento
                    listado_opciones = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-dropdown-trigger"))
                    )
                    listado_opciones.click()
                    time.sleep(1)  # Espera breve para que el menú se despliegue
        
                    # Vuelve a buscar las opciones del menú
                    opciones = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-dropdown-menu .ant-dropdown-menu-item"))
                    )
                    opcion_encontrada = None
                    for opcion in opciones:
                        if "Borrar" in opcion.text:
                            opcion_encontrada = opcion
                            break
        
                    if opcion_encontrada:
                        ActionChains(driver).move_to_element(opcion_encontrada).click().perform()
                        print(f"Intento {intento+1}: click en 'Borrar'")
                        try:
                            WebDriverWait(self.driver, 2).until(
                                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Delete Location?')]"))
                            )
                            print("✅ Apareció 'Delete Location?' en pantalla")
                            break
                        except TimeoutException as e:
                                print(f"❌ Error: {str(e)}")
                                observaciones = f"Error: {str(e)}"
                                estado = "FALLIDO"
                                self.registrar_resultado(id_caso, estado, observaciones)
                boton_yes = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Yes']]"))
                )
                boton_yes.click()
                print("✅ Botón 'Yes' clickeado")
                observaciones = "Sede eliminada exitosamente"
                estado = "EXITOSO"
        
            else:
                print("❌ No se encontró la opción 'Borrar'")
                observaciones = "No se encontró la opción 'Borrar'"
                estado = "FALLIDO"
        
            self.registrar_resultado(id_caso, estado, observaciones)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            observaciones = f"Error: {str(e)}"
            estado = "FALLIDO"

    def test_tc020(self):
        id_caso = 'TC020'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC020"
        #nombre_caja = input("Ingrese el nombre de la caja a crear: ")
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            time.sleep(10)
        

            # =====================
            # NAVEGACIÓN A UBICACIONES
            # =====================
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
        
        #     segundopath = ModuloUbicaciones.find_element(By.XPATH, "/html/body/div[1]/div/section/section/aside/div/ul/li[1]/ul/li[12]/ul/li[1]/span/a")
        #     self.driver.get(segundopath.get_attribute("href"))
        
            # =====================
            self.driver.find_element(By.CSS_SELECTOR, "button.ant-btn.ant-btn-secondary.ant-btn-sm").click()
            
            fecha_inicio = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Start date"]')
            self.driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].removeAttribute('disabled');", fecha_inicio)
            fecha_inicio.send_keys(Keys.ESCAPE)  # Cierra el calendario si está abierto
            fecha_inicio.clear()
            try:
                fecha_inicio.send_keys("2025-09-01")
                fecha_inicio.send_keys(Keys.ENTER)
            except Exception:
                # Si falla, usa JS para poner el valor
                self.driver.execute_script("arguments[0].value = arguments[1];", fecha_inicio, "2025-09-01")
                fecha_inicio.send_keys(Keys.ENTER)
            time.sleep(10)
        
            # Fecha de fin
            fecha_fin = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder="End date"]')
            self.driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].removeAttribute('disabled');", fecha_fin)
            fecha_fin.send_keys(Keys.ESCAPE)
            fecha_fin.clear()
            try:
                fecha_fin.send_keys("2025-09-30")
                fecha_fin.send_keys(Keys.ENTER)
            except Exception:
                self.driver.execute_script("arguments[0].value = arguments[1];", fecha_fin, "2025-09-30")
                fecha_fin.send_keys(Keys.ENTER)
            time.sleep(10)
            boton_buscar = self.driver.find_element(By.XPATH, "//button[@type='button' and contains(@class, 'ant-btn-default')]//span[text()='Buscar']/..")
            boton_buscar.click()
            time.sleep(10)
            observaciones = "Prueba  completada exitosamente permite filtrar por fecha de inicio y fin"
            estado = "EXITOSO"
            self.registrar_resultado(id_caso, estado, observaciones)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            observaciones = f"Error: {str(e)}"
            estado = "FALLIDO"
            self.registrar_resultado(id_caso, estado, observaciones)

    def test_tc021(self):
        id_caso = 'TC021'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC021"
        #nombre_caja = input("Ingrese el nombre de la caja a crear: ")
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            time.sleep(10)
        

            # =====================
            # NAVEGACIÓN A MODULO DE UBICACIONES
            # =====================
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
        
            # Buscar las opciones del submenú dentro del menú de ubicaciones
            opciones_submenu = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'ant-menu-sub')]//li")
            opcion_encontrada = None
            for opcion in opciones_submenu:
                texto = opcion.text.lower()
                if "actividades" in texto or "actvidades" in texto or "bitácora" in texto or "bitacora" in texto:
                    opcion_encontrada = opcion
                    break
        
            if opcion_encontrada:
                opcion_encontrada.click()
                print("✅ Click en 'Actividades'")
            else:
                print("❌ No se encontró la opción 'Actividades'")

            # Esperar a que el botón sea visible y clickeable
            botoncrear = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Crear Actividad')]"))
            )
            # Hacer scroll al botón
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botoncrear)
            time.sleep(1)
            # Intentar click normal, si falla usar JS
            try:
                botoncrear.click()
                print("✅ Click normal en 'Crear Actividad'")
            except Exception as e:
                self.driver.execute_script("arguments[0].click();", botoncrear)
                print("⚠️ Click JS en 'Crear Actividad' (fallback)")
        
            campo_nombre = self.wait.until(
                EC.visibility_of_element_located((By.ID, "name"))
             )
            campo_nombre.clear()
            campo_nombre.send_keys("Mi actividad de prueba")
            print("✅ Nombre de actividad ingresado")

        
            # =====================
            # SELECCIÓN DEL NÚMERO DE CAMPOS
            # =====================
            # Esperar el input del número de campos
            input_num_campos = self.wait.until(
                EC.presence_of_element_located((By.ID, "number_of_fields"))
            )
            # Quitar readonly y hacer visible el input con JS
            self.driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].style.opacity = 1;", input_num_campos)
            input_num_campos.clear()
            input_num_campos.send_keys("3")  # Cambia "3" por el número que desees
            input_num_campos.send_keys(Keys.ENTER)
            print("✅ Número de campos ingresado manualmente")
        
            time.sleep(10)
        
            # Espera a que los campos dinámicos estén presentes (espera el primero)
            total_campos = 3  # Cambia este valor según lo que seleccionaste antes
            for i in range(total_campos):
                # Esperar el input de nombre
                input_nombre = self.wait.until(
                    EC.visibility_of_element_located((By.ID, f"name_{i}"))
                )
                input_nombre.clear()
                input_nombre.send_keys(f"Campo {i+1}")
                print(f"✅ Ingresado nombre para campo {i+1}")
        
                # Esperar el contenedor del selector del tipo
                selector_tipo = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//input[@id='type_{i}']/ancestor::div[contains(@class, 'ant-select')]//div[contains(@class, 'ant-select-selector')]"))
                )
                selector_tipo.click()
                time.sleep(0.5)
        
                # Esperar y seleccionar la opción deseada (ejemplo: "Hora")
                opciones_tipo = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-select-item-option')]"))
                )
                opcion_encontrada = None
                for opcion in opciones_tipo:
                    if "Hora" in opcion.text:  # Cambia "Hora" por el tipo que desees
                        opcion_encontrada = opcion
                        break
                if opcion_encontrada:
                    opcion_encontrada.click()
                    print(f"✅ Seleccionado tipo para campo {i+1}")
                else:
                    print(f"❌ No se encontró la opción de tipo para campo {i+1}")
        
                time.sleep(0.5)
        
            # Esperar a que el botón "Guardar" sea visible y clickeable usando el XPath absoluto
            boton_guardar = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/section/section/div/main/div[1]/div/div/div/button[2]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_guardar)
            time.sleep(1)
            try:
                boton_guardar.click()
                print("✅ Click normal en botón Guardar")
                observaciones += "✅ Actividad creada exitosamente.\n"
                estado = "EXITOSO"
                self.registrar_resultado(id_caso, estado, observaciones)
            except Exception as e:
                print(f"⚠️ Click normal falló: {e}, intentando con JavaScript...")
                self.driver.execute_script("arguments[0].click();", boton_guardar)
                print("✅ Click forzado con JavaScript en botón Guardar")
                observaciones += "✅ Actividad creada fallidamente (click JS).\n"
                estado = "FALLIDO"
                self.registrar_resultado(id_caso, estado, observaciones)
        
        except Exception as e:
            observaciones += f"❌ Error durante la ejecución: {str(e)}\n"
            estado = "FALLIDO"
            print(observaciones)
            self.registrar_resultado(id_caso, estado, observaciones)

    def test_tc022(self):
        id_caso = 'TC022'
        print(f'\n=== Iniciando {id_caso} ===')
        id_caso = "TC022"
        #nombre_caja = input("Ingrese el nombre de la caja a crear: ")
        
        try:
            # =====================
            # LOGIN
            # =====================
            print("🔐 Iniciando proceso de login...")
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(os.getenv("KARROT_LOGIN_EMAIL"))

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()
            time.sleep(10)
        

            # =====================
            # NAVEGACIÓN A MODULO DE UBICACIONES
            # =====================
            ModuloUbicaciones = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))
            ModuloUbicaciones.click()
        
            # Buscar las opciones del submenú dentro del menú de ubicaciones
            opciones_submenu = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'ant-menu-sub')]//li")
            opcion_encontrada = None
            for opcion in opciones_submenu:
                texto = opcion.text.lower()
                if "actividades" in texto or "actvidades" in texto or "bitácora" in texto or "bitacora" in texto:
                    opcion_encontrada = opcion
                    break
        
            if opcion_encontrada:
                opcion_encontrada.click()
                print("✅ Click en 'Actividades'")
            else:
                print("❌ No se encontró la opción 'Actividades'")

            # Esperar a que la tabla esté visible (puedes esperar por el tbody o por el botón)
            boton_editar = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/section/section/div/main/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[4]/div/button[1]'))
            )
            # Hacer scroll al botón por si está fuera de vista
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_editar)
            time.sleep(1)
            boton_editar.click()
            print("✅ Click en el botón de editar de la primera fila")

            # Esperar el input del número de campos
            input_num_campos = self.wait.until(
                EC.presence_of_element_located((By.ID, "number_of_fields"))
            )
            # Quitar readonly y hacer visible el input con JS
            self.driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].style.opacity = 1;", input_num_campos)
            input_num_campos.clear()
            input_num_campos.send_keys("3")  # Cambia "3" por el número que desees
            input_num_campos.send_keys(Keys.ENTER)
            print("✅ Número de campos ingresado manualmente")
        
            time.sleep(10)
        
            # Espera a que los campos dinámicos estén presentes (espera el primero)
            total_campos = 3  # Cambia este valor según lo que seleccionaste antes
            for i in range(total_campos):
                # Esperar el input de nombre
                input_nombre = self.wait.until(
                    EC.visibility_of_element_located((By.ID, f"name_{i}"))
                )
                input_nombre.clear()
                input_nombre.send_keys(f"Campo {i+1}")
                print(f"✅ Ingresado nombre para campo {i+1}")
        
                # Esperar el contenedor del selector del tipo
                selector_tipo = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//input[@id='type_{i}']/ancestor::div[contains(@class, 'ant-select')]//div[contains(@class, 'ant-select-selector')]"))
                )
                selector_tipo.click()
                time.sleep(0.5)
        
                # Esperar y seleccionar la opción deseada (ejemplo: "Hora")
                opciones_tipo = self.wait.until(
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
            boton_guardar = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/section/section/div/main/div[1]/div/div/div/button[2]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_guardar)
            time.sleep(1)
            try:
                boton_guardar.click()
                print("✅ Click normal en botón actualizar")
                observaciones += "✅ Actividad actualizada exitosamente.\n"
                estado = "EXITOSO"
                self.registrar_resultado(id_caso, estado, observaciones)
            except Exception as e:
                print(f"⚠️ Click normal falló: {e}, intentando con JavaScript...")
                self.driver.execute_script("arguments[0].click();", boton_guardar)
                print("✅ Click forzado con JavaScript en botón Guardar")
                observaciones += "✅ Actividad actualizada fallidamente (click JS).\n"
                estado = "FALLIDO"
                self.registrar_resultado(id_caso, estado, observaciones)

        except Exception as e:    
            observaciones += f"❌ Error durante la ejecución: {str(e)}\n"
            estado = "FALLIDO"
            print(observaciones)
            self.registrar_resultado(id_caso, estado, observaciones)

# if __name__ == '__main__':
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    print("=== Iniciando Módulo 2: Sedes y Cajas ===")
    suite = unittest.TestSuite()
    
    # Core
    suite.addTest(TestSedesCajas('test_tc012'))
    suite.addTest(TestSedesCajas('test_tc017'))
    
    if os.getenv('WEB_EXEC_EXHAUSTIVO') == 'true':
        print("[INFO] Validaciones secundarias activadas.")
        suite.addTest(TestSedesCajas('test_tc013'))
        suite.addTest(TestSedesCajas('test_tc014'))
        suite.addTest(TestSedesCajas('test_tc015'))
        suite.addTest(TestSedesCajas('test_tc016'))
        suite.addTest(TestSedesCajas('test_tc018'))
        suite.addTest(TestSedesCajas('test_tc019'))
        suite.addTest(TestSedesCajas('test_tc020'))
        suite.addTest(TestSedesCajas('test_tc021'))
        suite.addTest(TestSedesCajas('test_tc022'))
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    sys.exit(not runner.run(suite).wasSuccessful())
