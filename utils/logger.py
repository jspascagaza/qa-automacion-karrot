import sys
import os
from datetime import datetime

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        # Evitar errores de codificación en Windows terminal (cp1252) con emojis o caracteres especiales
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            self.terminal.write(message.encode('cp1252', 'ignore').decode('cp1252'))
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    @staticmethod
    def setup_logger(nombre_archivo):
        if not os.path.exists("logs"):
            os.makedirs("logs")
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"logs/{nombre_archivo}_{fecha_hora}.log"
        logger = Logger(log_filename)
        sys.stdout = logger
        sys.stderr = logger
        return logger
