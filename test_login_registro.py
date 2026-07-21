import unittest
import os
import sys
from datetime import datetime

# Importar las clases de prueba existentes
from test_login import TestLogin
from test_registro import TestRegistro

if __name__ == '__main__':
    # Configurar stdout para que vaya directamente a la consola web en tiempo real
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    print("=== Iniciando Módulo 1: Acceso (Login y Registro) ===")
    
    suite = unittest.TestSuite()
    
    # Pruebas Core (Siempre se ejecutan)
    suite.addTest(TestLogin('test_tc001')) # Login Exitoso
    suite.addTest(TestLogin('test_tc002')) # Login Fallido
    suite.addTest(TestRegistro('test_tc003')) # Registro Exitoso
    suite.addTest(TestRegistro('test_tc011')) # Redirección a login
    
    # Validaciones secundarias
    if os.getenv('WEB_EXEC_EXHAUSTIVO') == 'true':
        print("[INFO] Validaciones secundarias activadas.")
        suite.addTest(TestRegistro('test_tc004'))
        suite.addTest(TestRegistro('test_tc005'))
        suite.addTest(TestRegistro('test_tc006'))
        suite.addTest(TestRegistro('test_tc007'))
        suite.addTest(TestRegistro('test_tc008'))
        suite.addTest(TestRegistro('test_tc009'))
    else:
        print("[INFO] Validaciones secundarias desactivadas (modo Core).")

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Salir con código de error si alguna prueba falló
    if not result.wasSuccessful():
        sys.exit(1)
    else:
        sys.exit(0)
