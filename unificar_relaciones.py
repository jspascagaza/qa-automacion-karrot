from pathlib import Path
import pandas as pd


def cruzar_archivos_con_left(
    carpeta_base: str = r"C:\Users\yonas\Downloads",
    nombre_notas: str = "notas_credito_no_timbradas.xlsx",
    nombre_orders: str = "orders_unificado.xlsx",
    nombre_credit_notes: str = "credit_notes_unificado.xlsx",
    nombre_salida: str = "credit_notes_con_orders.xlsx",
    deduplicar_ordenes: bool = True,
) -> None:
  carpeta = Path(carpeta_base)

  ruta_notas = carpeta / nombre_notas
  ruta_orders = carpeta / nombre_orders
  ruta_credit_notes = carpeta / nombre_credit_notes
  ruta_salida = carpeta / nombre_salida

  for etiqueta, ruta in [
      ("Notas de credito", ruta_notas),
      ("Ordenes unificadas", ruta_orders),
      ("Notas de credito unificadas", ruta_credit_notes),
  ]:
    if not ruta.exists():
      print(f"[!] Archivo no encontrado ({etiqueta}): {ruta.resolve()}")
      return

  print("Cargando archivos Excel desde:", carpeta.resolve())
  df_notas = pd.read_excel(ruta_notas)
  df_orders = pd.read_excel(ruta_orders)
  df_credit = pd.read_excel(ruta_credit_notes)

  print(
      f" -> Registros originales en credit_notes_unificado: {len(df_credit)}"
  )

  # 1. Preparar tabla puente (notas_credito_no_timbradas)
  df_puente = df_notas[["Order ID", "Credit Note ID"]].dropna().copy()
  df_puente.rename(
      columns={"Order ID": "orderID", "Credit Note ID": "creditNoteID"},
      inplace=True,
  )

  # Limpiar cadenas para que no fallen por espacios invisibles
  df_puente["orderID"] = df_puente["orderID"].astype(str).str.strip()
  df_puente["creditNoteID"] = (
      df_puente["creditNoteID"].astype(str).str.strip()
  )
  df_orders["orderID"] = df_orders["orderID"].astype(str).str.strip()
  df_credit["creditNoteID"] = (
      df_credit["creditNoteID"].astype(str).str.strip()
  )

  # Si una orden tiene reintentos (filas duplicadas en orders), tomar el registro más exitoso/reciente
  if deduplicar_ordenes:
    if "dianStatus" in df_orders.columns:
      df_orders = df_orders.sort_values(by="dianStatus", ascending=True)
    df_orders = df_orders.drop_duplicates(subset=["orderID"], keep="first")

  # 2. Paso 1: Relacionar puente con orders usando LEFT
  df_puente_orders = pd.merge(df_puente, df_orders, on="orderID", how="left")

  # 3. Paso 2: LEFT JOIN desde credit_notes_unificado
  # Garantiza que NINGÚN registro de credit_notes_unificado sea descartado
  df_resultado = pd.merge(
      df_credit,
      df_puente_orders,
      on="creditNoteID",
      how="left",
      suffixes=("", "_order"),
  )

  # 4. Guardar archivo final
  df_resultado.to_excel(ruta_salida, index=False)
  print("=" * 60)
  print("¡Consolidacion con LEFT completada!")
  print(
      f"Filas resultantes en el archivo final: {len(df_resultado)} (se"
      " mantuvieron todas las notas de credito)"
  )
  print(f"Columnas totales: {len(df_resultado.columns)}")
  print(f"Archivo guardado en: {ruta_salida.resolve()}")


if __name__ == "__main__":
  CARPETA_DESCARGAS = r"C:\Users\yonas\Downloads"

  cruzar_archivos_con_left(
      carpeta_base=CARPETA_DESCARGAS,
      nombre_notas="notas_credito_no_timbradas.xlsx",
      nombre_orders="orders_unificado.xlsx",
      nombre_credit_notes="credit_notes_unificado.xlsx",
      nombre_salida="credit_notes_con_orders.xlsx",
      deduplicar_ordenes=True,
  )