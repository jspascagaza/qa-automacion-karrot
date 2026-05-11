import pandas as pd
import os

def validar_detalle_articulos():
    # 1. Configuración de rutas
    ruta_descargas = r'C:\Users\yonas\Downloads'
    archivo_athena = os.path.join(ruta_descargas, 'reporte de ventas por articulo athena.xlsx')
    archivo_no_athena = os.path.join(ruta_descargas, 'reporte de ventas por articulo no athena.xlsx')
    archivo_resultado = os.path.join(ruta_descargas, 'CONTROL_DIFERENCIAS_POR_ARTICULO.xlsx')

    print("--- Cargando reportes de detalle por artículo ---")

    try:
        df_athena = pd.read_excel(archivo_athena)
        df_old = pd.read_excel(archivo_no_athena)
    except Exception as e:
        print(f"Error al abrir los archivos: {e}")
        return

    # 2. Limpieza y Normalización
    col_factura = '# Factura'
    for df in [df_athena, df_old]:
        df[col_factura] = df[col_factura].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        # Creamos un índice auxiliar por factura para comparar artículo 1 vs artículo 1, etc.
        df['item_rank'] = df.groupby(col_factura).cumcount() + 1

    # 3. Columnas a comparar (según tu lista)
    columnas_comparar = [
        'Nombre Producto', 'Cantidad', 'Venta Bruta', 'Descuento', 'Venta', 
        'Impuestos', 'Venta Neta', 'Costo Total', 'Utilidad', 'Margen %',
        'Nombre Almacén', 'Caja', 'Canal de Venta'
    ]

    # 4. Cruce de datos por Factura e Item
    # Usamos merge para alinear artículo por artículo dentro de cada factura
    comparativa = pd.merge(
        df_athena, df_old, 
        on=[col_factura, 'item_rank'], 
        suffixes=('_ATHENA', '_ANTIGUO'),
        how='outer'
    )

    diferencias = []

    print("Analizando diferencias...")

    for index, fila in comparativa.iterrows():
        factura = fila[col_factura]
        
        # Si la factura falta en un lado, lo saltamos para el reporte de diferencias de campos
        if pd.isna(fila['Venta_ATHENA']) or pd.isna(fila['Venta_ANTIGUO']):
            continue

        for col in columnas_comparar:
            col_a = f"{col}_ATHENA"
            col_o = f"{col}_ANTIGUO"
            
            if col_a in comparativa.columns and col_o in comparativa.columns:
                val_a = str(fila[col_a]).strip().replace('.0', '') if pd.notnull(fila[col_a]) else 'VACIO'
                val_o = str(fila[col_o]).strip().replace('.0', '') if pd.notnull(fila[col_o]) else 'VACIO'
                
                if val_a != val_o:
                    diferencias.append({
                        '# Factura': factura,
                        'Item #': fila['item_rank'],
                        'Campo': col,
                        'En_Athena': fila[col_a],
                        'En_Base_Antigua': fila[col_o]
                    })

    # 5. Guardar Reporte
    df_diffs = pd.DataFrame(diferencias)
    solo_athena = df_athena[~df_athena[col_factura].isin(df_old[col_factura])]
    solo_old = df_old[~df_old[col_factura].isin(df_athena[col_factura])]

    with pd.ExcelWriter(archivo_resultado) as writer:
        if not df_diffs.empty:
            df_diffs.to_excel(writer, sheet_name='DIFERENCIAS_ARTICULOS', index=False)
        else:
            pd.DataFrame(['Sin diferencias']).to_excel(writer, sheet_name='OK', index=False)
            
        solo_athena.to_excel(writer, sheet_name='FACTURAS_NUEVAS_ATHENA', index=False)
        solo_old.to_excel(writer, sheet_name='FACTURAS_FALTANTES', index=False)

    print("\n" + "="*40)
    print(f"PROCESO TERMINADO")
    print(f"Diferencias encontradas: {len(df_diffs)}")
    print(f"Reporte generado en: {archivo_resultado}")
    print("="*40)

if __name__ == "__main__":
    validar_detalle_articulos()