import os, glob

code_to_insert = '''
    # -----------------------------------------------------------------------------------
    # EXTRACCIÓN DE DATOS DEL PROVEEDOR Y NAVEGACIÓN A ÓRDENES DE COMPRA
    # -----------------------------------------------------------------------------------
    print("📦 Navegando a Proveedores para extraer datos...")
    proveedor_nombre = ""
    producto_nombre = ""
    
    try:
        # Click en el menú padre 'Proveedores'
        menu_proveedores = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Proveedores']"))
        )
        menu_proveedores.click()
        time.sleep(2)
        
        # 1. Ir a Lista de proveedores
        submenu_lista_proveedores = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Lista de proveedores'] | //a[normalize-space()='Lista de proveedores']"))
        )
        submenu_lista_proveedores.click()
        print("✅ Click en Lista de proveedores")
        time.sleep(5)
        
        # Extraer datos
        try:
            # Buscamos la primera fila de datos de la tabla de proveedores
            fila_proveedor = wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[contains(@class, 'ant-table-row')][1] | //table//tbody/tr[2]")))
            
            celdas = fila_proveedor.find_elements(By.TAG_NAME, "td")
            if len(celdas) >= 2:
                proveedor_nombre = celdas[1].text.strip() # El nombre suele estar en la segunda columna
            
            print(f"✅ Proveedor seleccionado: {proveedor_nombre}")
            
            # Click en Más información
            btn_mas_info = fila_proveedor.find_element(By.XPATH, ".//button[contains(., 'Más información')] | .//span[contains(., 'Más información')] | .//a[contains(., 'Más información')] | .//*[contains(text(), 'Más información')]")
            driver.execute_script("arguments[0].click();", btn_mas_info)
            time.sleep(5)
            
            # Ahora estamos en la pantalla de detalles.
            # Extraer productos. Buscamos en la tabla de Productos del proveedor o Materia prima
            # XPath: tablas que en su thead tienen la palabra PRODUCTO o MATERIA PRIMA
            xpath_filas = "//table[.//thead//th[contains(normalize-space(text()), 'PRODUCTO') or contains(normalize-space(text()), 'MATERIA PRIMA')]]/tbody/tr"
            filas_productos = driver.find_elements(By.XPATH, xpath_filas)
                
            productos_disponibles = []
            import random
            for fila in filas_productos:
                celdas_prod = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas_prod) > 0:
                    texto = celdas_prod[0].text.strip()
                    if texto and "No Data" not in texto and "Resultados" not in texto and "Result" not in texto:
                        # Extraer solo el texto que está dentro del div.ml-2 (el nombre real) para evadir el icono
                        try:
                            nombre_div = celdas_prod[0].find_element(By.XPATH, ".//div[contains(@class, 'ml-2')]")
                            texto_limpio = nombre_div.text.strip()
                        except:
                            # Fallback si no tiene div.ml-2
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
        print("📦 Navegando a Órdenes de Compra...")
        # Volver a desplegar Proveedores si se cerró por el cambio de ruta
        try:
            menu_proveedores = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Proveedores']"))
            )
            # Solo clickear si el submenu no está visible
            if len(driver.find_elements(By.XPATH, "//span[normalize-space()='Ordenes de Compra']")) == 0:
                menu_proveedores.click()
                time.sleep(1)
        except:
            pass
            
        submenu_ordenes = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Ordenes de Compra'] | //a[normalize-space()='Ordenes de Compra']"))
        )
        submenu_ordenes.click()
        print("✅ Click en Ordenes de Compra")
        time.sleep(5)
        
        # Click en el botón especificado
        print("⏳ Buscando botón de Crear/Agregar (especificado)...")
        boton_xpath = '//*[@id="root"]/div/section/section/section/div/main/div[5]/div/div[1]/div[2]/div/button[1]'
        boton = wait.until(EC.element_to_be_clickable((By.XPATH, boton_xpath)))
        boton.click()
        print("✅ Click en el botón especificado")
        time.sleep(3)
        
        # Llenar el input con el proveedor extraído
        if proveedor_nombre:
            print(f"⏳ Ingresando el proveedor '{proveedor_nombre}' en el selector...")
            input_proveedor = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rc_select_24"]')))
            
            # Scroll to element to avoid interception
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_proveedor)
            time.sleep(0.5)
            
            input_proveedor.click()
            time.sleep(1)
            
            # Limpiamos usando ctrl+a / backspace en vez de .clear() que a veces falla en selectores React
            input_proveedor.send_keys(webdriver.Keys.CONTROL + "a")
            input_proveedor.send_keys(webdriver.Keys.BACKSPACE)
            
            input_proveedor.send_keys(proveedor_nombre)
            time.sleep(2)
            
            # Seleccionar la opción del dropdown
            # Buscamos un elemento en el popup del dropdown que contenga el nombre
            xpath_opcion = f"//div[contains(@class, 'ant-select-item-option-content') and contains(text(), '{proveedor_nombre}')]"
            try:
                opcion = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opcion)))
                opcion.click()
                print("✅ Proveedor seleccionado en el dropdown")
            except:
                print("⚠️ No se pudo clickear la opción por texto, intentando seleccionar la primera opción activa...")
                input_proveedor.send_keys(webdriver.Keys.ENTER)
            time.sleep(2)
            
    except Exception as e:
        print(f"⚠️ Error en la navegación/extracción: {e}")
        raise e
'''

files = glob.glob('TC05*.py')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_token = '    # -----------------------------------------------------------------------------------\n    # EXTRACCIÓN DE DATOS DEL PROVEEDOR Y NAVEGACIÓN A ÓRDENES DE COMPRA\n    # -----------------------------------------------------------------------------------'
    end_token = '    except Exception as e:\n        print(f"⚠️ Error en la navegación/extracción: {e}")\n        raise e'
    
    if start_token in content and end_token in content:
        start_idx = content.find(start_token)
        end_idx = content.find(end_token) + len(end_token)
        
        new_content = content[:start_idx] + code_to_insert.strip() + content[end_idx:]
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
    else:
        print(f'Tokens not found in {file}')
