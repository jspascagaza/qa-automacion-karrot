import random
from datetime import datetime, timedelta
import pandas as pd

# Listas maestras basadas en la validación de la plantilla
FIRST_NAMES = ["Carlos", "Valentina", "Mateo", "Camila", "Santiago", "Sofia", "Alejandro", "Mariana", "Diego", "Lucia"]
LAST_NAMES = ["Gomez", "Rodriguez", "Perez", "Hernandez", "Martinez", "Lopez", "Garcia", "Torres", "Morales", "Ramirez"]
COMPANY_NAMES = ["Soluciones Andinas SAS", "Logística Express Ltda", "Innovación Tech SAS", "Distribuidora del Norte", "Grupo Comercial Central"]
DOMAINS = ["gmail.com", "outlook.com", "empresa.co", "correo.net"]

DANE_LOCATIONS = [
    ("11 - Bogotá", "11001 - Bogotá D.C."),
    ("05 - Antioquia", "05001 - Medellín"),
    ("76 - Valle del Cauca", "76001 - Cali"),
    ("08 - Atlántico", "08001 - Barranquilla"),
    ("68 - Santander", "68001 - Bucaramanga"),
    ("17 - Caldas", "17001 - Manizales"),
    ("25 - Cundinamarca", "25754 - Soacha"),
]

DOC_TYPES_NATURAL = ["Cédula de ciudadanía", "Tarjeta de extranjería", "Cédula de extranjería", "Pasaporte", "NUIP"]
DOC_TYPES_EMPRESA = ["NIT", "NIT de otro país"]
RESPONSABILIDADES = ["Gran contribuyente", "Autorretenedor", "Agente de retención IVA", "Régimen simple de tributación", "No responsable"]

COLUMNS = [
    "Tipo de Cliente",
    "Nombre*",
    "Email*",
    "Tipo de Documento",
    "Documento de Identidad",
    "Prefijo Teléfono",
    "Teléfono",
    "Regimen",
    "Responsabilidad",
    "Codigo Departamento Dane",
    "Codigo Municipio Dane",
    "custom_Fecha_ingreso",
    "custom_color_favorito",
    "custom_Tipo_cliente",
    "custom_aceptacion_terminos_y_condiciones",
    "custom_segmento_cliente",
    "custom_edad"
]

def generate_random_date(start_year=2021, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 10, 1)
    delta = end - start
    return (start + timedelta(days=random.randrange(delta.days))).strftime("%Y-%m-%d")

def generate_client_record(mode="clean"):
    client_type = random.choice(["Persona Natural", "Empresa"])
    
    if client_type == "Empresa":
        name = random.choice(COMPANY_NAMES)
        doc_type = random.choice(DOC_TYPES_EMPRESA)
        doc_id = str(random.randint(800000000, 999999999))
        regimen = "IVA Responsable"
        responsabilidad = random.choice(["Gran contribuyente", "Autorretenedor", "No responsable"])
    else:
        fn, ln = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        doc_type = random.choice(DOC_TYPES_NATURAL)
        doc_id = str(random.randint(10000000, 1099999999))
        regimen = random.choice(["IVA Responsable", "No IVA Responsable"])
        responsabilidad = "No responsable"

    clean_email_name = name.lower().replace(" ", ".").replace("ñ", "n")
    email = f"{clean_email_name}{random.randint(1, 99)}@{random.choice(DOMAINS)}"
    dept, mun = random.choice(DANE_LOCATIONS)
    phone = f"3{random.randint(100000000, 299999999)}"
    
    # 1. Campos base limpios (100% completos, válidos, sin blancos ni errores)
    record = {
        "Tipo de Cliente": client_type,
        "Nombre*": name,
        "Email*": email,
        "Tipo de Documento": doc_type,
        "Documento de Identidad": doc_id,
        "Prefijo Teléfono": "+57",
        "Teléfono": phone,
        "Regimen": regimen,
        "Responsabilidad": responsabilidad,
        "Codigo Departamento Dane": dept,
        "Codigo Municipio Dane": mun,
        "custom_Fecha_ingreso": generate_random_date(),
        "custom_color_favorito": random.choice(["Azul", "Negro", "Rojo", "Verde", "Blanco"]),
        "custom_Tipo_cliente": random.choice(["VIP", "Frecuente", "Ocasional", "Mayorista"]),
        "custom_aceptacion_terminos_y_condiciones": random.choice(["SI", "NO"]),
        "custom_segmento_cliente": random.choice(["Retail", "Corporativo", "B2B", "Ecommerce"]),
        "custom_edad": random.randint(18, 75)
    }

    # MODO 1: 'clean' -> Todos los datos completos, válidos, sin errores ni celdas vacías
    if mode == "clean":
        return record

    # MODO 2: 'blanks' -> Deja algunos campos en blanco (datos válidos pero con celdas vacías)
    if mode == "blanks":
        # Selecciona aleatoriamente entre 2 y 4 columnas para dejarlas en blanco
        num_blanks = random.randint(2, 4)
        cols_to_blank = random.sample(COLUMNS, k=num_blanks)
        for col in cols_to_blank:
            record[col] = ""
        return record

    # MODO 3: 'errors' -> Deja campos con errores de validación para pruebas negativas
    if mode == "errors":
        # Catálogo de mutaciones con error garantizado
        error_options = [
            ("Email*", lambda: random.choice(["correo_sin_arroba.com", "usuario@", "@dominio.co", "correo con espacios@test.com"])),
            ("Nombre*", lambda: random.choice(["", "123456789", "### Nombre Invalido ###"])),
            ("Documento de Identidad", lambda: random.choice(["ABC-XYZ", "-999999", "00000", "DOC_ERRONEO"])),
            ("Teléfono", lambda: random.choice(["123", "ABC1234567", "+57300", "00000"])),
            ("Codigo Departamento Dane", lambda: "99 - Departamento Inexistente"),
            ("Codigo Municipio Dane", lambda: "99999 - Municipio Inexistente"),
            ("custom_Fecha_ingreso", lambda: random.choice(["2026/02/30", "32-13-2025", "FECHA_INVALIDA"])),
            ("custom_edad", lambda: random.choice(["cien", -5, 999, "N/A"])),
            ("Tipo de Cliente", lambda: random.choice(["Persona Ficticia", "Gobierno", "12345"]))
        ]
        # Inyecta entre 1 y 3 errores por registro de forma garantizada
        num_errors = random.randint(1, 3)
        chosen_errors = random.sample(error_options, k=num_errors)
        for field, error_func in chosen_errors:
            record[field] = error_func()
        return record

    return record

