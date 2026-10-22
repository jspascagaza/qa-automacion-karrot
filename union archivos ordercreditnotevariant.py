from pathlib import Path
import pandas as pd


def consolidar_todos_los_csvs(
    directorio_carpeta: str = r"C:\Users\yonas\Downloads\variantcreditnote",
    archivo_salida: str = r"C:\Users\yonas\Downloads\credit_notes_unificado.csv",
    separador: str = ",",
    encoding: str = "utf-8",
) -> None:
  ruta = Path(directorio_carpeta)

  if not ruta.exists():
    print(f"[!] La ruta especificada no existe: {ruta}")
    return

  # Buscar todos los archivos .csv dentro de la carpeta
  archivos_csv = sorted(ruta.glob("*.csv"))

  # Si el archivo final se guarda en la misma carpeta, excluirlo para no duplicar datos
  archivo_salida_path = Path(archivo_salida).resolve()
  archivos_csv = [f for f in archivos_csv if f.resolve() != archivo_salida_path]

  if not archivos_csv:
    print(f"[!] No se encontraron archivos .csv en: {ruta.resolve()}")
    return

  print(f"Se encontraron {len(archivos_csv)} archivo(s) .csv para procesar.")

  lista_dfs = []

  for archivo in archivos_csv:
    try:
      df = pd.read_csv(archivo, sep=separador, encoding=encoding)
      lista_dfs.append(df)
      print(f" [+] Leido: {archivo.name} ({len(df)} filas)")
    except UnicodeDecodeError:
      try:
        df = pd.read_csv(archivo, sep=separador, encoding="latin-1")
        lista_dfs.append(df)
        print(f" [+] Leido (latin-1): {archivo.name} ({len(df)} filas)")
      except Exception as e:
        print(f" [-] Error leyendo {archivo.name}: {e}")
    except Exception as e:
      print(f" [-] Error al leer {archivo.name}: {e}")

  if lista_dfs:
    df_final = pd.concat(lista_dfs, ignore_index=True)
    df_final.to_csv(
        archivo_salida, index=False, sep=separador, encoding=encoding
    )
    print("=" * 60)
    print("Consolidacion completada con exito!")
    print(f"Archivos procesados: {len(lista_dfs)}")
    print(f"Total de registros consolidados: {len(df_final)}")
    print(f"Archivo guardado en: {archivo_salida}")
  else:
    print("[!] No se pudo consolidar ningun archivo.")


if __name__ == "__main__":
  # --- CONFIGURA TUS RUTAS AQUI ---
  # 1. Ruta de la carpeta donde estan tus CSVs:
  CARPETA_ORIGEN = r"C:\Users\yonas\Downloads\variantcreditnote"

  # 2. Ruta y nombre donde quieres guardar el archivo consolidado:
  ARCHIVO_FINAL = r"C:\Users\yonas\Downloads\credit_notes_unificado.csv"

  consolidar_todos_los_csvs(
      directorio_carpeta=CARPETA_ORIGEN,
      archivo_salida=ARCHIVO_FINAL,
      separador=",",
      encoding="utf-8",
  )