import pandas as pd
import os

def validar_ventas_canal():
    # 1. Configuración de rutas de archivos
    ruta_descargas = r'C:\Users\yonas\Downloads'
    archivo_athena = os.path.join(ruta_descargas, 'reporte de ventas por canal athena.xlsx')
    archivo_no_athena = os.path.join(ruta_descargas, 'reporte de ventas por canal no athena.xlsx')
    archivo_control = os.path.join(ruta_descargas, 'CONTROL_DIFERENCIAS_CANALES.xlsx')

    print("--- Iniciando validación de Ventas por Canal ---")

    try:
        df_athena = pd.read_excel(archivo_athena)
        df_old = pd.read_excel(archivo_no_athena)
    except Exception as e:
        print(f"Error al abrir los archivos: {e}")
        return

    # 2. Normalización de la llave principal (Canal de Venta)
    col_llave = 'Canal de Venta'
    for df in [df_athena, df_old]:
        df[col_llave] = df[col_llave].astype(str).str.strip().str.upper()
        # Limpiar nombres de columnas para evitar espacios invisibles
        df.columns = df.columns.str.strip()

    # 3. Columnas a validar (Acumulados por canal)
    columnas_validar = [
        'Órdenes', 'Unidades', 'Venta Bruta', 'Descuento', 'Venta', 
        'Propina', 'Venta con Propina', 'Impuestos', 'Venta Neta', 
        'Costo', 'Margen %', 'Utilidad'
    ]

    # 4. Cruce de datos (Merge para comparar canales existentes en ambos lados)
    comparativa = pd.merge(
        df_athena, df_old, 
        on=col_llave, 
        suffixes=('_ATHENA', '_ANTIGUO'),
        how='outer'
    )

    diferencias = []

    print("Analizando métricas por canal...")

    for index, fila in comparativa.iterrows():
        canal = fila[col_llave]
        
        # Saltamos si el canal falta en alguna de las dos bases (se maneja en pestañas aparte)
        if pd.isna(fila.get('Venta_ATHENA')) or pd.isna(fila.get('Venta_ANTIGUO')):
            continue

        for col in columnas_validar:
            col_a = f"{col}_ATHENA"
            col_o = f"{col}_ANTIGUO"
            
            if col_a in comparativa.columns and col_o in comparativa.columns:
                val_a = fila[col_a]
                val_o = fila[col_o]
                
                # Validación numérica con tolerancia para decimales (0.1)
                try:
                    if abs(float(val_a or 0) - float(val_o or 0)) > 0.1:
                        diferencias.append({
                            'Canal de Venta': canal,
                            'Métrica': col,
                            'Valor_Athena': val_a,
                            'Valor_Antiguo': val_o,
                            'Diferencia_Absoluta': abs(float(val_a or 0) - float(val_o or 0))
                        })
                except (ValueError, TypeError):
                    # En caso de que el valor sea texto
                    if str(val_a).strip() != str(val_o).strip():
                        diferencias.append({
                            'Canal de Venta': canal,
                            'Métrica': col,
                            'Valor_Athena': val_a,
                            'Valor_Antiguo': val_o,
                            'Diferencia_Absoluta': 'N/A (Texto)'
                        })

    # 5. Generación del reporte Excel de control
    df_resultado = pd.DataFrame(diferencias)
    
    # Canales que solo existen en un reporte
    solo_en_athena = df_athena[~df_athena[col_llave].isin(df_old[col_llave])]
    solo_en_no_athena = df_old[~df_old[col_llave].isin(df_athena[col_llave])]

    with pd.ExcelWriter(archivo_control) as writer:
        if not df_resultado.empty:
            df_resultado.to_excel(writer, sheet_name='DIFERENCIAS_POR_CANAL', index=False)
        else:
            pd.DataFrame(['Todos los canales coinciden']).to_excel(writer, sheet_name='SIN_DIFERENCIAS', index=False)
            
        solo_en_athena.to_excel(writer, sheet_name='CANALES_NUEVOS_ATHENA', index=False)
        solo_en_no_athena.to_excel(writer, sheet_name='CANALES_FALTANTES', index=False)

    print("\n" + "="*45)
    print("REPORTE DE CANALES COMPLETADO")
    print(f"Diferencias de datos detectadas: {len(df_resultado)}")
    print(f"Canales nuevos: {len(solo_en_athena)}")
    print(f"Canales faltantes: {len(solo_en_no_athena)}")
    print(f"Reporte generado en: {archivo_control}")
    print("="*45)

if __name__ == "__main__":
    validar_ventas_canal()