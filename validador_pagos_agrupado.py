import pandas as pd
import os

def validar_pagos_agrupados():
    # 1. Configuración de rutas
    ruta_descargas = r'C:\Users\yonas\Downloads'
    archivo_athena = os.path.join(ruta_descargas, 'reporte de ventas agrupado por metodo de pago athena.xlsx')
    archivo_no_athena = os.path.join(ruta_descargas, 'reporte de ventas agrupado por metodo de pago no athena.xlsx')
    archivo_control = os.path.join(ruta_descargas, 'CONTROL_DIFERENCIAS_PAGOS_AGRUPADOS.xlsx')

    print("--- Iniciando validación de Totales por Método de Pago ---")

    try:
        df_athena = pd.read_excel(archivo_athena)
        df_old = pd.read_excel(archivo_no_athena)
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        return

    # 2. Normalización de la llave principal
    col_llave = 'Método de Pago'
    for df in [df_athena, df_old]:
        df[col_llave] = df[col_llave].astype(str).str.strip().str.upper()
        df.columns = df.columns.str.strip()

    # 3. Columnas a validar
    columnas_validar = ['Órdenes', 'Total Pagado']

    # 4. Cruce de datos
    comparativa = pd.merge(
        df_athena, df_old, 
        on=col_llave, 
        suffixes=('_ATHENA', '_ANTIGUO'),
        how='outer'
    )

    diferencias = []

    print("Comparando totales globales...")

    for index, fila in comparativa.iterrows():
        metodo = fila[col_llave]
        
        # Ignorar si el método no existe en un lado (se ve en las otras pestañas)
        if pd.isna(fila.get('Total Pagado_ATHENA')) or pd.isna(fila.get('Total Pagado_ANTIGUO')):
            continue

        for col in columnas_validar:
            col_a = f"{col}_ATHENA"
            col_o = f"{col}_ANTIGUO"
            
            val_a = float(fila[col_a] or 0)
            val_o = float(fila[col_o] or 0)
            
            # Validación con tolerancia para centavos
            if abs(val_a - val_o) > 0.1:
                diferencias.append({
                    'Método de Pago': metodo,
                    'Campo': col,
                    'Total_Athena': val_a,
                    'Total_Antiguo': val_o,
                    'Diferencia': val_a - val_o
                })

    # 5. Generación del reporte de control
    df_diffs = pd.DataFrame(diferencias)
    solo_athena = df_athena[~df_athena[col_llave].isin(df_old[col_llave])]
    solo_old = df_old[~df_old[col_llave].isin(df_athena[col_llave])]

    with pd.ExcelWriter(archivo_control) as writer:
        if not df_diffs.empty:
            df_diffs.to_excel(writer, sheet_name='DIFERENCIAS_TOTALES', index=False)
        else:
            pd.DataFrame(['Todos los totales por método de pago coinciden']).to_excel(writer, sheet_name='OK', index=False)
            
        solo_athena.to_excel(writer, sheet_name='METODOS_NUEVOS_ATHENA', index=False)
        solo_old.to_excel(writer, sheet_name='METODOS_FALTANTES', index=False)

    print("\n" + "="*45)
    print("REPORTE DE TOTALES POR PAGO COMPLETADO")
    print(f"Diferencias encontradas: {len(df_diffs)}")
    print(f"Nuevos métodos detectados: {len(solo_athena)}")
    print(f"Métodos que no aparecen: {len(solo_old)}")
    print(f"Archivo guardado en: {archivo_control}")
    print("="*45)

if __name__ == "__main__":
    validar_pagos_agrupados()