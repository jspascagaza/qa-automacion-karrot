import glob
import re
import os

files = glob.glob('TC*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content

    # Fix ModuloUbicaciones
    new_content = re.sub(
        r'ModuloUbicaciones\s*=\s*wait\.until\(\s*EC\.element_to_be_clickable\(\(By\.XPATH,\s*".*?li\[12\].*?"\)\)\s*\)',
        '''ModuloUbicaciones = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")))''',
        new_content,
        flags=re.DOTALL
    )

    # Fix 'Agregar Artículo'
    new_content = re.sub(
        r'boton_agregar\s*=\s*WebDriverWait\(driver, 10\)\.until\(\s*EC\.element_to_be_clickable\(\(By\.XPATH,\s*"//button\[contains\(text\(\),\s*\'Agregar Artículo\'\)\]"\)\)\s*\)',
        '''boton_agregar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-btn-primary') and (contains(., 'Agregar') or contains(., 'Añadir') or contains(., 'Nuevo'))]")))''',
        new_content,
        flags=re.DOTALL
    )
    
    # Fix 'Confirmar' button in TC027/028 (if any absolute xpath is brittle)
    # wait I will check TC027 first.

    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
