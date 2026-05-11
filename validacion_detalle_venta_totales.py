import pandas as pd
import os

def ejecutar_comparacion():
    # 1. Configuración de rutas y nombres
    ruta_base = r'C:\Users\yonas\Downloads'
    archivo_athena = os.path.join(ruta_base, 'reporte ventas de total athena.xlsx')
    archivo_no_athena = os.path.join(ruta_base, 'reporte ventas de total no athena.xlsx')
    archivo_reporte = os.path.join(ruta_base, 'CONTROL_DIFERENCIAS_VENTAS.xlsx')

    print("--- Iniciando proceso de validación ---")

    # 2. Carga de datos
    try:
        # Cargamos la primera hoja por defecto
        df_athena = pd.read_excel(archivo_athena)
        df_old = pd.read_excel(archivo_no_athena)
    except Exception as e:
        print(f"Error al cargar los archivos: {e}")
        return

    # 3. Preparación y Limpieza
    col_llave = '# Factura'
    
    for df in [df_athena, df_old]:
        # Convertir factura a texto limpio para evitar errores de comparación
        df[col_llave] = df[col_llave].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        # Limpiar espacios en los nombres de las columnas
        df.columns = df.columns.str.strip()

    # 4. Cruce de Datos (Inner Join)
    # Buscamos las facturas que están en AMBOS archivos para comparar sus campos
    comunes = pd.merge(df_athena, df_old, on=col_llave, suffixes=('_ATHENA', '_ANTIGUO'))
    
    ids_athena = set(df_athena[col_llave])
    ids_old = set(df_old[col_llave])
    
    # 5. Lógica de Comparación de Campos
    diferencias_detalle = []
    
    # Lista de columnas a validar (basada en tu lista)
    columnas_validar = [
        'Nombre Almacén', 'Caja', 'Canal de Venta', 'Método de Pago Principal', 
        'Nombre Usuario', 'Nombre Vendedor', 'Fecha', 'Hora', 'Nombre Cliente', 
        'Documento Cliente', 'Unidades', 'Venta Bruta', 'Descuento', 'Venta', 
        'Impuestos', 'Venta Neta', 'Costo', 'Utilidad'
    ]

    print(f"Comparando {len(comunes)} facturas comunes...")

    for index, fila in comunes.iterrows():
        factura_id = fila[col_llave]
        
        for col in columnas_validar:
            col_a = f"{col}_ATHENA"
            col_o = f"{col}_ANTIGUO"
            
            if col_a in comunes.columns and col_o in comunes.columns:
                # Normalizar valores para la comparación (evitar fallos por decimales o nulos)
                val_a = str(fila[col_a]).strip().replace('.0', '') if pd.notnull(fila[col_a]) else 'VACIO'
                val_o = str(fila[col_o]).strip().replace('.0', '') if pd.notnull(fila[col_o]) else 'VACIO'
                
                if val_a != val_o:
                    diferencias_detalle.append({
                        '# Factura': factura_id,
                        'Campo_con_Diferencia': col,
                        'Valor_en_Athena': fila[col_a],
                        'Valor_en_Base_Antigua': fila[col_o],
                        'Estado': 'DIFERENTE'
                    })

    # 6. Generación del archivo de Control (Excel)
    df_resultado = pd.DataFrame(diferencias_detalle)
    
    # Identificar facturas que faltan en un lado u otro
    solo_en_athena = df_athena[~df_athena[col_llave].isin(ids_old)]
    solo_en_no_athena = df_old[~df_old[col_llave].isin(ids_athena)]

    with pd.ExcelWriter(archivo_reporte) as writer:
        if not df_resultado.empty:
            df_resultado.to_excel(writer, sheet_name='DIFERENCIAS_ENCONTRADAS', index=False)
        else:
            # Crear hoja vacía si no hay diferencias
            pd.DataFrame(['Sin diferencias encontradas']).to_excel(writer, sheet_name='SIN_DIFERENCIAS', index=False)
            
        solo_en_athena.to_excel(writer, sheet_name='SOLO_EN_ATHENA', index=False)
        solo_en_no_athena.to_excel(writer, sheet_name='FALTAN_EN_ATHENA', index=False)

    print("\n" + "="*40)
    print("REPORTE FINALIZADO")
    print(f"Diferencias de datos detectadas: {len(df_resultado)}")
    print(f"Facturas nuevas en Athena: {len(solo_en_athena)}")
    print(f"Facturas que no migraron: {len(solo_en_no_athena)}")
    print(f"Archivo guardado en: {archivo_reporte}")
    print("="*40)

if __name__ == "__main__":
    ejecutar_comparacion()