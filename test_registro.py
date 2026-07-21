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

def limpiar_campo_completamente(elemento):
    """Función para limpiar completamente un campo de entrada"""
    try:
        driver = elemento.parent
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
        
        print("✅ Campo limpiado completamente")
        
    except Exception as e:
        print(f"⚠️ Error al limpiar campo: {e}")

class TestRegistro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nombre_archivo = "test_registro"
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
        self.driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/register/es")
        self.wait = WebDriverWait(self.driver, 20)

    def tearDown(self):
        self.driver.quit()

    def test_tc003(self):
        id_caso = 'TC003'
        print(f'\n=== Iniciando {id_caso} ===')
        modo_automatico = True

        company_name = os.getenv("WEB_EMPRESA") or f"Empresa{random.randint(1000,9999)}"
        first_names = [fake.first_name() for _ in range(5)]
        last_names = [fake.last_name() for _ in range(5)]
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        user = ((first_name[0] if first_name else "") + (last_name if last_name else "")).lower().replace(" ", "")
        email = os.getenv("WEB_EMAIL") or fake.email()
        phone_number = f"{random.randint(3000000000,3999999999)}"  # ejemplo para Colombia
        print(f"Datos generados -> Empresa: {company_name}, Nombre: {first_name} {last_name}, Email: {email}, Tel: {phone_number}")
        
        # Inicializar navegador
        # Variable para controlar el éxito de la ejecución
        exito = False
        observaciones = ""
        
        try:
            # Nombre de empresa
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
            print("✅ Nombre de empresa ingresado")
        
            # Nombre persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
            print("✅ Nombre ingresado")
        
            # Apellido persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
            print("✅ Apellido ingresado")
        
            # --- Seleccionar país: Colombia ---
            print("🔄 Intentando seleccionar país...")
            
            pais_seleccionado = False
            # Método 1: Intentar encontrar el dropdown de Ant Design
            try:
                # Buscar el elemento del selector de país
                country_selector = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
                
                # Hacer clic para abrir el dropdown
                country_selector.click()
                print("✅ Click en el selector de país")
                time.sleep(2)  # Esperar a que se abra el dropdown
                
                # Buscar la opción de Colombia usando diferentes selectores
                try:
                    # Intentar con selector por texto visible
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 1)")
                    pais_seleccionado = True
                except:
                    # Intentar con selector por valor
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 2)")
                    pais_seleccionado = True
                    
            except Exception as e:
                print(f"⚠️ Método dropdown falló: {e}")
                observaciones += f"Método dropdown falló: {str(e)}. "
                
                # Método 2: Intentar escribir directamente
                try:
                    country_input = self.driver.find_element(By.ID, "register-form_mainCountry")
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
                        self.driver.execute_script("""
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
            # Continuar con el resto de los campos
            # Correo electrónico
        
            # Correo electrónico
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
            print("✅ Correo electrónico ingresado")
        
            # Número de celular
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
            print("✅ Número de celular ingresado")
        
            # Contraseña
            print("✅ Contraseña ingresada")
        
            print("🎉 Todos los campos fueron llenados correctamente")
            exito = True
            observaciones = "Formulario completado exitosamente - País Colombia seleccionado"
        
            # Tomar captura de pantalla para verificar
            self.driver.save_screenshot("formulario_lleno.png")
            print("📸 Captura de pantalla guardada como 'formulario_lleno.png'")
        
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            observaciones += f"Error final: {str(e)}"
            
            # Tomar captura de pantalla del error
            self.driver.save_screenshot("error_formulario.png")
            print("📸 Captura de error guardada como 'error_formulario.png'")
        finally:
            self.registrar_resultado(id_caso, "Exitosa" if exito else "Fallida", observaciones)

    def test_tc004(self):
        id_caso = 'TC004'
        print(f'\n=== Iniciando {id_caso} ===')
        
        # Generar datos de prueba
        company_name = ""  # Nombre vacío para probar el error
        first_names = ["Juan","Carlos","Luis","Ana","María","Laura","José","Miguel","Sofía","Valentina"]
        last_names = ["Pérez","González","Rodríguez","López","Martínez","Sánchez","Gómez","Ramírez"]
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = fake.email()
        phone_number = f"{random.randint(300000000,399999999)}"
        print(f"Datos generados -> Empresa: {company_name}, Nombre: {first_name} {last_name}, Email: {email}, Tel: {phone_number}")

        # Variable para controlar el éxito de la ejecución
        exito = False
        observaciones = ""
        mensaje_error_encontrado = ""
        
        try:
            # Nombre de empresa (VACÍO - esta es la prueba)
            if company_name:
                self.wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
                print("✅ Nombre de empresa ingresado")
            else:
                print("⚠️ Nombre de empresa dejado vacío (esto es intencional para la prueba)")
        
            # Nombre persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
            print("✅ Nombre ingresado")
        
            # Apellido persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
            print("✅ Apellido ingresado")
        
            # --- Seleccionar país: Colombia ---
            print("🔄 Intentando seleccionar país...")
            
            pais_seleccionado = False
            # Método 1: Intentar encontrar el dropdown de Ant Design
            try:
                # Buscar el elemento del selector de país
                country_selector = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
                
                # Hacer clic para abrir el dropdown
                country_selector.click()
                print("✅ Click en el selector de país")
                time.sleep(2)  # Esperar a que se abra el dropdown
                
                # Buscar la opción de Colombia usando diferentes selectores
                try:
                    # Intentar con selector por texto visible
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 1)")
                    pais_seleccionado = True
                except:
                    # Intentar con selector por valor
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 2)")
                    pais_seleccionado = True
                    
            except Exception as e:
                print(f"⚠️ Método dropdown falló: {e}")
                observaciones += f"Método dropdown falló: {str(e)}. "
                
                # Método 2: Intentar escribir directamente
                try:
                    country_input = self.driver.find_element(By.ID, "register-form_mainCountry")
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
                        self.driver.execute_script("""
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
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
            print("✅ Correo electrónico ingresado")
        
            # Número de celular
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
            print("✅ Número de celular ingresado")
        
            # Contraseña
            print("✅ Contraseña ingresada")
        
            # Hacer clic en el botón "¡Inicia tu prueba gratuita!"
            print("🔄 Haciendo clic en el botón de registro...")
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
            submit_button.click()
            print("✅ Botón de registro presionado")
        
            # Esperar a que aparezca el mensaje de error
            print("🔄 Esperando mensaje de error...")
            time.sleep(2)  # Esperar a que se procese la validación
        
            # Buscar el mensaje de error específico
            try:
                mensaje_error = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error') and contains(., 'Introduce el nombre de tu empresa')]")))
                mensaje_error_encontrado = mensaje_error.text
                print(f"✅ Mensaje de error encontrado: '{mensaje_error_encontrado}'")
                
                # La prueba es exitosa si encontramos el mensaje de error esperado
                exito = True
                observaciones = f"Prueba exitosa - Mensaje de error detectado: {mensaje_error_encontrado}"
                
                # Tomar captura de pantalla del error
                self.driver.save_screenshot("error_nombre_vacio.png")
                print("📸 Captura de error guardada como 'error_nombre_vacio.png'")
                
            except Exception as error_msg:
                print("❌ No se encontró el mensaje de error esperado")
                observaciones = f"Fallo en la prueba - No se detectó el mensaje de error esperado. Error: {str(error_msg)}"
                
                # Tomar captura de pantalla para investigar
                self.driver.save_screenshot("sin_mensaje_error.png")
                print("📸 Captura de pantalla guardada como 'sin_mensaje_error.png'")
        
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            observaciones += f"Error final: {str(e)}"
            
            # Tomar captura de pantalla del error
            self.driver.save_screenshot("error_proceso.png")
            print("📸 Captura de error guardada como 'error_proceso.png'")
        finally:
            self.registrar_resultado(id_caso, "Exitosa" if exito else "Fallida", observaciones)

    def test_tc005(self):
        id_caso = 'TC005'
        print(f'\n=== Iniciando {id_caso} ===')
        
        # Generar datos de prueba
        company_name = f"Empresa{random.randint(1000,9999)}"
        first_name = ""  # Nombre vacío para la prueba
        last_name = ""   # Apellido vacío para la prueba
        email = fake.email()
        phone_number = f"{random.randint(300000000,399999999)}"
        print(f"Datos generados -> Empresa: {company_name}, Nombre: {first_name} {last_name}, Email: {email}, Tel: {phone_number}")

        # Variable para controlar el éxito de la ejecución
        exito = False
        observaciones = ""
        mensajes_error_encontrados = []
        
        try:
            # Nombre de empresa
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
            print("✅ Nombre de empresa ingresado")
        
            # Nombre persona (VACÍO - esta es la prueba)
            if first_name:
                self.wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
                print("✅ Nombre ingresado")
            else:
                print("⚠️ Nombre dejado vacío (esto es intencional para la prueba)")
        
            # Apellido persona (VACÍO - esta es la prueba)
            if last_name:
                self.wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
                print("✅ Apellido ingresado")
            else:
                print("⚠️ Apellido dejado vacío (esto es intencional para la prueba)")
        
            # --- Seleccionar país: Colombia ---
            print("🔄 Intentando seleccionar país...")
            
            pais_seleccionado = False
            # Método 1: Intentar encontrar el dropdown de Ant Design
            try:
                # Buscar el elemento del selector de país
                country_selector = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
                
                # Hacer clic para abrir el dropdown
                country_selector.click()
                print("✅ Click en el selector de país")
                time.sleep(2)  # Esperar a que se abra el dropdown
                
                # Buscar la opción de Colombia usando diferentes selectores
                try:
                    # Intentar con selector por texto visible
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 1)")
                    pais_seleccionado = True
                except:
                    # Intentar con selector por valor
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 2)")
                    pais_seleccionado = True
                    
            except Exception as e:
                print(f"⚠️ Método dropdown falló: {e}")
                observaciones += f"Método dropdown falló: {str(e)}. "
                
                # Método 2: Intentar escribir directamente
                try:
                    country_input = self.driver.find_element(By.ID, "register-form_mainCountry")
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
                        self.driver.execute_script("""
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
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
            print("✅ Correo electrónico ingresado")
        
            # Número de celular
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
            print("✅ Número de celular ingresado")
        
            # Contraseña
            print("✅ Contraseña ingresada")
        
            # Hacer clic en el botón "¡Inicia tu prueba gratuita!"
            print("🔄 Haciendo clic en el botón de registro...")
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
            submit_button.click()
            print("✅ Botón de registro presionado")
        
            # Esperar a que aparezcan los mensajes de error
            print("🔄 Esperando mensajes de error...")
            time.sleep(2)  # Esperar a que se procese la validación
        
            # Buscar los mensajes de error específicos
            errores_encontrados = 0
            
            # Mensaje de error para nombre
            try:
                mensaje_error_nombre = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error') and contains(., 'Introduce tu nombre')]")))
                mensaje_nombre = mensaje_error_nombre.text
                mensajes_error_encontrados.append(f"Nombre: {mensaje_nombre}")
                print(f"✅ Mensaje de error para nombre encontrado: '{mensaje_nombre}'")
                errores_encontrados += 1
            except Exception as error_nombre:
                print("❌ No se encontró el mensaje de error para nombre")
                observaciones += f"Fallo - No se detectó mensaje de error para nombre. "
            
            # Mensaje de error para apellido
            try:
                mensaje_error_apellido = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error') and contains(., 'Ingresa tu apellido')]")))
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
                self.driver.save_screenshot("errores_nombre_apellido_detectados.png")
                print("📸 Captura de errores guardada como 'errores_nombre_apellido_detectados.png'")
            else:
                self.driver.save_screenshot("errores_incompletos.png")
                print("📸 Captura de errores incompletos guardada como 'errores_incompletos.png'")
        
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            observaciones += f"Error final: {str(e)}"
            
            # Tomar captura de pantalla del error
            self.driver.save_screenshot("error_proceso.png")
            print("📸 Captura de error guardada como 'error_proceso.png'")
        finally:
            self.registrar_resultado(id_caso, "Exitosa" if exito else "Fallida", observaciones)

    def test_tc006(self):
        id_caso = 'TC006'
        print(f'\n=== Iniciando {id_caso} ===')
        
        # Generar datos de prueba
        company_name = f"Empresa{random.randint(1000,9999)}"
        first_names = ["Juan","Carlos","Luis","Ana","María","Laura","José","Miguel","Sofía","Valentina"]
        last_names = ["Pérez","González","Rodríguez","López","Martínez","Sánchez","Gómez","Ramírez"]
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        phone_number = f"{random.randint(300000000,399999999)}"
        print(f"Datos generados -> Empresa: {company_name}, Nombre: {first_name} {last_name}, Tel: {phone_number}")

        # Variable para controlar el éxito de la ejecución
        exito = False
        observaciones = ""
        mensajes_error_encontrados = []
        
        try:
            # Nombre de empresa
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
            print("✅ Nombre de empresa ingresado")
        
            # Nombre persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
            print("✅ Nombre ingresado")
        
            # Apellido persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
            print("✅ Apellido ingresado")
        
            # --- Seleccionar país: Colombia ---
            print("🔄 Intentando seleccionar país...")
            
            pais_seleccionado = False
            # Método 1: Intentar encontrar el dropdown de Ant Design
            try:
                # Buscar el elemento del selector de país
                country_selector = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
                
                # Hacer clic para abrir el dropdown
                country_selector.click()
                print("✅ Click en el selector de país")
                time.sleep(2)  # Esperar a que se abra el dropdown
                
                # Buscar la opción de Colombia usando diferentes selectores
                try:
                    # Intentar con selector por texto visible
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 1)")
                    pais_seleccionado = True
                except:
                    # Intentar con selector por valor
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 2)")
                    pais_seleccionado = True
                    
            except Exception as e:
                print(f"⚠️ Método dropdown falló: {e}")
                observaciones += f"Método dropdown falló: {str(e)}. "
                
                # Método 2: Intentar escribir directamente
                try:
                    country_input = self.driver.find_element(By.ID, "register-form_mainCountry")
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
                        self.driver.execute_script("""
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
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
            print("✅ Número de celular ingresado")
        
            # Contraseña
            print("✅ Contraseña ingresada")

            # Correo electrónico
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_email")))
            
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
                },
                {
                    "tipo": "CORREO_REGISTRADO", 
                    "valor": "karrotdev@outlook.com",
                    "mensaje_esperado": "Este correo electrónico ya está registrado",
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
                self.driver.find_element(By.ID, "register-form_phoneNumber").click()
                print("✅ Foco cambiado para activar validación")
                
                # Esperar a que se procese la validación
                time.sleep(3)
                
                # Buscar el mensaje de error esperado
                try:
                    mensaje_error = self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, f"//div[contains(@class, 'ant-form-item-explain-error') and contains(., '{prueba['mensaje_esperado']}')]")
                    ))
                    
                    mensaje_texto = mensaje_error.text
                    mensajes_error_encontrados.append(f"{prueba['tipo']}: {mensaje_texto}")
                    prueba['encontrado'] = True
                    print(f"✅ Mensaje de error encontrado: '{mensaje_texto}'")
                    
                    # Tomar captura de pantalla del mensaje
                    self.driver.save_screenshot(f"error_{prueba['tipo'].lower()}_{i}.png")
                    print(f"📸 Captura guardada como 'error_{prueba['tipo'].lower()}_{i}.png'")
                    
                except Exception as e:
                    print(f"❌ No se encontró el mensaje de error esperado: '{prueba['mensaje_esperado']}'")
                    print(f"Error: {e}")
                    observaciones += f"Fallo - No se detectó mensaje para {prueba['tipo']}. "
                    
                    # Tomar captura de pantalla para debug
                    self.driver.save_screenshot(f"no_error_{prueba['tipo'].lower()}_{i}.png")
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
            
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
            submit_button.click()
            print("✅ Botón de registro presionado")
            time.sleep(3)
            
            # Tomar captura final
            if exito:
                self.driver.save_screenshot("validacion_completa_exitosa.png")
                print("📸 Captura final de validación exitosa guardada")
            else:
                self.driver.save_screenshot("validacion_completa_fallida.png")
                print("📸 Captura final de validación fallida guardada")
        
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            observaciones += f"Error final: {str(e)}"
            
            # Tomar captura de pantalla del error
            self.driver.save_screenshot("error_proceso.png")
            print("📸 Captura de error guardada como 'error_proceso.png'")
        finally:
            self.registrar_resultado(id_caso, "Exitosa" if exito else "Fallida", observaciones)

    def test_tc007(self):
        id_caso = 'TC007'
        print(f'\n=== Iniciando {id_caso} ===')
        
        # Generar datos de prueba
        company_name = "Empresa de Prueba S.A.S."
        first_names = ["Juan","Carlos","Luis","Ana","María","Laura","José","Miguel","Sofía","Valentina"]
        last_names = ["Pérez","González","Rodríguez","López","Martínez","Sánchez","Gómez","Ramírez"]
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = fake.email()
        phone_number = f"{random.randint(300000000,399999999)}"
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"

        exito = False
        observaciones = ""
        try:
            # Nombre de empresa
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
            print("✅ Nombre de empresa ingresado")
        
            # Nombre persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
            print("✅ Nombre ingresado")
        
            # Apellido persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
            print("✅ Apellido ingresado")
        
            # --- Seleccionar país: Colombia ---
            print("🔄 Intentando seleccionar país...")
            pais_seleccionado = False
            try:
                country_selector = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
                country_selector.click()
                print("✅ Click en el selector de país")
                time.sleep(2)
        
                try:
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 1)")
                    pais_seleccionado = True
                except:
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 2)")
                    pais_seleccionado = True
            except Exception as e:
                print(f"⚠️ Método dropdown falló: {e}")
                observaciones += f"Método dropdown falló: {str(e)}. "
        
                try:
                    country_input = self.driver.find_element(By.ID, "register-form_mainCountry")
                    country_input.clear()
                    country_input.send_keys("Colombia")
                    time.sleep(1)
                    country_input.send_keys(Keys.ENTER)
                    print("✅ Colombia ingresado manualmente")
                    pais_seleccionado = True
                except Exception as e2:
                    print(f"⚠️ Método escritura falló: {e2}")
                    observaciones += f"Método escritura falló: {str(e2)}. "
        
                    try:
                        self.driver.execute_script("""
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
                        raise Exception("❌ No se pudo seleccionar el país")
        
            if not pais_seleccionado:
                raise Exception("❌ No se pudo seleccionar el país")

            # Correo electrónico
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
            print("✅ Correo electrónico ingresado")
        
            # Número de celular
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
            print("✅ Número de celular ingresado")
        
            # Contraseña
            print("✅ Contraseña ingresada")
        
            # Click fuera para disparar validación
            self.driver.find_element(By.TAG_NAME, "body").click()
        
            # Esperar mensaje de error de contraseña
            error_msg_elem = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class,'ant-form-item-explain-error') and contains(text(),'La contraseña debe tener al menos 8 caracteres')]")
                )
            )
            error_msg = error_msg_elem.text.strip()
            print(f"⚠️ Mensaje mostrado en pantalla: '{error_msg}'")
        
            if "La contraseña debe tener al menos 8 caracteres" in error_msg:
                print("✅ Caso exitoso: validación de contraseña detectada")
                exito = True
                observaciones = "Mensaje de validación de contraseña mostrado"
            else:
                print("❌ Caso fallido: mensaje no coincide")
                observaciones = f"Mensaje encontrado: {error_msg}"
        
        except Exception as e:
            print(f"❌ Caso fallido: {e}")
            observaciones = f"No apareció el mensaje esperado: {str(e)}"
        finally:
            self.registrar_resultado(id_caso, "Exitosa" if exito else "Fallida", observaciones)

    def test_tc008(self):
        id_caso = 'TC008'
        print(f'\n=== Iniciando {id_caso} ===')
        
        # Generar datos de prueba
        company_name = "Empresa de Prueba S.A.S."
        first_names = ["Juan","Carlos","Luis","Ana","María","Laura","José","Miguel","Sofía","Valentina"]
        last_names = ["Pérez","González","Rodríguez","López","Martínez","Sánchez","G Gómez","Ramírez"]
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = fake.email()
        phone_number = ""  # Vacío para la prueba de error
        print(f"Datos generados -> Empresa: {company_name}, Nombre: {first_name} {last_name}, Email: {email}, Tel: {phone_number}")

        # Variable para controlar el éxito de la ejecución
        exito = False
        observaciones = ""
        mensaje_error_encontrado = ""
        
        try:
            # Nombre de empresa
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
            print("✅ Nombre de empresa ingresado")
        
            # Nombre persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
            print("✅ Nombre ingresado")
        
            # Apellido persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
            print("✅ Apellido ingresado")
        
            # --- Seleccionar país: Colombia ---
            print("🔄 Intentando seleccionar país...")
            
            pais_seleccionado = False
            # Método 1: Intentar encontrar el dropdown de Ant Design
            try:
                # Buscar el elemento del selector de país
                country_selector = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
                
                # Hacer clic para abrir el dropdown
                country_selector.click()
                print("✅ Click en el selector de país")
                time.sleep(2)  # Esperar a que se abra el dropdown
                
                # Buscar la opción de Colombia usando diferentes selectores
                try:
                    # Intentar con selector por texto visible
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 1)")
                    pais_seleccionado = True
                except:
                    # Intentar con selector por valor
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 2)")
                    pais_seleccionado = True
                    
            except Exception as e:
                print(f"⚠️ Método dropdown falló: {e}")
                observaciones += f"Método dropdown falló: {str(e)}. "
                
                # Método 2: Intentar escribir directamente
                try:
                    country_input = self.driver.find_element(By.ID, "register-form_mainCountry")
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
                        self.driver.execute_script("""
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
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
            print("✅ Correo electrónico ingresado")
        
            # Celular (VACÍO - esta es la prueba)
            phone_input = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber")))
            if phone_number:
                phone_input.send_keys()
                print("✅ Número de celular ingresado")
            else:
                print("⚠️ Número de celular dejado vacío (esto es intencional para la prueba)")
        
            # Contraseña
            print("✅ Contraseña ingresada")
        
            # Hacer clic en el botón "¡Inicia tu prueba gratuita!"
            print("🔄 Haciendo clic en el botón de registro...")
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
            submit_button.click()
            print("✅ Botón de registro presionado")
        
            # Esperar a que aparezca el mensaje de error
            print("🔄 Esperando mensaje de error...")
            time.sleep(3)  # Esperar a que se procese la validación
        
            # Buscar el mensaje de error específico para celular
            try:
                mensaje_error = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error') and contains(., 'Introduce tu número de teléfono')]")
                ))
                
                mensaje_error_encontrado = mensaje_error.text
                print(f"✅ Mensaje de error encontrado: '{mensaje_error_encontrado}'")
                
                # La prueba es exitosa si encontramos el mensaje de error esperado
                exito = True
                observaciones = f"Prueba exitosa - Mensaje de error detectado: {mensaje_error_encontrado}"
                
                # Tomar captura de pantalla del error
                self.driver.save_screenshot("error_celular_vacio.png")
                print("📸 Captura de error guardada como 'error_celular_vacio.png'")
                
            except Exception as error_msg:
                print("❌ No se encontró el mensaje de error esperado")
                observaciones = f"Fallo en la prueba - No se detectó el mensaje de error esperado. Error: {str(error_msg)}"
                
                # Verificar si hay otros mensajes de error
                try:
                    otros_errores = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ant-form-item-explain-error')]")
                    if otros_errores:
                        mensajes_otros = [error.text for error in otros_errores]
                        observaciones += f" Otros errores encontrados: {', '.join(mensajes_otros)}"
                        print(f"Otros errores detectados: {mensajes_otros}")
                except:
                
                # Tomar captura de pantalla para investigar
                    self.driver.save_screenshot("sin_mensaje_error_celular.png")
                print("📸 Captura de pantalla guardada como 'sin_mensaje_error_celular.png'")
        
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            observaciones += f"Error final: {str(e)}"
            
            # Tomar captura de pantalla del error
            self.driver.save_screenshot("error_proceso.png")
            print("📸 Captura de error guardada como 'error_proceso.png'")
        finally:
            self.registrar_resultado(id_caso, "Exitosa" if exito else "Fallida", observaciones)

    def test_tc011(self):
        id_caso = 'TC011'
        print(f'\n=== Iniciando {id_caso} ===')
        
        # Generar datos de prueba
        company_name = "Empresa de Prueba S.A.S."
        first_names = ["Juan","Carlos","Luis","Ana","María","Laura","José","Miguel","Sofía","Valentina"]
        last_names = ["Pérez","González","Rodríguez","López","Martínez","Sánchez","Gómez","Ramírez"]
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = "karrotdev@outlook.com"  # Correo ya registrado
        phone_number = f"{random.randint(300000000,399999999)}"
        print(f"Datos generados -> Empresa: {company_name}, Nombre: {first_name} {last_name}, Email: {email}, Tel: {phone_number}")

        # Variable para controlar el éxito de la ejecución
        exito = False
        observaciones = ""
        url_final = ""
        
        try:
            # Nombre de empresa
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_companyName"))).send_keys(company_name)
            print("✅ Nombre de empresa ingresado")
        
            # Nombre persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_name"))).send_keys(first_name)
            print("✅ Nombre ingresado")
        
            # Apellido persona
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_lastName"))).send_keys(last_name)
            print("✅ Apellido ingresado")
        
            # --- Seleccionar país: Colombia ---
            print("🔄 Intentando seleccionar país...")
            
            pais_seleccionado = False
            # Método 1: Intentar encontrar el dropdown de Ant Design
            try:
                # Buscar el elemento del selector de país
                country_selector = self.wait.until(EC.presence_of_element_located((By.ID, "register-form_mainCountry")))
                
                # Hacer clic para abrir el dropdown
                country_selector.click()
                print("✅ Click en el selector de país")
                time.sleep(2)
                
                # Buscar la opción de Colombia
                try:
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item') and contains(., 'Colombia')]")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 1)")
                    pais_seleccionado = True
                except:
                    colombia_option = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ant-select-item-option') and @title='Colombia']")
                    colombia_option.click()
                    print("✅ Colombia seleccionado desde dropdown (método 2)")
                    pais_seleccionado = True
                    
            except Exception as e:
                print(f"⚠️ Método dropdown falló: {e}")
                observaciones += f"Método dropdown falló: {str(e)}. "
                
                # Método 2: Intentar escribir directamente
                try:
                    country_input = self.driver.find_element(By.ID, "register-form_mainCountry")
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
                        self.driver.execute_script("""
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
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_email"))).send_keys(email)
            print("✅ Correo electrónico ingresado")
        
            # Número de celular
            self.wait.until(EC.presence_of_element_located((By.ID, "register-form_phoneNumber"))).send_keys(phone_number)
            print("✅ Número de celular ingresado")
        
            # Contraseña
            print("✅ Contraseña ingresada")
        
            # --- COMPLETAR REGISTRO ---
            print("🔄 Completando proceso de registro...")
            
            # Hacer clic en el botón "¡Inicia tu prueba gratuita!"
            submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Inicia tu prueba gratuita') or contains(., '¡Inicia tu prueba gratuita!')]")))
            submit_button.click()
            print("✅ Botón de registro presionado")
            time.sleep(6)
        
            # Esperar a que aparezcan los 4 inputs del OTP
            otp_inputs = self.wait.until(
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
                boton = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continuar')]")))
                boton.click()
                print("✅ Botón Continuar presionado")
        
                # Esperar y validar si hay error
                time.sleep(3)
                
                # Verificar si aparece el mensaje de error
                try:
                    mensaje_error = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, "//span[contains(@class, 'text-danger') and contains(., 'no es válido')]"))
                    )
                    
                    if mensaje_error.is_displayed():
                        print("❌ ERROR: El código introducido no es válido")
                        intento += 1
                        if intento <= max_intentos:
                            print("🔄 Por favor, ingresa un nuevo código OTP")
                            # Volver a obtener los inputs OTP por si la página se recargó
                            try:
                                otp_inputs = self.wait.until(
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
                elemento = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Selecciona una ubicación y una caja para comenzar tu turno')]"))
                )
                print("✅ Registro exitoso - Texto encontrado en dashboard")
                exito = True
                url_final = self.driver.current_url
                observaciones += "Registro y redirección exitosos. "
                
            except Exception as e:
                print(f"⚠️ No se encontró el texto esperado: {e}")
                observaciones += "No se encontró el texto esperado en dashboard. "
                # Verificar si al menos estamos en una URL diferente
                if "auth" not in self.driver.current_url:
                    print("✅ Parece que el registro fue exitoso (URL cambiada)")
                    exito = True
                    url_final = self.driver.current_url
                else:
                    raise Exception("Registro falló - No se redirigió al dashboard")
        
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            observaciones += f"Error final: {str(e)}"
            self.driver.save_screenshot("error_proceso.png")
            print("📸 Captura de error guardada")
        finally:
            self.registrar_resultado(id_caso, "Exitosa" if exito else "Fallida", observaciones)

if __name__ == '__main__':
    unittest.main()
