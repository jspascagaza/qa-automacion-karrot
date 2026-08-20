import glob
import re

code_to_insert = """            input_proveedor.send_keys(proveedor_nombre)
            time.sleep(2)
            
        # -----------------------------------------------------------
        # 3. SELECCIONAR EL LUGAR DE ENTREGA
        # -----------------------------------------------------------
        print("⏳ Seleccionando el Lugar de Entrega...")
        
        # Buscar el input correcto basándonos en su Label
        xpath_ubicacion = "//div[contains(@class, 'ant-form-item') and .//label[contains(text(), 'Lugar de Entrega')]]//input[not(@readonly)]"
        input_ubicacion = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_ubicacion)))
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_ubicacion)
        time.sleep(0.5)
        
        # Forzar clic para abrir el menú
        driver.execute_script("arguments[0].click();", input_ubicacion)
        time.sleep(1)
        
        # Usar el teclado para seleccionar la primera opción (infalible en React)
        input_ubicacion.send_keys(webdriver.Keys.ARROW_DOWN)
        time.sleep(0.5)
        input_ubicacion.send_keys(webdriver.Keys.ENTER)
        
        print("✅ Lugar de Entrega seleccionado correctamente.")
        time.sleep(1)"""

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we already inserted it
    if "SELECCIONAR EL LUGAR DE ENTREGA" in content:
        print(f"Ya actualizado: {file}")
        continue
    
    # Replace the end of the provider block with the new block
    # We look for: input_proveedor.send_keys(proveedor_nombre) \n time.sleep(2)
    pattern = r'input_proveedor\.send_keys\(proveedor_nombre\)\s+time\.sleep\(2\)'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, code_to_insert.replace('\\', '\\\\'), content, count=1)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
    else:
        print(f'Pattern not found in {file}')
