import unittest
import time
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

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

class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nombre_archivo = "test_login"
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"logs/{nombre_archivo}_{fecha_hora}.log"
        cls.logger = Logger(log_filename)
        sys.stdout = cls.logger
        sys.stderr = cls.logger
        
        # =====================
        # CONFIGURACIÓN GOOGLE SHEETS
        # =====================
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
        # Restaurar stdout si es necesario
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    @classmethod
    def registrar_resultado(cls, id_caso, estado, observaciones=""):
        if not cls.sheet:
            print(f"⚠️ No se pudo registrar {id_caso} - Sheet no disponible")
            return
            
        try:
            celda = cls.sheet.find(id_caso)
            if not celda:
                print(f"⚠️ No se encontró el ID {id_caso}")
                return
            fila = celda.row
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            automatizado = "Sí"
            cls.sheet.update_cell(fila, 11, automatizado)   # Columna K
            cls.sheet.update_cell(fila, 13, fecha)          # Columna M
            cls.sheet.update_cell(fila, 14, estado)         # Columna N
            cls.sheet.update_cell(fila, 15, observaciones)  # Columna O
            print(f"✅ Caso {id_caso} actualizado -> {estado}")
        except Exception as e:
            print(f"❌ Error al actualizar el caso {id_caso}: {str(e)}")

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get("https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login")
        self.wait = WebDriverWait(self.driver, 40)

    def tearDown(self):
        self.driver.quit()

    def test_tc001_login_exitoso(self):
        print("\\n=== Iniciando TC001 ===")
        id_caso = "TC001"
        try:
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_val = os.getenv("WEB_EMAIL") or os.getenv("KARROT_LOGIN_EMAIL")
            email_input.send_keys(email_val)

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()

            time.sleep(10)
            
            # Wait for text after login (h1 dashboard/welcome)
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='root']/div/section/section/section/div/main/div[1]/div[1]/div[1]/h1")   
            ))

            self.registrar_resultado(id_caso, "Exitosa", "Login realizado correctamente")
        except Exception as e:
            self.registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")
            self.fail(f"TC001 failed: {str(e)}")

    def test_tc002_login_fallido(self):
        print("\\n=== Iniciando TC002 ===")
        id_caso = "TC002"
        email_user = os.getenv("KARROT_LOGIN_EMAIL")
        try:
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
            email_input.click()
            email_input.send_keys(email_user)

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
            login_button.click()

            # Verify error message
            try:
                alert_element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ant-alert-message"))
                )

                error_message = alert_element.text.strip()
                print(f"Mensaje encontrado en pantalla: '{error_message}'")

                if error_message:
                    print("✅ Caso exitoso: mensaje de error detectado")
                    self.registrar_resultado(id_caso, "Exitosa", f"Mensaje mostrado: {error_message}")
                else:
                    print("❌ Caso fallido: no se detectó texto en el mensaje")
                    self.registrar_resultado(id_caso, "Fallida", "El mensaje de error está vacío")
                    self.fail("Error message is empty")
            except Exception as inner_e:
                print("❌ Caso fallido: no apareció el mensaje en 20 segundos")
                self.registrar_resultado(id_caso, "Fallida", "No apareció el mensaje de error.")
                self.fail(f"No apareció el mensaje de error: {inner_e}")
        except Exception as e:
            self.registrar_resultado(id_caso, "Fallida", f"Error inesperado: {str(e)}")
            self.fail(f"TC002 failed unexpectedly: {str(e)}")

if __name__ == '__main__':
    unittest.main()
