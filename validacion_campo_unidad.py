from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

def encontrar_y_clickear_dropdown():
    try:
        print("🎯 Buscando dropdown de unidad...")
        
        # ESTRATEGIA 1: Buscar el input hidden primero
        try:
            input_hidden = WebDriverWait(WebDriverWait, 10).until(
                EC.presence_of_element_located((By.ID, "rc_select_2"))
            )
            print("✅ Input hidden encontrado")
        except:
            print("❌ Input hidden no encontrado, probando otras estrategias...")
            input_hidden = None

        # ESTRATEGIA 2: Buscar todos los posibles contenedores
        selectores = [
            # Por estructura Ant Design
            "//div[contains(@class, 'ant-select-selector')]",
            "//span[contains(@class, 'ant-select-selector')]",
            "//div[contains(@class, 'ant-select') and not(contains(@class, 'hidden'))]",
            "//span[contains(@class, 'ant-select')]",
            
            # Por contexto de búsqueda avanzada
            "//*[contains(text(), 'Unidad') or contains(text(), 'unidad')]/following::div[contains(@class, 'ant-select')][1]",
            "//label[contains(text(), 'Unidad')]/following::div[contains(@class, 'ant-select')][1]",
            
            # Por atributos ARIA
            "//*[@role='combobox']/ancestor::div[contains(@class, 'ant-select')]",
            "//*[contains(@aria-owns, 'rc_select_2_list')]/ancestor::div[contains(@class, 'ant-select')]",
            
            # Genéricos
            "//div[contains(@class, 'selection')]",
            "//span[contains(@class, 'selection')]",
        ]
        
        elemento_encontrado = None
        for selector in selectores:
            try:
                print(f"🔍 Probando selector: {selector}")
                elemento = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                # Verificar si es visible y tiene tamaño
                if elemento.is_displayed() and elemento.size['width'] > 0 and elemento.size['height'] > 0:
                    elemento_encontrado = elemento
                    print(f"✅ Elemento encontrado con: {selector}")
                    print(f"   Tag: {elemento.tag_name}, Clases: {elemento.get_attribute('class')}")
                    break
            except Exception as e:
                continue
        
        # ESTRATEGIA 3: Si no encontramos con selectores, usar JavaScript
        if not elemento_encontrado and input_hidden:
            print("🔧 Usando JavaScript para encontrar elemento...")
            elemento_encontrado = driver.execute_script("""
                var input = document.getElementById('rc_select_2');
                if (!input) return null;
                
                // Buscar el contenedor visible
                var container = input.closest('.ant-select-selector') || 
                               input.closest('.ant-select') ||
                               input.closest('[class*="select"]') ||
                               input.parentElement;
                
                // Si no encontramos, buscar cualquier elemento visible cerca
                if (!container || container.offsetWidth === 0) {
                    var xpath = "//div[contains(@class, 'ant-select')]";
                    var elements = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                    for (var i = 0; i < elements.snapshotLength; i++) {
                        var el = elements.snapshotItem(i);
                        if (el.offsetWidth > 100 && el.offsetHeight > 20) {
                            return el;
                        }
                    }
                }
                return container;
            """)
        
        # ESTRATEGIA 4: Hacer click
        if elemento_encontrado:
            print("🖱️ Intentando hacer click...")
            
            # Intentar diferentes métodos de click
            metodos_click = [
                lambda: elemento_encontrado.click(),
                lambda: driver.execute_script("arguments[0].click();", elemento_encontrado),
                lambda: ActionChains(driver).move_to_element(elemento_encontrado).click().perform(),
                lambda: driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", elemento_encontrado)
            ]
            
            for i, metodo in enumerate(metodos_click):
                try:
                    print(f"🔧 Método click {i+1}...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", elemento_encontrado)
                    time.sleep(1)
                    metodo()
                    print("✅ Click exitoso")
                    
                    # Verificar si se abrió el dropdown
                    time.sleep(2)
                    opciones = driver.find_elements(By.CSS_SELECTOR, ".ant-select-item-option-content, [role='option']")
                    if opciones:
                        print("📋 Dropdown abierto correctamente")
                        return True
                    break
                except Exception as e:
                    print(f"❌ Método {i+1} falló: {e}")
                    continue
        
        # ESTRATEGIA 5: Último recurso - click por coordenadas
        if input_hidden and not elemento_encontrado:
            print("🎯 Usando click por coordenadas...")
            location = input_hidden.location
            size = input_hidden.size
            
            # Hacer click cerca del elemento
            action = ActionChains(driver)
            action.move_by_offset(location['x'] + size['width']//2, location['y'] + size['height']//2).click().perform()
            print("✅ Click por coordenadas realizado")
            time.sleep(2)
            return True
            
        return False
        
    except Exception as e:
        print(f"💥 Error general: {e}")
        return False

def seleccionar_opcion_unidad():
    try:
        print("🎯 Buscando opciones del dropdown...")
        
        # Esperar opciones del dropdown
        opciones = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//div[contains(@class, 'ant-select-item-option-content')] | //div[role='option']"
            ))
        )
        
        print(f"📋 Encontradas {len(opciones)} opciones:")
        for i, opcion in enumerate(opciones):
            print(f"  {i+1}. {opcion.text}")
        
        # Buscar y seleccionar "Unidad (u)"
        for opcion in opciones:
            if "Unidad (u)" in opcion.text:
                print("✅ Seleccionando 'Unidad (u)'...")
                opcion.click()
                return True
        
        # Si no encuentra, seleccionar la primera
        if opciones:
            print(f"⚠️ Seleccionando primera opción: {opciones[0].text}")
            opciones[0].click()
            return True
            
        return False
        
    except Exception as e:
        print(f"💥 Error seleccionando opción: {e}")
        return False

# EJECUCIÓN PRINCIPAL
print("🚀 Iniciando selección de unidad...")

if encontrar_y_clickear_dropdown():
    time.sleep(2)
    if seleccionar_opcion_unidad():
        print("🎉 Proceso completado exitosamente!")
    else:
        print("❌ No se pudo seleccionar la opción")
else:
    print("❌ No se pudo abrir el dropdown")

print("📝 Finalizado")