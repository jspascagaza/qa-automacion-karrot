import glob
import re
import os

files = glob.glob('TC*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content

    # Fix 'Agregar Artículo' for any wait type
    new_content = re.sub(
        r'([a-zA-Z0-9_]+\s*=\s*(?:WebDriverWait\(.*?\)|\bwait\b)\.until\(\s*EC\.element_to_be_clickable\(\(By\.XPATH,\s*)"//button\[contains\(text\(\),\s*\'Agregar Artículo\'\)\]"\)\)\s*\)',
        r'\1"//button[contains(@class, \'ant-btn-primary\') and (contains(., \'Agregar\') or contains(., \'Añadir\') or contains(., \'Nuevo\'))]")))',
        new_content,
        flags=re.DOTALL
    )

    # Fix 'Añadir' save button
    new_content = re.sub(
        r'//button\[@type=\'submit\' and contains\(@class,\s*\'ant-btn-primary\'\) and contains\(text\(\),\s*\'Añadir\'\)\]',
        r'//button[@type=\'submit\' and contains(@class, \'ant-btn-primary\')]',
        new_content,
        flags=re.DOTALL
    )

    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
