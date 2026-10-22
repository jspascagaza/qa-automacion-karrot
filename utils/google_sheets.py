import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GoogleSheetsClient:
    def __init__(self):
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        
        # We assume the credential file is in the root directory
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "automatizacion-karrot-456d1a1552ca.json")
        try:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            self.client = gspread.authorize(self.creds)
            self.spreadsheet = self.client.open_by_url(
                "https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit#gid=0"
            )
            self.sheet = self.spreadsheet.sheet1
        except Exception as e:
            print(f"Error al conectar con Google Sheets: {e}")
            self.sheet = None

    def registrar_resultado(self, id_caso, estado, observaciones=""):
        if not self.sheet:
            print("No hay conexion a la hoja de calculo.")
            return
        
        try:
            celda = self.sheet.find(id_caso)
            if not celda:
                print(f"No se encontro el ID {id_caso}")
                return
            fila = celda.row
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            automatizado = "Sí"
            self.sheet.update_cell(fila, 11, automatizado)   # Columna K
            self.sheet.update_cell(fila, 13, fecha)          # Columna M
            self.sheet.update_cell(fila, 14, estado)         # Columna N
            self.sheet.update_cell(fila, 15, observaciones)  # Columna O
            print(f"Caso {id_caso} actualizado -> {estado}")
        except Exception as e:
            print(f"Error al actualizar el caso {id_caso}: {str(e)}")
