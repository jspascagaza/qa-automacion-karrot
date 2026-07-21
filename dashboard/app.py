from flask import Flask, render_template, jsonify, request
import subprocess
import threading
import os
import glob

app = Flask(__name__)

# Almacenar el estado actual de las pruebas
test_status = {
    "login": {"running": False, "log": "", "result": ""},
    "registro": {"running": False, "log": "", "result": ""},
    "tc011": {"running": False, "log": "", "result": "", "waiting_otp": False}
}

# Referencias a procesos activos
active_processes = {}

def run_test(test_name, script_name, env_vars=None):
    test_status[test_name]["running"] = True
    test_status[test_name]["log"] = "Iniciando pruebas...\n"
    test_status[test_name]["result"] = ""
    test_status[test_name]["waiting_otp"] = False
    
    try:
        # Preparar variables de entorno uniendo las del sistema y las del payload
        process_env = os.environ.copy()
        if env_vars:
            for key, val in env_vars.items():
                if val is not None:
                    process_env[key] = str(val)

        # Ejecutar el script con python -u para deshabilitar el buffering de salida
        process = subprocess.Popen(
            ["python", "-u", script_name],
            cwd="..",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=process_env,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        active_processes[test_name] = process
        
        # Leer salida carácter por carácter para detectar prompts interactivos
        buffer = ""
        while True:
            char = process.stdout.read(1)
            if not char:
                break
            test_status[test_name]["log"] += char
            buffer += char
            
            # Detectar si se está solicitando el OTP (sin esperar nueva línea)
            if "Ingresa el código OTP" in buffer or "Se requiere entrada" in buffer:
                test_status[test_name]["waiting_otp"] = True
                buffer = ""
            
            if char == '\n':
                buffer = ""
                
        process.stdout.close()
        return_code = process.wait()
        
        if return_code == 0:
            test_status[test_name]["result"] = "success"
        else:
            test_status[test_name]["result"] = "failed"
            
    except Exception as e:
        test_status[test_name]["log"] += f"\nError al ejecutar la prueba: {str(e)}"
        test_status[test_name]["result"] = "failed"
        
    test_status[test_name]["running"] = False
    test_status[test_name]["waiting_otp"] = False
    active_processes.pop(test_name, None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run/<test_type>', methods=['POST'])
def start_test(test_type):
    data = request.json or {}
    
    # Crear un entorno limpio con prefijo WEB_
    env_vars = {}
    for k, v in data.items():
        if isinstance(v, bool):
            env_vars[f"WEB_EXEC_{k.upper()}"] = "true" if v else "false"
        elif v: # Solo si no está vacío
            env_vars[f"WEB_{k.upper()}"] = str(v)
            
    if test_status.get(test_type, {}).get("running"):
        return jsonify({"message": "La prueba ya está en ejecución"}), 400
        
    # Inicializar estado si es nuevo módulo
    if test_type not in test_status:
        test_status[test_type] = {"running": False, "log": "", "result": "", "waiting_otp": False}
        
    if test_type == "acceso":
        script_name = "test_login_registro.py"
    elif test_type == "sedes":
        script_name = "test_sedes_cajas.py"
    elif test_type == "productos":
        script_name = "test_productos.py"
    elif test_type == "pos":
        script_name = "test_inventario_pos.py"
    else:
        return jsonify({"error": "Tipo de prueba no válido"}), 400
    
    # Iniciar la prueba en un hilo separado
    thread = threading.Thread(target=run_test, args=(test_type, script_name, env_vars))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": f"Iniciando pruebas de {test_type}"})

@app.route('/api/status/<test_type>')
def get_status(test_type):
    if test_type not in test_status:
        return jsonify({"error": "Tipo de prueba no válido"}), 400
    return jsonify(test_status[test_type])

@app.route('/api/submit_otp/<test_type>', methods=['POST'])
def submit_otp(test_type):
    data = request.json or {}
    otp = data.get('otp', '')
    
    if test_type not in active_processes:
        return jsonify({"error": "No hay ningún proceso activo para esta prueba"}), 400
        
    process = active_processes[test_type]
    try:
        # Escribir el OTP en el canal de entrada del proceso
        process.stdin.write(otp + '\n')
        process.stdin.flush()
        test_status[test_type]["waiting_otp"] = False
        return jsonify({"message": "OTP enviado al proceso"})
    except Exception as e:
        return jsonify({"error": f"Error al enviar OTP: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
