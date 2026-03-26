from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_otp_from_console():
    """
    Solicita el código OTP por consola con validación
    """
    while True:
        otp_code = input("🔢 Por favor ingresa el código OTP de 4 dígitos que recibiste: ").strip()
        
        # Validaciones
        if len(otp_code) != 4:
            print("❌ El código debe tener exactamente 4 dígitos. Intenta nuevamente.")
            continue
            
        if not otp_code.isdigit():
            print("❌ El código debe contener solo números. Intenta nuevamente.")
            continue
            
        # Confirmación
        confirm = input(f"✅ ¿Confirmar código '{otp_code}'? (s/n): ").strip().lower()
        if confirm in ['s', 'si', 'sí', 'yes', 'y']:
            return otp_code
        else:
            print("🔄 Ingresa el código nuevamente...")

def enter_otp_automatically(driver, otp_code):
    """
    Ingresa el OTP automáticamente en los inputs
    """
    try:
        print("🔄 Buscando inputs del OTP...")
        
        # Esperar a que los inputs estén disponibles
        wait = WebDriverWait(driver, 15)
        inputs = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'input.ant-input.ant-input-lg[type="text"][maxlength="1"]')
        ))
        
        if len(inputs) < 4:
            # Intentar con otro selector si es necesario
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input.ant-input.ant-input-lg[type="text"]')
        
        if len(inputs) < 4:
            raise Exception(f"Solo se encontraron {len(inputs)} inputs de OTP")
        
        print(f"✅ Encontrados {len(inputs)} inputs de OTP")
        
        # Ingresar dígito por dígito
        for i, digit in enumerate(otp_code):
            try:
                # Hacer scroll para hacer visible el input
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inputs[i])
                
                # Limpiar y escribir el dígito
                inputs[i].clear()
                inputs[i].send_keys(digit)
                print(f"   📝 Input {i+1}: {digit}")
                
                time.sleep(0.3)  # Pausa breve entre dígitos
                
            except Exception as e:
                print(f"⚠️  Error en input {i+1}: {e}")
                # Intentar con JavaScript como respaldo
                driver.execute_script(f"arguments[0].value = '{digit}';", inputs[i])
        
        print("🎉 OTP ingresado exitosamente!")
        
        # Verificar que se ingresó correctamente
        time.sleep(1)
        verify_otp(driver, otp_code)
        
    except Exception as e:
        print(f"❌ Error al ingresar OTP: {e}")
        raise

def verify_otp(driver, expected_otp):
    """
    Verifica que el OTP se haya ingresado correctamente
    """
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input.ant-input.ant-input-lg[type="text"]')
        entered_otp = ''.join([input.get_attribute('value') or '' for input in inputs[:4]])
        
        if entered_otp == expected_otp:
            print(f"✅ Verificación exitosa: OTP '{entered_otp}' correctamente ingresado")
        else:
            print(f"⚠️  Advertencia: Se ingresó '{entered_otp}' pero se esperaba '{expected_otp}'")
            
    except Exception as e:
        print(f"⚠️  No se pudo verificar el OTP: {e}")

def main():
    """
    Función principal del script
    """
    print("🚀 Iniciando automatización de OTP")
    print("=" * 50)
    
    # Inicializar el navegador (ajusta según tu necesidad)
    driver = webdriver.Chrome()
    
    try:
        # Aquí va tu código para navegar a la página
        # driver.get("https://tu-pagina.com")
        
        print("👀 Por favor, abre la página donde está el formulario OTP...")
        input("Presiona Enter cuando la página esté cargada y lista para el OTP...")
        
        # Obtener el OTP por consola
        otp_code = get_otp_from_console()
        
        # Ingresar el OTP automáticamente
        enter_otp_automatically(driver, otp_code)
        
        print("\n" + "=" * 50)
        print("✅ Proceso completado. El OTP ha sido ingresado.")
        print("💡 Puedes continuar con el siguiente paso manualmente si es necesario.")
        
        # Mantener el navegador abierto para revisión
        input("Presiona Enter para cerrar el navegador...")
        
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")
        
    finally:
        driver.quit()
        print("👋 Navegador cerrado. Fin del programa.")

# Versión simplificada si ya tienes el driver iniciado
def quick_otp_entry(driver):
    """
    Versión rápida para usar cuando ya tienes el driver activo
    """
    otp_code = get_otp_from_console()
    enter_otp_automatically(driver, otp_code)
    return otp_code

if __name__ == "__main__":
    main()