def export_clients_file(output_filename="clientes_generados.xlsx", n_records=50, mode="clean"):
    """
    Genera el archivo en base a la plantilla.
    :param output_filename: Ruta del archivo (.xlsx o .csv).
    :param n_records: Cantidad de clientes a generar.
    :param mode: 'clean' (válidos), 'blanks' (celdas vacías), o 'errors' (datos corruptos).
    """
    data = [generate_client_record(mode=mode) for _ in range(n_records)]
    df = pd.DataFrame(data, columns=COLUMNS)
    
    try:
        if output_filename.endswith(".csv"):
            df.to_csv(output_filename, index=False, encoding="utf-8-sig")
        else:
            if not output_filename.endswith(".xlsx"):
                output_filename += ".xlsx"
            df.to_excel(output_filename, sheet_name="Plantilla Clientes", index=False)
            
        print(f"Archivo generado exitosamente: {output_filename}")
        print(f"Total registros: {n_records} | Modo: {mode}")
    except PermissionError:
        print(f"\n[ERROR DE PERMISO] No se pudo guardar '{output_filename}'.")
        print("Asegúrate de que el archivo no esté abierto en Excel u otro programa y vuelve a intentarlo.")
    except Exception as e:
        print(f"\n[ERROR INESPERADO]: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("        GENERADOR MASIVO DE CLIENTES")
    print("=" * 50)

    # 1. Cantidad de clientes a crear
    while True:
        entrada_cantidad = input("1. Ingrese la cantidad de clientes a crear (por defecto 15): ").strip()
        if not entrada_cantidad:
            REGISTROS = 15
            print(f"   -> Se usará el valor por defecto: {REGISTROS}")
            break
        try:
            REGISTROS = int(entrada_cantidad)
            if REGISTROS > 0:
                break
            print("   [!] Ingrese un número mayor a 0.")
        except ValueError:
            print("   [!] Debe ingresar un número entero válido.")

    # 2. Selección del Modo
    print("\n2. Seleccione el modo de generación:")
    print("   [1] clean  -> Sin errores y sin blancos (todos los campos completos y válidos)")
    print("   [2] blanks -> Con campos en blanco (datos válidos, con algunas celdas vacías)")
    print("   [3] errors -> Con campos con errores (datos con errores de formato/validación)")
    opcion_modo = input("   Elija una opción [1/2/3] (por defecto 1 - clean): ").strip().lower()
    mapa_modos = {
        "1": "clean", "clean": "clean",
        "2": "blanks", "blanks": "blanks",
        "3": "errors", "errors": "errors"
    }
    MODO = mapa_modos.get(opcion_modo, "clean")
    
    modos_info = {
        "clean": "Sin errores y sin celdas en blanco",
        "blanks": "Con algunos campos en blanco",
        "errors": "Con errores de validación intencionales"
    }
    print(f"   -> Modo seleccionado: {MODO.upper()} ({modos_info[MODO]})")

    # 3. Nombre del archivo de salida
    archivo_default = f"clientes_{MODO}.xlsx"
    archivo_input = input(f"\n3. Nombre del archivo (por defecto '{archivo_default}'): ").strip()
    ARCHIVO = archivo_input if archivo_input else archivo_default

    print("\n" + "=" * 50)
    print(f"Generando {REGISTROS} registros en modo '{MODO}' en el archivo '{ARCHIVO}'...")
    export_clients_file(
        output_filename=ARCHIVO,
        n_records=REGISTROS,
        mode=MODO
    )
    print("=" * 50)