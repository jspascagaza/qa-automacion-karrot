import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
# 1. Esperar y dar click en los 3 puntos del producto
menu_tres_puntos = wait.until(
EC.element_to_be_clickable((By.XPATH, "//table//button | //table//*[name()='svg' and @data-icon='ellipsis']"))
)
menu_tres_puntos.click()
print("✅ Click en los 3 puntos")
time.sleep(5)

# 2. Esperar a que aparezca la opción "Editar producto" y hacer click
editar_producto = wait.until(
EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Editar producto']"))
)
editar_producto.click()
print("✅ Click en Editar producto")
time.sleep(10)
# 3. Ir directamente al formulario de edición por URL
edit_url = f"https://app.karrotup.com/app/catalogue/edit-products/{product_id}"
driver.get(edit_url)
print(f"✏️ Editando producto {product_id}")

guardados = []
fallidos = []

guardar_selectores = [
    # 1. Por type y clase (el que ya usas)
    (By.XPATH, "//button[@type='submit' and contains(@class, 'ant-btn-primary')]"),

    # 2. Solo por texto visible
    (By.XPATH, "//button[contains(text(), 'Guardar')]"),

    # 3. Texto normalizado (ignora espacios)
    (By.XPATH, "//button[contains(normalize-space(.), 'Guardar')]"),

    # 4. Por type=submit solamente
    (By.XPATH, "//button[@type='submit']"),

    # 5. Por clase principal ant-btn-primary
    (By.CSS_SELECTOR, "button.ant-btn-primary"),

    # 6. Botón con span interno que tenga el texto Guardar
    (By.XPATH, "//button[.//span[contains(text(),'Guardar')]]"),

    # 7. Por ID (si el HTML lo define)
    (By.ID, "save-button"),

    # 8. Por role y texto (si usa ARIA roles)
    (By.XPATH, "//button[@role='button' and contains(., 'Guardar')]"),
]
save_button = None
for by, value in guardar_selectores:
    try:
        save_button = wait.until(EC.element_to_be_clickable((by, value)))
        # Resaltar el botón en pantalla antes de hacer click
        driver.execute_script("arguments[0].style.border='3px solid red'", save_button)
        time.sleep(2)
        save_button.click()
        print(f"💾 Producto {product_id} guardado con éxito usando selector: {by} = {value}")
        guardados.append(product_id)
        break
    except Exception as e:
        print(f"⚠️ No se encontró con {by} = {value}")
