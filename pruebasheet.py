import gspread
from google.oauth2.service_account import Credentials

# Autenticación con tu JSON
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(r"C:\Users\karrot\Documents\qa-automacion\automatizacion-karrot-a72723f4eafb.json", scopes=scopes)
client = gspread.authorize(creds)

# Abre el spreadsheet
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw/edit?usp=sharing")
sheet = spreadsheet.worksheet("Hoja 1")

# Solo columnas A:O (es decir, desde la A hasta la O)
data = sheet.get("A4:O1000")  # Ajusta 1000 al número máximo de filas que esperas

for row in data:
    print(row)
    # Asegúrate de que la fila tenga suficientes columnas
    if len(row) < 15:
        print("⚠️ Fila incompleta:", row)
        continue
    id_caso = row[0]  # Columna A
    estado = row[13]  # Columna N 