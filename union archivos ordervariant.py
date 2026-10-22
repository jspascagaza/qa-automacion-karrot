from pathlib import Path
import pandas as pd

# Lista exacta de IDs requeridos
NUMEROS_PERMITIDOS = [
    "11006", "11116", "11117", "11118", "11119", "11120", "11121", "11122",
    "11123", "11124", "11125", "11126", "11127", "11128", "12236", "12237",
    "12238", "12246", "12247", "12248", "12249", "12261", "12262", "12263",
    "12264", "12265", "12266", "12268", "12269", "12270", "12271"
]


def unificar_csvs_especificos(
    directorio: str = r"C:\Users\yonas\Downloads",
    archivo_salida: str = r"C:\Users\yonas\Downloads\resultado_especificos_unificado.csv",
    separador: str = ",",
    encoding: str = "utf-8"
) -> None:
    ruta = Path(directorio)

    if not ruta.exists():
        print(f"[!] La ruta no existe: {ruta}")
        return

    permitidos_set = set(NUMEROS_PERMITIDOS)

    # Filtrar solo archivos .csv cuyo nombre este en la lista permitida
    archivos_objetivo = [
        archivo for archivo in ruta.glob("*.csv")
        if archivo.stem in permitidos_set
    ]
    archivos_objetivo.sort(key=lambda x: int(x.stem) if x.stem.isdigit() else x.stem)

    if not archivos_objetivo:
        print(f"No se encontraron archivos de la lista en: {ruta.resolve()}")
        return

    print(f"Archivos encontrados para unificar: {len(archivos_objetivo)} de {len(permitidos_set)} especificados.")

    lista_dfs = []

    for archivo in archivos_objetivo:
        numero_id = archivo.stem
        try:
            df = pd.read_csv(archivo, sep=separador, encoding=encoding)
            df.insert(0, "numero", numero_id)
            lista_dfs.append(df)
            print(f" [+] Leido: {archivo.name} | Total filas: {len(df)}")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(archivo, sep=separador, encoding="latin-1")
                df.insert(0, "numero", numero_id)
                lista_dfs.append(df)
                print(f" [+] Leido (latin-1): {archivo.name} | Total filas: {len(df)}")
            except Exception as e:
                print(f" [-] Error leyendo {archivo.name} con latin-1: {e}")
        except Exception as e:
            print(f" [-] Error procesando {archivo.name}: {e}")

    if lista_dfs:
        df_consolidado = pd.concat(lista_dfs, ignore_index=True)
        df_consolidado.to_csv(archivo_salida, index=False, sep=separador, encoding=encoding)
        print("=" * 60)
        print("Consolidacion exitosa!")
        print(f"Archivos procesados: {len(lista_dfs)}")
        print(f"Filas totales consolidadas: {len(df_consolidado)}")
        print(f"Archivo generado en: {archivo_salida}")
    else:
        print("[!] No se proceso ningun archivo.")


if __name__ == "__main__":
    unificar_csvs_especificos()