import os, glob

code_to_insert = '''
    # -----------------------------------------------------------------------------------
    # NAVEGACIÓN A ÓRDENES DE COMPRA
    # -----------------------------------------------------------------------------------
    print("📦 Navegando a Proveedores -> Órdenes de Compra...")
    try:
        # Click en el menú padre 'Proveedores'
        menu_proveedores = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Proveedores']"))
        )
        menu_proveedores.click()
        print("✅ Click en Proveedores")
        time.sleep(2)
        
        # Click en 'Ordenes de Compra'
        submenu_ordenes = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ordenes de Compra']"))
        )
        submenu_ordenes.click()
        print("✅ Click en Ordenes de Compra")
        time.sleep(5)
        
        # Click en el botón especificado
        print("⏳ Buscando botón específico...")
        boton_xpath = '//*[@id="root"]/div/section/section/section/div/main/div[5]/div/div[1]/div[2]/div/button[1]'
        boton = wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath)))
        boton.click()
        print("✅ Click en el botón especificado")
        time.sleep(3)
        
    except Exception as e:
        print(f"⚠️ Error en la navegación: {e}")
        raise e
'''

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    target = '    # -----------------------------------------------------------------------------------\n    # A PARTIR DE AQUÍ CONTINUARÁ EL PROCESO ESPECÍFICO DEL CASO DE PRUEBA\n    # -----------------------------------------------------------------------------------'
    if target in content:
        content = content.replace(target, code_to_insert)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {file}')
    else:
        print(f'Target not found in {file}')
