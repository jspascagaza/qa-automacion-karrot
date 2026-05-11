import subprocess
import os
import sys

# Lista de todos los archivos de prueba TC023
archivos_tc023 = [
    "TC023 Creación exitosa de producto con datos válidos.py",
    "TC023 Creacion exitosa sin atributos.py",
    "TC023 Creacion exitosa sin atributos y perecedero.py",
    "TC023 Creacion exitosa con atributos.py",
    "TC023 Creacion exitosa con atributos y producto perecedero.py"
]

def ejecutar_pruebas():
    print("="*60)
    print("   INICIANDO EJECUCIÓN DE TODOS LOS CASOS TC023")
    print("="*60)
    
    # Obtener el directorio actual donde se espera que estén los scripts
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    
    resultados = []

    for archivo in archivos_tc023:
        ruta_archivo = os.path.join(directorio_base, archivo)
        
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            print(f"\n⚠️ Advertencia: No se encontró el archivo '{archivo}'")
            resultados.append((archivo, "No encontrado"))
            continue
            
        print(f"\n▶️ Ejecutando: {archivo} ...")
        
        try:
            # Ejecutar el script usando el ejecutable actual de python
            proceso = subprocess.run(
                [sys.executable, ruta_archivo],
                check=False, # No lanzar excepción en caso de error (código != 0)
                text=True    # Redirigir salida a texto si fuese necesario capturarla
            )
            
            if proceso.returncode == 0:
                print(f"✅ Finalizó con éxito: {archivo}")
                resultados.append((archivo, "Exitoso"))
            else:
                print(f"❌ Falló la ejecución: {archivo} (Código de salida: {proceso.returncode})")
                resultados.append((archivo, "Fallido"))
                
        except Exception as e:
            print(f"❌ Ocurrió una excepción al ejecutar {archivo}:\n{str(e)}")
            resultados.append((archivo, "Error de Ejecución"))
            
    print("\n" + "="*60)
    print("                  RESUMEN DE EJECUCIÓN")
    print("="*60)
    for archivo, estado in resultados:
        if estado == "Exitoso":
            print(f"✅ {archivo} -> {estado}")
        elif estado == "Fallido" or estado == "Error de Ejecución":
            print(f"❌ {archivo} -> {estado}")
        else:
            print(f"⚠️ {archivo} -> {estado}")
            
    print("="*60)

if __name__ == "__main__":
    ejecutar_pruebas()
