import glob
import re

def fix_tc027_028():
    for file in ['TC027 Registro de entrada de inventario Admin.py', 'TC028 Registro de salida de inventario Admin.py']:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        
        # 1. Fix 'Confirmar' button in TC027/028
        new_content = re.sub(
            r'//span\[normalize-space\(\)=\'Confirmar\'\] \| //button\[contains\(\., \'Confirmar\'\)\]',
            r"//div[contains(@class, 'ant-modal-footer')]//button[contains(@class, 'ant-btn-primary')] | //button[contains(@class, 'ant-btn-primary') and (contains(., 'Confirmar') or contains(., 'Guardar') or contains(., 'OK'))]",
            new_content
        )

        # 2. Add driver.refresh() before 'EXTRAYENDO VALORES FINALES'
        if 'driver.refresh()' not in new_content and 'EXTRAYENDO VALORES FINALES' in new_content:
            new_content = new_content.replace(
                'print("\\n📊 EXTRAYENDO VALORES FINALES:")',
                'driver.refresh()\n                    time.sleep(5)\n                    print("\\n📊 EXTRAYENDO VALORES FINALES:")'
            )

        if new_content != content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Updated {file}')

def fix_tc030():
    file = 'TC030 AJUSTE INVENTARIO MANUAL EN POS.py'
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    # Add driver.refresh() before 'EXTRAYENDO VALORES FINALES' in TC030
    if 'driver.refresh()' not in new_content and 'EXTRAYENDO VALORES FINALES' in new_content:
        new_content = new_content.replace(
            'print("\\n📊 EXTRAYENDO VALORES FINALES:")',
            'driver.refresh()\n                time.sleep(5)\n                print("\\n📊 EXTRAYENDO VALORES FINALES:")'
        )
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')

fix_tc027_028()
fix_tc030()
