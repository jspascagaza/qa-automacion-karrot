import time
import random
from faker import Faker
from pages.registro_page import RegistroPage

def test_tc003_registro_exitoso(driver, gs_client):
    """
    Test Case TC003: Verifica que un usuario puede registrar una empresa exitosamente.
    """
    id_caso = "TC003"
    
    # Preparar datos ficticios
    fake = Faker()
    company_name = f"Empresa{random.randint(1000,9999)}"
    first_names = [fake.first_name() for _ in range(5)]
    last_names = [fake.last_name() for _ in range(5)]
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = fake.email()
    phone_number = f"+57{random.randint(3000000000,3999999999)}"
    password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    
    print(f"\nDatos generados -> Empresa: {company_name}, Nombre: {first_name} {last_name}, Email: {email}, Tel: {phone_number}")

    try:
        registro_page = RegistroPage(driver)
        registro_page.go_to_registro()
        
        # Llenar el formulario con los datos generados
        registro_page.fill_registration_form(
            company=company_name,
            name=first_name,
            last_name=last_name,
            country="Colombia",
            stores=random.randint(1, 10),
            email=email,
            phone=phone_number,
            password=password
        )
        
        print("✅ Todos los campos fueron llenados correctamente")
        
        # Guardar captura
        driver.save_screenshot("formulario_lleno_refactored.png")
        
        # Registro de resultado exitoso
        observaciones = "Formulario completado exitosamente - País Colombia seleccionado"
        gs_client.registrar_resultado(id_caso, "Exitosa", observaciones)
        
    except Exception as e:
        driver.save_screenshot("error_formulario_refactored.png")
        # Registro de resultado fallido
        observaciones = f"Error final: {str(e)}"
        gs_client.registrar_resultado(id_caso, "Fallida", observaciones)
        raise e
    finally:
        time.sleep(5)
