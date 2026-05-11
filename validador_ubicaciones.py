import pandas as pd
import os

def validar_ventas_ubicacion():
    # 1. Configuración de rutas
    ruta_descargas = r'C:\Users\yonas\Downloads'
    archivo_athena = os.path.join(ruta_descargas, 'reporte de ventas por ubicacion athena.xlsx')
    archivo_no_athena = os.path.join(ruta_descargas, 'reporte de ventas por ubicacion no athena.xlsx')
    archivo_control = os.path.join(ruta_descargas, 'CONTROL_DIFERENCIAS_UBICACIONES.xlsx')

    print("--- Iniciando validación de Ventas por Ubicación ---")

    try:
        df_athena = pd.read_excel(archivo_athena)
        df_old = pd.read_excel(archivo_no_athena)
    except Exception as e:
        print(f"Error al cargar los archivos: {e}")
        return

    # 2. Normalización de la llave principal (Nombre Ubicación)
    col_llave = 'Nombre Ubicación'
    for df in [df_athena, df_old]:
        df[col_llave] = df[col_llave].astype(str).str.strip().str.upper()
        df.columns = df.columns.str.strip()

    # 3. Columnas a validar (Acumulados financieros y de conteo)
    columnas_validar = [
        'Órdenes', 'Unidades', 'Venta Bruta', 'Descuento', 'Venta', 
        'Propina', 'Venta con Propina', 'Impuestos', 'Venta Neta', 
        'Costo', 'Margen %', 'Utilidad', 'Nombre Ciudad'
    ]

    # 4. Cruce de datos (Outer join para ver si faltan sedes)
    comparativa = pd.merge(
        df_athena, df_old, 
        on=col_llave, 
        suffixes=('_ATHENA', '_ANTIGUO'),
        how='outer'
    )

    diferencias = []

    print("Comparando acumulados por sede...")

    for index, fila in comparativa.iterrows():
        ubicacion = fila[col_llave]
        
        # Caso: La ubicación no existe en uno de los dos reportes
        if pd.isna(fila.get('Venta_ATHENA')):
            continue # Se gestiona en la pestaña de faltantes
        if pd.isna(fila.get('Venta_ANTIGUO')):
            continue

        for col in columnas_validar:
            col_a = f"{col}_ATHENA"
            col_o = f"{col}_ANTIGUO"
            
            if col_a in comparativa.columns and col_o in comparativa.columns:
                # Para valores numéricos, comparamos con un redondeo para evitar diferencias por decimales mínimos
                val_a = fila[col_a]
                val_o = fila[col_o]
                
                # Si son strings (como Nombre Ciudad)
                if isinstance(val_a, str) or isinstance(val_o, str):
                    if str(val_a).strip() != str(val_o).strip():
                        diferencias.append({
                            'Ubicación': ubicacion,
                            'Campo': col,
                            'Valor_Athena': val_a,
                            'Valor_Antiguo': val_o
                        })
                # Si son números
                else:
                    if abs(float(val_a or 0) - float(val_o or 0)) > 0.1: # Tolerancia de 0.1 centavos
                        diferencias.append({
                            'Ubicación': ubicacion,
                            'Campo': col,
                            'Valor_Athena': val_a,
                            'Valor_Antiguo': val_o
                        })

    # 5. Generación del reporte de control
    df_resultado = pd.DataFrame(diferencias)
    
    # Identificar sedes faltantes
    solo_en_athena = df_athena[~df_athena[col_llave].isin(df_old[col_llave])]
    solo_en_no_athena = df_old[~df_old[col_llave].isin(df_athena[col_llave])]

    with pd.ExcelWriter(archivo_control) as writer:
        if not df_resultado.empty:
            df_resultado.to_excel(writer, sheet_name='DIFERENCIAS_ACUMULADOS', index=False)
        else:
            pd.DataFrame(['Todos los acumulados coinciden']).to_excel(writer, sheet_name='OK', index=False)
            
        solo_en_athena.to_excel(writer, sheet_name='UBICACIONES_NUEVAS', index=False)
        solo_en_no_athena.to_excel(writer, sheet_name='UBICACIONES_FALTANTES', index=False)

    print("\n" + "="*45)
    print("REPORTE DE UBICACIONES COMPLETADO")
    print(f"Diferencias encontradas: {len(df_resultado)}")
    print(f"Sedes nuevas: {len(solo_en_athena)}")
    print(f"Sedes faltantes: {len(solo_en_no_athena)}")
    print(f"Archivo guardado en: {archivo_control}")
    print("="*45)

if __name__ == "__main__":
    validar_ventas_ubicacion()