import glob
import re

code_to_insert = """        print("o. Lugar de Entrega seleccionado correctamente.")
        time.sleep(1)
        
        # -----------------------------------------------------------
        # 4. BUSCAR Y AGREGAR EL PRODUCTO
        # -----------------------------------------------------------
        print(f"⏳ Buscando el producto '{producto_nombre}'...")
        
        # Encontrar el input de busqueda por su placeholder
        xpath_buscador = "//input[@placeholder='Busca por producto, SKU o cdigo de barras' or @placeholder='Busca por producto, SKU o código de barras']"
        input_buscador = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_buscador)))
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_buscador)
        time.sleep(0.5)
        
        input_buscador.click()
        time.sleep(0.5)
        input_buscador.send_keys(producto_nombre)
        time.sleep(3) # Esperar a que cargue la lista desplegable
        
        # Seleccionar el producto del listado desplegable
        # Buscamos la opcion exacta
        xpath_opcion_prod = f"//div[contains(@class, 'ant-select-item-option-content') and contains(text(), '{producto_nombre}')]"
        try:
            opcion_prod = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion_prod)))
            opcion_prod.click()
            print("o. Producto seleccionado de la lista desplegable.")
        except:
            print("s? No se encontro la opcion exacta por texto. Seleccionando la primera opcion con el teclado...")
            input_buscador.send_keys(webdriver.Keys.ARROW_DOWN)
            time.sleep(0.5)
            input_buscador.send_keys(webdriver.Keys.ENTER)
            print("o. Producto seleccionado con teclado.")
            
        time.sleep(2) # Esperar a que se agregue a la tabla
"""

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we already inserted it
    if "BUSCAR Y AGREGAR EL PRODUCTO" in content:
        print(f"Ya actualizado: {file}")
        continue
    
    # Replace the end of the location block with the new block
    pattern = r'print\("o\. Lugar de Entrega seleccionado correctamente\."\)\s+time\.sleep\(1\)'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, code_to_insert.replace('\\', '\\\\'), content, count=1)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
    else:
        print(f'Pattern not found in {file}')
