import re
import glob

code_to_insert = '''
            # Ahora estamos en la pantalla de detalles.
            # Extraer productos. Buscamos en las tablas que tengan PRODUCTO o MATERIA PRIMA
            xpath_filas = "//table[.//thead//th[contains(normalize-space(text()), 'PRODUCTO') or contains(normalize-space(text()), 'MATERIA PRIMA')]]/tbody/tr[contains(@class, 'ant-table-row')]"
            filas_productos = driver.find_elements(By.XPATH, xpath_filas)
                
            productos_disponibles = []
            import random
            for fila in filas_productos:
                celdas_prod = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas_prod) > 0:
                    texto = celdas_prod[0].text.strip()
                    if texto and "No Data" not in texto and "Resultados" not in texto and "Result" not in texto:
                        # Extraer solo el texto que está dentro del div para evadir iconos
                        try:
                            nombre_div = celdas_prod[0].find_element(By.XPATH, ".//div[contains(@class, 'ml-2')]")
                            texto_limpio = nombre_div.text.strip()
                        except:
                            texto_limpio = texto.split('\\n')[-1].strip()
                            
                        if texto_limpio and texto_limpio != "-":
                            productos_disponibles.append(texto_limpio)
            
            if productos_disponibles:
                producto_nombre = random.choice(productos_disponibles)
                print(f"✅ Producto aleatorio seleccionado: {producto_nombre}")
            else:
                print("⚠️ No se encontraron productos para este proveedor.")
                
        except Exception as ex:
            print(f"⚠️ Error al extraer datos del proveedor: {ex}")
        
        # 2. Ir a Órdenes de Compra
'''

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex to replace from `# Ahora estamos en la pantalla de detalles.` to `# 2. Ir a Órdenes de Compra`
    pattern = re.compile(r'# Ahora estamos en la pantalla de detalles\..*?# 2\. Ir a Órdenes de Compra', re.DOTALL)
    
    if pattern.search(content):
        new_content = pattern.sub(code_to_insert.strip(), content)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
    else:
        print(f'Tokens not found in {file}')
