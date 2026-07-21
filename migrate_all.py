import glob
import re
import os

def generate_header(class_name):
    return f"""import unittest
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

class {class_name}(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nombre_archivo = "{class_name.lower()}"
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"logs/{{nombre_archivo}}_{{fecha_hora}}.log"
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
            print(f"⚠️ Error al conectar con Google Sheets: {{e}}")
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
                print(f"⚠️ No se encontró el ID {{id_caso}}")
                return
            fila = celda.row
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            automatizado = "Sí"
            cls.sheet.update_cell(fila, 11, automatizado)
            cls.sheet.update_cell(fila, 13, fecha)
            cls.sheet.update_cell(fila, 14, estado)
            cls.sheet.update_cell(fila, 15, observaciones)
            print(f"✅ Caso {{id_caso}} actualizado -> {{estado}}")
        except Exception as e:
            print(f"❌ Error al actualizar el caso {{id_caso}}: {{str(e)}}")

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

"""

def extract_test_logic(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error opening {filepath}: {e}")
        return ""

    match = re.search(r'wait\s*=\s*WebDriverWait\([^\)]+\)', content)
    if not match:
        # Fallback to driver.get
        match = re.search(r'driver\.get\([^\)]+\)', content)
        if not match:
            print(f"Could not find start point in {filepath}")
            return ""
    
    id_caso_match = re.search(r'id_caso\s*=\s*[\'"](TC\d+)[\'"]', content)
    tc_id = id_caso_match.group(1) if id_caso_match else filepath.split(" ")[0].replace(".py", "")

    pre_driver_logic = ""
    start_pre = content.find("modo_automatico =")
    if start_pre == -1:
        start_pre = content.find("id_caso =")
        
    end_pre = content.find("chrome_options = Options()")
    if end_pre == -1: end_pre = content.find("driver = webdriver")
    
    if start_pre != -1 and end_pre != -1 and start_pre < end_pre:
        pre_driver_logic = content[start_pre:end_pre].strip()

    start_idx = match.end()
    end_idx = content.find("finally:")
    if end_idx == -1:
        # Fallback to driver.quit
        end_idx = content.find("driver.quit()")
        if end_idx == -1:
            end_idx = len(content)
        
    logic = content[start_idx:end_idx].strip()
    
    logic = logic.replace("driver.", "self.driver.")
    logic = logic.replace("wait.", "self.wait.")
    logic = logic.replace("registrar_resultado(", "self.registrar_resultado(")
    logic = re.sub(r'WebDriverWait\(driver,', r'WebDriverWait(self.driver,', logic)
    logic = logic.replace("(driver,", "(self.driver,")

    method_name = f"test_{tc_id.lower()}"
    
    indent = "    "
    method_body = f"{indent}def {method_name}(self):\n"
    method_body += f"{indent}    id_caso = '{tc_id}'\n"
    method_body += f"{indent}    print(f'\\n=== Iniciando {{id_caso}} ===')\n"
    
    if pre_driver_logic:
        for line in pre_driver_logic.split('\n'):
            if "id_caso =" not in line:
                method_body += f"{indent}    {line}\n"
            
    for line in logic.split('\n'):
        method_body += f"{indent}    {line}\n"
        
    method_body += "\n"
    return method_body

def migrate_suite(files, out_name, class_name):
    with open(out_name, "w", encoding="utf-8") as out:
        out.write(generate_header(class_name))
        for f in files:
            print(f"Procesando {f} para {out_name}...")
            logic = extract_test_logic(f)
            if logic:
                out.write(logic)
        out.write("if __name__ == '__main__':\n    unittest.main()\n")
    print(f"Migración completada. {out_name} generado.")

if __name__ == "__main__":
    sedes = [
        "TC012 Creación exitosa de sede con todos los datos.py",
        "TC013 Creación fallida sin nombre de ubicación.py",
        "TC014 Validación de dirección obligatoria.py",
        "TC015 Validación de ciudad obligatoria.py",
        "TC016 Creación de sede sin usuarios asignados.py",
        "TC017 Creación de caja una sede.py",
        "TC018 eliminacion de sede existente.py",
        "TC019 eliminacion de sede existente.py",
        "TC020 Registro de acciones en bitácora.py",
        "TC021 Creacion de actividad bitacora.py",
        "TC022 editar una bitacora.py"
    ]
    migrate_suite(sedes, "test_sedes_cajas.py", "TestSedesCajas")
    
    productos = [
        "TC023 Creación exitosa de producto con datos válidos.py",
        "TC024 Validación de campos obligatorios.py",
        "TC025 Edición de producto existente.py",
        "TC026 Eliminación de producto.py"
    ]
    migrate_suite(productos, "test_productos.py", "TestProductos")
    
    pos = [
        "TC027 Registro de entrada de inventario Admin.py",
        "TC028 Registro de salida de inventario Admin.py",
        "TC030 AJUSTE INVENTARIO MANUAL EN POS.py",
        "TC031 Realizar compra en POS.py"
    ]
    migrate_suite(pos, "test_inventario_pos.py", "TestInventarioPOS")
