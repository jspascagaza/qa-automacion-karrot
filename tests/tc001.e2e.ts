import { test, expect } from 'e2e';
import { GoogleSpreadsheet } from 'google-spreadsheet';
import { JWT } from 'google-auth-library';
import * as fs from 'fs';
import * as path from 'path';
import 'dotenv/config';

// =====================
// HELPER: LOGS Y GOOGLE SHEETS
// =====================

// Replicamos tu Logger en Python
function setupLogger(testName: string) {
  const logsDir = path.resolve(process.cwd(), 'logs');
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir);
  }

  const now = new Date();
  const dateStr = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}`;
  const timeStr = `${now.getHours().toString().padStart(2, '0')}-${now.getMinutes().toString().padStart(2, '0')}-${now.getSeconds().toString().padStart(2, '0')}`;

  const logFile = path.resolve(logsDir, `${testName}_${dateStr}_${timeStr}.log`);

  // Interceptamos console.log para que escriba en terminal y archivo (como tu Logger)
  const originalLog = console.log;
  console.log = function (...args: any[]) {
    const msg = args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' ') + '\n';
    fs.appendFileSync(logFile, msg);
    originalLog.apply(console, args);
  };
}

// Replicamos tu 'registrar_resultado' de gspread
async function registrarResultado(idCaso: string, estado: string, observaciones: string) {
  try {
    const credsPath = process.env.GOOGLE_CREDENTIALS_PATH || 'automatizacion-karrot-456d1a1552ca.json';
    const absPath = path.resolve(process.cwd(), credsPath);

    if (!fs.existsSync(absPath)) {
      console.log(`⚠️ No se pudo registrar ${idCaso} - Archivo de credenciales no encontrado en ${absPath}`);
      return;
    }

    const creds = JSON.parse(fs.readFileSync(absPath, 'utf-8'));

    // Autenticación tipo Service Account
    const auth = new JWT({
      email: creds.client_email,
      key: creds.private_key,
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });

    const doc = new GoogleSpreadsheet('1MIyz4grQ_U6VgAVY6PFMbTFin3GLBd7mc2mz15kAeaw', auth);
    await doc.loadInfo();
    const sheet = doc.sheetsByIndex[0]; // Tu sheet1

    // Para simular el "cls.sheet.find(id_caso)" de Python, cargamos las celdas
    await sheet.loadCells();
    let targetRowIndex = -1;

    // Buscamos la fila donde esté el ID del caso
    for (let r = 0; r < sheet.rowCount; r++) {
      for (let c = 0; c < sheet.columnCount; c++) {
        const cell = sheet.getCell(r, c);
        if (cell.value === idCaso) {
          targetRowIndex = r;
          break;
        }
      }
      if (targetRowIndex !== -1) break;
    }

    if (targetRowIndex !== -1) {
      const now = new Date();
      const fecha = `${now.getDate().toString().padStart(2, '0')}/${(now.getMonth() + 1).toString().padStart(2, '0')}/${now.getFullYear()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

      // En Python actualizabas columnas 11, 13, 14, 15 (K, M, N, O) que son índices 10, 12, 13, 14 (base 0)
      sheet.getCell(targetRowIndex, 10).value = "Sí";           // Columna K
      sheet.getCell(targetRowIndex, 12).value = fecha;          // Columna M
      sheet.getCell(targetRowIndex, 13).value = estado;         // Columna N
      sheet.getCell(targetRowIndex, 14).value = observaciones;  // Columna O

      await sheet.saveUpdatedCells();
      console.log(`✅ Caso ${idCaso} actualizado -> ${estado}`);
    } else {
      console.log(`⚠️ No se encontró el ID ${idCaso} en el documento de Sheets.`);
    }

  } catch (error) {
    console.log(`❌ Error al actualizar el caso ${idCaso}: ${(error as Error).message}`);
  }
}

// =====================
// CASO DE PRUEBA TC001
// =====================

test('TC001: Login exitoso', async ({ app, agent, screen }) => {
  setupLogger('test_login');

  const idCaso = 'TC001';
  console.log(`\n=== Iniciando ${idCaso} ===`);

  try {
    // 1. Ir a la URL (reemplaza driver.get)
    await app.open('/auth/login');

    // 2. Extraer el correo y la contraseña de las variables de entorno
    const emailVal = process.env.WEB_EMAIL || process.env.KARROT_LOGIN_EMAIL;
    const passVal = process.env.KARROT_LOGIN_PASSWORD;
    if (!emailVal) throw new Error('No se encontró el email en las variables de entorno');
    if (!passVal) throw new Error('No se encontró la contraseña en las variables de entorno');

    // 3. IA hace la interacción visual (dividido en pasos simples)
    await agent.act(`Escribe el correo '${emailVal}' en el campo de email.`);
    await agent.act(`Escribe la contraseña '${passVal}' en el campo de contraseña.`);
    await agent.act(`Haz click en el botón de iniciar sesión.`);

    // 4. Validación determinista rápida (espera hasta 15s a que aparezca el h1 del dashboard)
    await expect(screen.getByRole('heading')).toBeVisible({ timeout: 15000 });

    // 5. Registrar éxito en Google Sheets
    await registrarResultado(idCaso, 'Exitosa', 'Login realizado correctamente');

  } catch (error) {
    // 6. Registrar falla en Google Sheets si algo se rompe o el assert falla
    await registrarResultado(idCaso, 'Fallida', `Error: ${(error as Error).message}`);

    // Fallar la prueba explícitamente
    throw error;
  }
});
