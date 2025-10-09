from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

driver = webdriver.Chrome()
driver.get("https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login")
driver.maximize_window()

wait = WebDriverWait(driver, 40)

# Login
# Esperar campo de correo
email_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_email")))
email_input.click()  # hacer clic en el campo
email_input.send_keys("js.pascagaza@karrotup.com")

# Esperar campo de contraseña
password_input = wait.until(EC.presence_of_element_located((By.ID, "login-form_password")))
password_input.click()
password_input.send_keys("P4sc4g4z42025#*")

# Click en el botón "Iniciar sesión"
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Iniciar sesión')]")))
login_button.click()
time.sleep(30)

# ==========================
# 3. Click en "Ir al panel de administración"
# ==========================
# Esperar hasta que el botón "Ir al panel de administración" sea clickeable
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

# ==========================
# Click en el módulo Ubicaciones
ModuloUbicaciones = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ubicaciones']"))
)
ModuloUbicaciones.click()
print("✅ Click en Ubicaciones")
time.sleep(3)

# ==========================
# DEFINICIÓN DE FUNCIONES PARA HACER CLICK EN SEGUNDA UBICACIÓN
# ==========================
def metodo_1_xpath_indice(driver):
    """Método 1: Usando find_elements y índice"""
    ubicaciones = driver.find_elements(By.XPATH, "//*[contains(text(), 'Ubicacion') or contains(text(), 'Ubicaciones')]")
    print(f"Método 1 encontró {len(ubicaciones)} elementos")
    if len(ubicaciones) > 1:
        ubicaciones[1].click()
        return True
    return False

def metodo_2_xpath_posicion(driver):
    """Método 2: XPath específico para la segunda ocurrencia"""
    segunda_ubicacion = driver.find_element(By.XPATH, "(//*[contains(text(), 'Ubicacion') or contains(text(), 'Ubicaciones')])[2]")
    segunda_ubicacion.click()
    return True

def metodo_3_css_selector(driver):
    """Método 3: CSS Selector (puede necesitar ajustes)"""
    try:
        selectores = [
            "div:contains('Ubicacion'):nth-of-type(2)",
            "span:contains('Ubicacion'):nth-of-type(2)",
            "a:contains('Ubicacion'):nth-of-type(2)",
            "*:contains('Ubicacion'):nth-of-type(2)"
        ]
        
        for selector in selectores:
            try:
                segunda_ubicacion = driver.find_element(By.CSS_SELECTOR, selector)
                segunda_ubicacion.click()
                return True
            except:
                continue
    except:
        pass
    return False

def metodo_4_clases(driver):
    """Método 4: Buscar por clases comunes"""
    clases_comunes = ['ubicacion', 'location', 'btn', 'button', 'link', 'menu-item', 'item']
    
    for clase in clases_comunes:
        try:
            elementos = driver.find_elements(By.CLASS_NAME, clase)
            print(f"Método 4 - Clase '{clase}': encontró {len(elementos)} elementos")
            if len(elementos) > 1:
                elementos[1].click()
                return True
        except:
            continue
    
    try:
        elementos = driver.find_elements(By.XPATH, "//*[contains(@class, 'ubicacion')]")
        print(f"Método 4 - Clase 'ubicacion': encontró {len(elementos)} elementos")
        if len(elementos) > 1:
            elementos[1].click()
            return True
    except:
        pass
    
    return False

def metodo_5_texto_exacto(driver):
    """Método 5: Texto exacto 'Ubicaciones'"""
    try:
        ubicaciones = driver.find_elements(By.XPATH, "//*[text()='Ubicaciones']")
        print(f"Método 5 - Texto 'Ubicaciones': encontró {len(ubicaciones)} elementos")
        if len(ubicaciones) > 1:
            ubicaciones[1].click()
            return True
    except:
        pass
    
    try:
        ubicaciones = driver.find_elements(By.XPATH, "//*[text()='Ubicacion']")
        print(f"Método 5 - Texto 'Ubicacion': encontró {len(ubicaciones)} elementos")
        if len(ubicaciones) > 1:
            ubicaciones[1].click()
            return True
    except:
        pass
    
    return False

def metodo_6_espera_explicita(driver):
    """Método 6: Con espera explícita"""
    try:
        wait = WebDriverWait(driver, 5)
        segunda_ubicacion = wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//*[contains(text(), 'Ubicacion') or contains(text(), 'Ubicaciones')])[2]"))
        )
        segunda_ubicacion.click()
        return True
    except TimeoutException:
        return False

def click_segunda_ubicacion(driver):
    """
    Intenta diferentes métodos para hacer click en la segunda ubicación
    """
    methods = [
        metodo_1_xpath_indice,
        metodo_2_xpath_posicion,
        metodo_3_css_selector,
        metodo_4_clases,
        metodo_5_texto_exacto,
        metodo_6_espera_explicita
    ]
    
    for i, metodo in enumerate(methods, 1):
        try:
            print(f"🔍 Probando método {i}...")
            if metodo(driver):
                print(f"✅ Éxito con método {i}")
                return True
            else:
                print(f"❌ Método {i} no encontró suficientes elementos")
        except Exception as e:
            print(f"❌ Método {i} falló: {str(e)}")
            continue
    
    print("❌ Todos los métodos fallaron")
    return False

# ==========================
# LLAMAR A LA FUNCIÓN PARA HACER CLICK EN SEGUNDA UBICACIÓN
# ==========================
print("🚀 Intentando hacer click en la segunda ubicación...")
time.sleep(2)

# Llamar a la función principal
success = click_segunda_ubicacion(driver)

if success:
    print("🎉 ¡Click en segunda ubicación exitoso!")
else:
    print("💥 No se pudo hacer click en la segunda ubicación")

# Esperar para ver el resultado
time.sleep(5)

# Cerrar el navegador
driver.quit()