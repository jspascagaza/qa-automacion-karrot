import os
import time
from pages.login_page import LoginPage

def test_tc001_login_exitoso(driver, gs_client):
    """
    Test Case TC001: Verifica que un usuario puede iniciar sesión exitosamente
    con credenciales válidas.
    """
    id_caso = "TC001"
    try:
        login_page = LoginPage(driver)
        login_page.go_to_login()
        
        email = os.getenv("KARROT_LOGIN_EMAIL")
        password = os.getenv("KARROT_LOGIN_PASSWORD")
        
        if not email or not password:
            raise ValueError("Las credenciales no están definidas en el archivo .env")

        login_page.login(email, password)
        
        # Mantener el sleep original de 10 segundos
        time.sleep(10)
        
        # Verificación (Assertion)
        login_page.verify_successful_login()
        
        # Registro de resultado exitoso
        gs_client.registrar_resultado(id_caso, "Exitosa", "Login realizado correctamente")
        
    except Exception as e:
        # Registro de resultado fallido
        gs_client.registrar_resultado(id_caso, "Fallida", f"Error: {str(e)}")
        raise e
