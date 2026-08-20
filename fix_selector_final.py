import glob

code_to_replace = """            # El ID rc_select_... es dinámico, usamos un selector más robusto basado en el rol combobox
            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@role='combobox'] | //input[starts-with(@id, 'rc_select_')][1]")))
            
            # Scroll to element to avoid interception
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_proveedor)
            time.sleep(0.5)
            
            input_proveedor.click()
            time.sleep(1)"""

code_to_insert = """            # Seleccionar estrictamente el input dentro del contenedor del label 'Proveedor'
            xpath_input = "//div[contains(@class, 'ant-form-item') and .//label[contains(text(), 'Proveedor')]]//input"
            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_input)))
            
            # Scroll to element to avoid interception
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_proveedor)
            time.sleep(0.5)
            
            # Forzamos el click con Javascript por si está interceptado
            driver.execute_script("arguments[0].click();", input_proveedor)
            time.sleep(1)"""

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if code_to_replace in content:
        new_content = content.replace(code_to_replace, code_to_insert)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed selector in {file}')
    else:
        print(f'Not found in {file}')
