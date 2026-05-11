import pandas as pd
import os

def validar_metodos_pago():
    # 1. Rutas de archivos
    ruta_descargas = r'C:\Users\yonas\Downloads'
    archivo_athena = os.path.join(ruta_descargas, 'reporte de ventas por metodo de pago athena.xlsx')
    archivo_no_athena = os.path.join(ruta_descargas, 'reporte de ventas por metodo de pago no athena.xlsx')
    archivo_control = os.path.join(ruta_descargas, 'CONTROL_DIFERENCIAS_METODOS_PAGOS.xlsx')

    print("--- Iniciando validación por Métodos de Pago ---")

    try:
        df_athena = pd.read_excel(archivo_athena)
        df_old = pd.read_excel(archivo_no_athena)
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        return

    # 2. Preparación de llaves
    col_llave = '# Factura'
    for df in [df_athena, df_old]:
        df[col_llave] = df[col_llave].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        # Creamos un ranking por factura para comparar el pago 1, pago 2, etc.
        df['pago_n'] = df.groupby(col_llave).cumcount() + 1

    # 3. Campos a comparar
    campos_a_validar = [
        'Nombre Método de Pago', 'Valor Método de Pago', 'approvalCode',
        'Nombre Cliente', 'Fecha', 'Hora', 'Canal de Venta', 'Caja'
    ]

    # 4. Cruce de datos
    comparativa = pd.merge(
        df_athena, df_old, 
        on=[col_llave, 'pago_n'], 
        suffixes=('_ATHENA', '_ANTIGUO'),
        how='outer'
    )

    diferencias = []

    print("Buscando discrepancias en los pagos...")

    for index, fila in comparativa.iterrows():
        factura = fila[col_llave]
        
        # Saltamos si la factura no existe en alguno de los dos lados (eso va a otra pestaña)
        if pd.isna(fila.get('Valor Método de Pago_ATHENA')) or pd.isna(fila.get('Valor Método de Pago_ANTIGUO')):
            continue

        for col in campos_a_validar:
            col_a = f"{col}_ATHENA"
            col_o = f"{col}_ANTIGUO"
            
            # Solo comparamos si la columna existe en ambos reportes
            if col_a in comparativa.columns and col_o in comparativa.columns:
                val_a = str(fila[col_a]).strip().replace('.0', '') if pd.notnull(fila[col_a]) else 'VACIO'
                val_o = str(fila[col_o]).strip().replace('.0', '') if pd.notnull(fila[col_o]) else 'VACIO'
                
                if val_a != val_o:
                    diferencias.append({
                        '# Factura': factura,
                        'Pago #': fila['pago_n'],
                        'Campo_Diferente': col,
                        'Valor_Athena': fila[col_a],
                        'Valor_Antiguo': fila[col_o]
                    })

    # 5. Exportación del Reporte de Control
    df_diffs = pd.DataFrame(diferencias)
    solo_athena = df_athena[~df_athena[col_llave].isin(df_old[col_llave])]
    solo_old = df_old[~df_old[col_llave].isin(df_athena[col_llave])]

    with pd.ExcelWriter(archivo_control) as writer:
        if not df_diffs.empty:
            df_diffs.to_excel(writer, sheet_name='DIFERENCIAS_PAGOS', index=False)
        else:
            pd.DataFrame(['Sin diferencias encontradas']).to_excel(writer, sheet_name='SIN_DIFERENCIAS', index=False)
        
        solo_athena.to_excel(writer, sheet_name='FACTURAS_NUEVAS', index=False)
        solo_old.to_excel(writer, sheet_name='PAGOS_FALTANTES', index=False)

    print("\n" + "="*40)
    print("VALIDACIÓN FINALIZADA")
    print(f"Se encontraron {len(df_diffs)} diferencias en los campos de pago.")
    print(f"Reporte de control creado en: {archivo_control}")
    print("="*40)

if __name__ == "__main__":
    validar_metodos_pago()