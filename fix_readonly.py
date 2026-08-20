import glob

code_to_replace = """            # Seleccionar estrictamente el input dentro del contenedor del label 'Proveedor'
            xpath_input = "//div[contains(@class, 'ant-form-item') and .//label[contains(text(), 'Proveedor')]]//input"
            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_input)))"""

code_to_insert = """            # Seleccionar estrictamente el input dentro del contenedor del label 'Proveedor'
            # (Excluyendo el input readonly oculto que genera Ant Design)
            xpath_input = "//div[contains(@class, 'ant-form-item') and .//label[contains(text(), 'Proveedor')]]//input[not(@readonly)]"
            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_input)))"""

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
