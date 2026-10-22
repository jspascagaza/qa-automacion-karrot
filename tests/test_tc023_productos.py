import os
import time
import random
import string
import pytest
from faker import Faker
from pages.login_page import LoginPage
from pages.inventario_page import InventarioPage

# Parámetros: (ID_CASO, TIPO_PRODUCTO, ES_PERECEDERO)
TEST_CONFIGS = [
    ("TC023-001", "Kit to stock", False),
    ("TC023-002", "Kit to order", False),
]

@pytest.mark.parametrize("id_caso, tipo_producto, es_perecedero", TEST_CONFIGS)
def test_tc023_crear_producto_sin_atributos(driver, gs_client, id_caso, tipo_producto, es_perecedero):
    """
    Test Case TC023: Verifica la creación de productos en el catálogo.
    Se parametriza para probar distintos tipos de producto (ej. Kit to stock, Kit to order).
    """
    fake = Faker('es_CO')
    
    # Generar datos del producto
    nombre_producto = f"Producto {fake.word().capitalize()} {random.randint(100, 9999)}"
    descripcion = fake.sentence(nb_words=10)
    precio = round(random.uniform(400_000, 2_000_000), 2)
    sku_aleatorio = f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    barcode_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    print(f"\nDatos -> Nombre: {nombre_producto}, Precio: {precio}, SKU: {sku_aleatorio}, Barcode: {barcode_aleatorio}")

    exito = False
    observaciones = ""

    try:
        # 1. Login
        login_page = LoginPage(driver)
        login_page.go_to_login()
        email = os.getenv("KARROT_LOGIN_EMAIL")
        password = os.getenv("KARROT_LOGIN_PASSWORD")
        login_page.login(email, password)
        login_page.verify_successful_login()

        # 2. Navegar a Crear Producto
        inv_page = InventarioPage(driver)
        inv_page.navigate_to_add_product()
        
        # 3. Llenar Formulario
        inv_page.select_product_type(tipo_producto)
        inv_page.fill_basic_info(nombre_producto, descripcion)
        inv_page.set_perecedero(es_perecedero)
        
        # 4. Llenar variantes básicas (Sin atributos dinámicos)
        inv_page.fill_single_variant(sku=sku_aleatorio, barcode=barcode_aleatorio, cost=precio, price=precio)
        
        # 5. Guardar
        inv_page.submit_product()
        
        # 6. Validar que aparece en la búsqueda
        inv_page.search_by_barcode(barcode_aleatorio)
        
        exito = True
        observaciones = f"Producto '{tipo_producto}' creado exitosamente (Pytest)"

    except Exception as e:
        observaciones = f"Error en la creación del producto: {str(e)}"
        print(f"❌ {observaciones}")
        raise e
    finally:
        estado = "EXITOSO" if exito else "FALLIDO"
        gs_client.registrar_resultado(id_caso, estado, observaciones)
        time.sleep(2)
