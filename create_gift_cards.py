import csv
import requests
import time

# Configuración de la API
URL = "https://ohzo2uiiie.execute-api.us-west-2.amazonaws.com/v1/gift-cards/create"
TOKEN = "eyJraWQiOiI1TUhVbUJ2Zjdxa0p4SjhhL3ROZEhickU0blhodEZxMlRJZ2hmSzgwN1AwPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJmMGMyMzg1MS01Y2M3LTRmMzItODJhOS0yODlkZTg2NWE1NTkiLCJjb2duaXRvOmdyb3VwcyI6WyI3Zjc3OWMyMi05ZTYxLTQ3N2YtYmFmMy1lOWM4ZjQ1ODUxY2IiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOi8vY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb20vdXMtd2VzdC0yXzRQUG93QmlyZyIsImN1c3RvbTpjb21wYW55SUQiOiI3Zjc3OWMyMi05ZTYxLTQ3N2YtYmFmMy1lOWM4ZjQ1ODUxY2IiLCJjb2duaXRvOnVzZXJuYW1lIjoiZjBjMjM4NTEtNWNjNy00ZjMyLTgyYTktMjg5ZGU4NjVhNTU5IiwiY3VzdG9tOmlzU3VwZXJBZG1pbiI6InRydWUiLCJjdXN0b206dXNlcklEIjoiNzFmNDM3NTYtNGY2NC00Zjg3LTg2NmUtY2Y5N2JjNmViZGZmIiwib3JpZ2luX2p0aSI6ImM0MDBkZDVkLWQ0MGMtNDdjNi04NWQwLWEzODdmZjg4MDA4ZiIsImF1ZCI6IjU0YTYwN2czYjRlMjFjbzBhdXNzcGI2b2kiLCJldmVudF9pZCI6IjZlN2JjMWJmLTJjNTctNGJiNi04YTJlLTc3MjI3ZWZmMmZiMiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzkxNDk0MDcyLCJleHAiOjE3OTE0OTc2NzIsImlhdCI6MTc5MTQ5NDA3MiwianRpIjoiMjU3OWZkMmEtNTI5NS00OWVhLTlkNmMtMmVhOWM4MjZjOWMxIiwiZW1haWwiOiJldmVudG9rYXJyb3RtdUBnbWFpbC5jb20ifQ.A0PRIAx3GMNMvfRgDF5MvgltrWwpMHtlSqPCBjYadwJvcG7tU9yT3d3s6XVcHzRg4dEL-wkjZKVtRc25O4avBSw8rKvtAhTrNCMew2_lAhuOvFUwWypYTdXWoZmFI0y_5oce_gbSCvEgvpPYVoFeMSuex6ZMW5qA5TYc4WdBFYFvPG9cEaTem-qA2U-RcuCgb8g7IL3qTn37sQenbRGJej4U4CfHevUprQ-O5MDOWQJAImAY5uU2dHc14-CpaxIJC5it8om4CrXqIB-nrK0IViWANSlVbDRjBMV_y-2oT2V1Zkb2KSkxgunQylO1gF_KQBzPd5Y2tzwYo31DyqrTyg"
CSV_FILE = "datos.csv"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def main():
    print(f"Abriendo archivo {CSV_FILE}...")
    
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        # Usamos DictReader para leer basado en las cabeceras del CSV
        reader = csv.DictReader(file)
        
        exitos = 0
        errores = 0
        
        for row in reader:
            pin = row.get("Código")
            if not pin:
                continue
            
            # Se prepara el payload usando el PIN de la fila actual
            payload = {
                "type": "PHYSICAL",
                "typeGiftCard": "GIFT_CARD",
                "balance": 10000,
                "pin": pin,
                "expiration": 365,
                "status": "ACTIVE",
                "locationID": "90371233-8fd0-45ab-aacb-2021149f7c9e",
                "paymentMethodID": "ad3ff496-d7ef-47b4-92b6-10402059b860",
                "paymentMoreInfo": {},
                "journal": {
                    "cashierID": "dfc415c4-37cb-422b-8aa5-2ea7f44a8c36",
                    "userID": "71f43756-4f64-4f87-866e-cf97bc6ebdff"
                }
            }
            
            try:
                print(f"Ejecutando API para el PIN: {pin} ...", end=" ")
                response = requests.post(URL, headers=HEADERS, json=payload)
                
                # Se verifica si la respuesta es exitosa
                if response.status_code in [200, 201]:
                    print("✅ Éxito")
                    exitos += 1
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    errores += 1
                    
            except Exception as e:
                print(f"⚠️ Excepción de conexión: {e}")
                errores += 1
            
            # Pequeña pausa para no saturar/bloquear el servidor destino
            time.sleep(0.1)

    print("\n--- RESUMEN ---")
    print(f"Total creados con éxito: {exitos}")
    print(f"Total con errores: {errores}")

if __name__ == "__main__":
    main()
