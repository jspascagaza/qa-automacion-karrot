import os
import time
import random
from faker import Faker
from pages.login_page import LoginPage
from pages.sedes_page import SedesPage

def test_tc012_crear_sede_exitosa(driver, gs_client):
    """
    Test Case TC012: Verifica que se pueda crear una sede exitosamente.
    Requiere inicio de sesión previo.
    """
    id_caso = "TC012"

    # Datos ficticios para la sede
    fake = Faker()
    nombre_sede = f"Sede {fake.city()} {random.randint(100, 999)}"
    direccion_sede = fake.address().replace('\n', ' ')
    print(f"\nDatos generados -> Nombre Sede: {nombre_sede}, Dirección: {direccion_sede}")

    exito = False
    observaciones = ""

    try:
        # Login
        login_page = LoginPage(driver)
        login_page.go_to_login()
        
        email = os.getenv("KARROT_LOGIN_EMAIL")
        password = os.getenv("KARROT_LOGIN_PASSWORD")
        login_page.login(email, password)
        login_page.verify_successful_login()
        
        # Crear Sede
        sedes_page = SedesPage(driver)
        sedes_page.navigate_to_add_location()
        
        # Llenar formulario
        sedes_page.fill_location_form(nombre_sede, direccion_sede)
        
        # Guardar
        sedes_page.submit_form()
        
        exito = True
        observaciones = "Sede creada exitosamente con todos los datos (Pytest)"
        
    except Exception as e:
        observaciones = f"Error en el proceso: {str(e)}"
        print(f"❌ {observaciones}")
        raise e
    finally:
        estado = "EXITOSO" if exito else "FALLIDO"
        gs_client.registrar_resultado(id_caso, estado, observaciones)
        time.sleep(3)
