let pollIntervals = {};
let currentConsoleTest = null;

async function runTest(testType) {
    const btn = document.getElementById(`btn-${testType}`);
    const status = document.getElementById(`status-${testType}`);
    
    // Recolectar datos dinámicos según el testType
    let payload = {};
    if (testType === 'acceso') {
        payload.email = document.getElementById('acceso-email').value;
        payload.empresa = document.getElementById('acceso-empresa').value;
        payload.exhaustivo = document.getElementById('acceso-exhaustivo').checked;
    } else if (testType === 'sedes') {
        payload.nombre = document.getElementById('sedes-nombre').value;
        payload.direccion = document.getElementById('sedes-direccion').value;
        payload.exhaustivo = document.getElementById('sedes-exhaustivo').checked;
    } else if (testType === 'productos') {
        payload.nombre = document.getElementById('productos-nombre').value;
        payload.sku = document.getElementById('productos-sku').value;
        payload.barcode = document.getElementById('productos-barcode').value;
        payload.costo = document.getElementById('productos-costo').value;
        payload.propiedad = document.getElementById('productos-propiedad').value;
        payload.atributos = document.getElementById('productos-atributos').value;
        payload.perecedero = document.getElementById('productos-perecedero').checked;
        payload.exhaustivo = document.getElementById('productos-exhaustivo').checked;
    } else if (testType === 'pos') {
        payload.producto = document.getElementById('pos-producto').value;
        payload.exhaustivo = document.getElementById('pos-exhaustivo').checked;
    }
    
    // UI Loading state
    btn.disabled = true;
    btn.innerHTML = `Ejecutando... <span class="spinner">↻</span>`;
    status.className = 'status-indicator running';
    status.innerText = 'En ejecución';

    // Open console
    showConsole(testType);
    
    try {
        const response = await fetch(`/api/run/${testType}`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('Error al iniciar la prueba');
        
        // Start polling for logs
        if (pollIntervals[testType]) clearInterval(pollIntervals[testType]);
        pollIntervals[testType] = setInterval(() => pollStatus(testType, btn, status), 1500);
        
    } catch (error) {
        console.error(error);
        resetUI(testType, btn, status, 'Error', 'failed');
    }
}

async function pollStatus(testType, btn, status) {
    try {
        const response = await fetch(`/api/status/${testType}`);
        const data = await response.json();
        
        // Update console if it's the currently viewed test
        if (currentConsoleTest === testType) {
            const consoleOutput = document.getElementById('console-output');
            if (data.log) {
                consoleOutput.innerText = data.log;
                // Auto scroll to bottom
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            }
            
            // Show or hide OTP input panel based on waiting_otp flag
            const otpContainer = document.getElementById('otp-input-container');
            if (data.waiting_otp) {
                otpContainer.classList.remove('hidden');
            } else {
                otpContainer.classList.add('hidden');
            }
        }
        
        // Check if finished
        if (!data.running && data.log) {
            clearInterval(pollIntervals[testType]);
            
            if (data.result === 'success') {
                resetUI(testType, btn, status, 'Exitoso', 'success');
            } else {
                resetUI(testType, btn, status, 'Fallido', 'failed');
            }
            
            // Hide OTP if finished
            if (currentConsoleTest === testType) {
                document.getElementById('otp-input-container').classList.add('hidden');
            }
        }
        
    } catch (error) {
        console.error('Error polling status:', error);
    }
}

function resetUI(testType, btn, statusElement, statusText, statusClass) {
    btn.disabled = false;
    btn.innerText = `Ejecutar Módulo`;
    statusElement.className = `status-indicator ${statusClass}`;
    statusElement.innerText = statusText;
}

function showConsole(testType) {
    currentConsoleTest = testType;
    const container = document.getElementById('console-container');
    const target = document.getElementById('console-target');
    const output = document.getElementById('console-output');
    
    target.innerText = `- Módulo ${testType.toUpperCase()}`;
    output.innerText = 'Conectando con la ejecución...';
    container.classList.remove('hidden');
    document.getElementById('otp-input-container').classList.add('hidden');
}

function closeConsole() {
    currentConsoleTest = null;
    document.getElementById('console-container').classList.add('hidden');
}

async function submitOtp() {
    if (!currentConsoleTest) return;
    
    const otpInput = document.getElementById('otp-digit');
    const btnSubmit = document.getElementById('btn-submit-otp');
    const otp = otpInput.value.trim();
    
    if (otp === '') {
        alert('Por favor, ingresa un valor válido.');
        return;
    }
    
    btnSubmit.disabled = true;
    btnSubmit.innerText = 'Enviando...';
    
    try {
        const response = await fetch(`/api/submit_otp/${currentConsoleTest}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ otp: otp })
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'Error al enviar input');
        }
        
        // Success
        otpInput.value = '';
        document.getElementById('otp-input-container').classList.add('hidden');
    } catch (error) {
        alert(error.message);
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerText = 'Enviar Input';
    }
}
