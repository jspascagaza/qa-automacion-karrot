import os
import glob

path = r'c:\Users\yonas\Documents'
files = glob.glob(os.path.join(path, 'TC*.py'))

logger_code = """
# =====================
# CONFIGURACIÓN DE LOGS
# =====================
import sys
import os
from datetime import datetime

if not os.path.exists("logs"):
    os.makedirs("logs")

nombre_archivo = os.path.basename(__file__).replace(".py", "")
fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"logs/{nombre_archivo}_{fecha_hora}.log"

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(log_filename)
sys.stderr = sys.stdout
# =====================
"""

count = 0
for f in files:
    basename = os.path.basename(f)
    if not basename.startswith('TC'):
        continue

    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Prevenir inyección doble
    if "CONFIGURACIÓN DE LOGS" in content or "class Logger" in content:
        print(f"Skipping {basename} (already has logger)")
        continue

    # Insertar el logger después de load_dotenv() si existe, sino al principio de Google Sheets config
    if "load_dotenv()" in content:
        new_content = content.replace("load_dotenv()", f"load_dotenv()\n{logger_code}", 1)
    elif "# CONFIGURACIÓN GOOGLE SHEETS" in content:
        new_content = content.replace("# CONFIGURACIÓN GOOGLE SHEETS", f"{logger_code}\n# CONFIGURACIÓN GOOGLE SHEETS", 1)
    else:
        # Fallback: ponerlo al inicio
        new_content = f"{logger_code}\n{content}"
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        count += 1
        print(f'Injected logger in {basename}')

print(f'Total updated: {count}')
