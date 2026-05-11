import pandas as pd
import os

def validar_ventas_vendedor():
    # 1. Configuración de rutas
    ruta_descargas = r'C:\Users\yonas\Downloads'
    archivo_athena = os.path.join(ruta_descargas, 'reporte de ventas por vendedor athena.xlsx')
    archivo_no_athena = os.path.join(ruta_descargas, 'reporte de ventas por vendedor no athena.xlsx')
    archivo_control = os.path.join(ruta_descargas, 'CONTROL_DIFERENCIAS_VENDEDORES.xlsx')

    print("--- Iniciando validación de Ventas por Vendedor ---")

    try:
        # Se asume que la información está en la primera pestaña
        df_athena = pd.read_excel(archivo_athena)
        df_old = pd.read_excel(archivo_no_athena)
    except Exception as e:
        print(f"Error al cargar archivos Excel: {e}")
        return

    # 2. Normalización de la llave principal (# Doc)
    col_llave = '# Doc'
    for df in [df_athena, df_old]:
        # Asegurar que el ID sea texto limpio
        df[col_llave] = df[col_llave].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

    # 3. Columnas a validar
    # Basado en tu lista de columnas proporcionada
    columnas_validar = [
        'Seller Name', 'Seller Code', 'Unidades', 'Venta Bruta', 'Descuento', 
        'Venta', 'Propina', 'Venta con Propina', 'Impuestos', 'Venta Neta', 
        'Costo', 'Margen %', 'Utilidad', 'Nombre Almacén'
    ]

    # 4. Cruce de datos (Inner Join por documento)
    comunes = pd.merge(
        df_athena, df_old, 
        on=col_llave, 
        suffixes=('_ATHENA', '_ANTIGUO')
    )

    diferencias = []

    print(f"Comparando datos de {len(comunes)} documentos comunes...")

    for index, fila in comunes.iterrows():
        doc_id = fila[col_llave]
        
        for col in columnas_validar:
            col_a = f"{col}_ATHENA"
            col_o = f"{col}_ANTIGUO"
            
            if col_a in comunes.columns and col_o in comunes.columns:
                # Normalización para evitar falsos positivos por formato numérico o nulos
                val_a = str(fila[col_a]).strip().replace('.0', '') if pd.notnull(fila[col_a]) else 'VACIO'
                val_o = str(fila[col_o]).strip().replace('.0', '') if pd.notnull(fila[col_o]) else 'VACIO'
                
                if val_a != val_o:
                    diferencias.append({
                        '# Documento': doc_id,
                        'Campo_Diferente': col,
                        'Valor_en_Athena': fila[col_a],
                        'Valor_en_Base_Antigua': fila[col_o]
                    })

    # 5. Generación del reporte de control
    df_resultado = pd.DataFrame(diferencias)
    
    # Identificar registros que están en un lado pero no en otro
    ids_athena = set(df_athena[col_llave])
    ids_old = set(df_old[col_llave])
    
    solo_en_athena = df_athena[~df_athena[col_llave].isin(ids_old)]
    solo_en_no_athena = df_old[~df_old[col_llave].isin(ids_athena)]

    with pd.ExcelWriter(archivo_control) as writer:
        if not df_resultado.empty:
            df_resultado.to_excel(writer, sheet_name='DIFERENCIAS_POR_VENDEDOR', index=False)
        else:
            pd.DataFrame(['Sin diferencias detectadas']).to_excel(writer, sheet_name='SIN_DIFERENCIAS', index=False)
            
        solo_en_athena.to_excel(writer, sheet_name='DOCS_SOLO_EN_ATHENA', index=False)
        solo_en_no_athena.to_excel(writer, sheet_name='DOCS_FALTANTES_EN_ATHENA', index=False)

    print("\n" + "="*45)
    print("REPORTE DE VENDEDORES COMPLETADO")
    print(f"Diferencias encontradas: {len(df_resultado)}")
    print(f"Documentos nuevos en Athena: {len(solo_en_athena)}")
    print(f"Documentos que no migraron: {len(solo_en_no_athena)}")
    print(f"Archivo guardado en: {archivo_control}")
    print("="*45)

if __name__ == "__main__":
    validar_ventas_vendedor()