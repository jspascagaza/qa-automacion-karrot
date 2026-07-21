import os
import glob
import subprocess
import time

def run_tests():
    test_files = sorted(glob.glob("TC*.py"))
    print(f"Encontrados {len(test_files)} casos de prueba.")
    
    resultados = []
    
    for test in test_files:
        print(f"Ejecutando {test}...")
        start_time = time.time()
        try:
            # Ejecutar con timeout de 3 minutos
            result = subprocess.run(["python", test], capture_output=True, text=True, timeout=180)
            elapsed = time.time() - start_time
            if result.returncode == 0:
                print(f"[EXITO] {test} (en {elapsed:.2f}s)")
                resultados.append({"test": test, "status": "EXITO", "error": ""})
            else:
                print(f"[FALLO] {test} (en {elapsed:.2f}s)")
                resultados.append({"test": test, "status": "FALLO", "error": result.stderr or result.stdout})
        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start_time
            print(f"[TIMEOUT] {test} (en {elapsed:.2f}s)")
            resultados.append({"test": test, "status": "TIMEOUT", "error": f"Timeout después de {elapsed:.2f} segundos."})
        except Exception as e:
            print(f"[ERROR] {test} - {str(e)}")
            resultados.append({"test": test, "status": "ERROR", "error": str(e)})

    # Escribir resumen
    with open("test_summary_report.txt", "w", encoding="utf-8") as f:
        for res in resultados:
            if res["status"] != "EXITO":
                f.write(f"--- FALLO EN {res['test']} ---\n")
                f.write(res["error"][-2000:] if len(res["error"]) > 2000 else res["error"])
                f.write("\n\n")

if __name__ == "__main__":
    run_tests()
