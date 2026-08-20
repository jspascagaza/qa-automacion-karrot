import glob

code_to_replace = """            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rc_select_24"]')))"""

code_to_insert = """            # El ID rc_select_... es dinámico, usamos un selector más robusto basado en el rol combobox
            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@role='combobox'] | //input[starts-with(@id, 'rc_select_')][1]")))"""

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
