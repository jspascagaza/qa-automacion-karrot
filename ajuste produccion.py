import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ==========================
# 1. Ruta al archivo CSV
# ==========================
csv_path = r"C:\Users\Karrot\Downloads\productID.csv"  # 👈 cambia TU_USUARIO

# ==========================
# 2. Leer columna productID
# ==========================
ids = []
with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)  # lee usando encabezados
    for row in reader:
        product_id = row["productID"].strip()
        if product_id:
            ids.append(product_id)

print("Se cargaron estos IDs:", ids)

# ==========================
# 2. Abrir navegador y login
# ==========================
driver = webdriver.Chrome()
driver.get("https://app.karrotup.com/auth/login")

wait = WebDriverWait(driver, 40)

# Login
# Esperar campo de correo
email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
email_input.click()  # hacer clic en el campo
email_input.send_keys("gregory.murillo@hotmail.com")

# Esperar campo de contraseña
password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
password_input.click()
password_input.send_keys("gm123456")

# Click en el botón "Iniciar sesión"
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")))
login_button.click()
time.sleep(30)

# ==========================
# 3. Click en "Ir al panel de administración"
# ==========================
# Esperar hasta que el botón "Ir al panel de administración" sea clickeable
# Esperar hasta que aparezca y hacer click en "Ir al panel de administración"
panel_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
)
panel_button.click()

# Esperar a que cargue el Panel de control
wait.until(
    EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]"))
)
print("✅ Panel de control cargado correctamente")
time.sleep(5)
# Esperar a que aparezca el menú Catálogo
catalogo = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Catálogo']"))
)
catalogo.click()
print("✅ Click en Catálogo")
time.sleep(15)

productos_servicios = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Productos y Servicios']"))
)
productos_servicios.click()
print("✅ Click en Productos y Servicios")
time.sleep(15)

## ==========================
## 4. Recorrer IDs y editar
## ==========================
#
guardados = []
fallidos = []

def manejar_confirmacion_precios():
    """
    Maneja la confirmación de actualización de precios/costos
    Retorna True si se manejó la confirmación, False si no apareció
    """
    try:
        # Buscar el mensaje de confirmación con un timeout corto
        confirmacion_wait = WebDriverWait(driver, 5)
        
        # Buscar el mensaje "Actualización de precios/costos"
        mensaje_confirmacion = confirmacion_wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//strong[contains(text(), 'Actualización de precios/costos')]")
            )
        )
        
        if mensaje_confirmacion:
            print("⚠️ Apareció mensaje de confirmación de precios")
            
            # Buscar y hacer click en el botón "Sí"
            boton_si = confirmacion_wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'ant-btn-primary') and contains(@class, 'ant-btn-sm')]//span[text()='Sí']")
                )
            )
            boton_si.click()
            print("✅ Click en botón 'Sí' para confirmar actualización de precios")
            time.sleep(2)
            return True
            
    except TimeoutException:
        # No apareció el mensaje de confirmación, continuar normalmente
        print("ℹ️ No apareció mensaje de confirmación de precios")
        return False
    except Exception as e:
        print(f"⚠️ Error al manejar confirmación de precios: {e}")
        return False

for product_id in ids:
    try:
        # ======================
        # 1. Abrir menú del producto
        # ======================
        menu_tres_puntos = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//table//button | //table//*[name()='svg' and @data-icon='ellipsis']")
            )
        )
        menu_tres_puntos.click()
        print("✅ Click en los 3 puntos")
        time.sleep(5)

        # ======================
        # 2. Click en "Editar producto"
        # ======================
        editar_producto = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Editar producto']"))
        )
        editar_producto.click()
        print("✅ Click en Editar producto")
        time.sleep(10)

        # ======================
        # 3. Ir directamente al formulario de edición
        # ======================
        edit_url = f"https://app.karrotup.com/app/catalogue/edit-products/{product_id}"
        driver.get(edit_url)
        print(f"✏️ Editando producto {product_id}")
        time.sleep(3)

        # ======================
        # 4. Intentar guardar cambios con diferentes selectores
        # ======================
        guardar_selectores = [
            (By.XPATH, "//button[@type='submit' and contains(@class, 'ant-btn-primary')]"),  # con clase
            (By.XPATH, "//button[@type='submit' and text()='Guardar']"),                     # texto exacto
            (By.XPATH, "//button[contains(text(),'Guardar')]"),                              # texto parcial
            (By.CSS_SELECTOR, "button.ant-btn.ant-btn-primary"),                             # CSS
        #    (By.ID, "save-button"),                                                          # ID
        #    (By.XPATH, "//button[@role='button' and contains(., 'Guardar')]"),               # ARIA role
        ]

        save_button = None
        guardado_exitoso = False
        
        for by, value in guardar_selectores:
            try:
                save_button = wait.until(EC.element_to_be_clickable((by, value)))
                driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", save_button)  # click con JS
                print(f"✅ Click en botón Guardar para producto {product_id}")
                
                # ======================
                # 5. DESPUÉS del click en Guardar: Manejar confirmación de precios
                # ======================
                time.sleep(2)  # Esperar un momento para que aparezca el modal si va a aparecer
                manejar_confirmacion_precios()
                
                guardado_exitoso = True
                guardados.append(product_id)
                break  # Si llegamos aquí, el guardado fue exitoso
                
            except Exception as e:
                print(f"⚠️ No se pudo hacer click con selector {by}={value}: {e}")
                continue
        
        if not guardado_exitoso:
            fallidos.append(product_id)
            print(f"❌ No se pudo guardar el producto {product_id}")
            
        # Pequeña pausa entre productos
        time.sleep(2)
        
    except Exception as e: 
        print(f"❌ Error al procesar el producto {product_id}: {e}") 
        fallidos.append(product_id) 

# --- Reporte final ---
print("\n📊 Proceso finalizado")
print(f"✅ Guardados: {guardados}")
print(f"❌ Fallidos: {fallidos}")

## ==========================
## 5. Cerrar navegador
## ==========================
driver.quit()