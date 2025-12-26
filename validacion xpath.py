from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json

class AutoLoginWithExtractor:
    def __init__(self):
        """Inicializa el auto-login con extracción de elementos"""
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 40)
        
    def extract_login_elements(self):
        """Extrae automáticamente los elementos de login"""
        print("🔍 Extrayendo elementos de login...")
        
        elements = {
            'url': self.driver.current_url,
            'title': self.driver.title,
            'elements': {}
        }
        
        # Buscar todos los elementos relevantes
        element_types = {
            'email_fields': [
                "input[@type='email']",
                "input[contains(@id, 'email')]",
                "input[contains(@name, 'email')]",
                "input[contains(@placeholder, 'email')]",
                "*[@id='login-form_email']"
            ],
            'password_fields': [
                "input[@type='password']",
                "input[contains(@id, 'password')]",
                "input[contains(@name, 'password')]",
                "input[contains(@placeholder, 'password')]",
                "*[@id='login-form_password']"
            ],
            'submit_buttons': [
                "button[@type='submit']",
                "button[contains(text(), 'Iniciar')]",
                "button[contains(text(), 'Login')]",
                "button[contains(text(), 'Sign')]",
                "//*[@id='login-form']/div[3]/div/div/div/div/button"
            ]
        }
        
        for category, selectors in element_types.items():
            elements['elements'][category] = []
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        # XPath
                        found_elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS Selector
                        found_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elem in found_elements:
                        element_info = {
                            'xpath': self.get_element_xpath(elem),
                            'selector': selector,
                            'tag': elem.tag_name,
                            'attributes': self.get_element_attributes(elem),
                            'visible': elem.is_displayed(),
                            'enabled': elem.is_enabled()
                        }
                        elements['elements'][category].append(element_info)
                        print(f"✅ Encontrado {category}: {element_info['xpath'][:50]}...")
                        
                except Exception as e:
                    continue
        
        # Guardar elementos extraídos
        with open('login_elements.json', 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        
        print("✅ Elementos guardados en login_elements.json")
        return elements
    
    def get_element_xpath(self, element):
        """Obtiene el XPath de un elemento"""
        return self.driver.execute_script("""
            function getElementXPath(element) {
                if (element.id !== '')
                    return '//*[@id="' + element.id + '"]';
                if (element === document.body)
                    return '/html/body';
                
                var ix = 0;
                var siblings = element.parentNode.childNodes;
                
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element)
                        return getElementXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + 
                               '[' + (ix + 1) + ']';
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                        ix++;
                }
            }
            return getElementXPath(arguments[0]);
        """, element)
    
    def get_element_attributes(self, element):
        """Obtiene los atributos de un elemento"""
        attrs = {}
        common_attrs = ['id', 'name', 'class', 'type', 'placeholder', 'value', 'aria-label']
        
        for attr in common_attrs:
            value = element.get_attribute(attr)
            if value:
                attrs[attr] = value
        
        return attrs
    
    def smart_login(self, email, password):
        """
        Login inteligente que primero extrae elementos y luego los usa
        """
        URL = "https://dev.do5o1l1ov8f4a.amplifyapp.com/auth/login"
        
        print("🌐 Navegando a la página de login...")
        self.driver.get(URL)
        self.driver.maximize_window()
        time.sleep(3)
        
        # Extraer elementos
        elements_data = self.extract_login_elements()
        
        print("\n🔐 Intentando login con elementos encontrados...")
        
        # Intentar con cada campo de email encontrado
        for email_field in elements_data['elements'].get('email_fields', []):
            try:
                elem = self.driver.find_element(By.XPATH, email_field['xpath'])
                if elem.is_displayed() and elem.is_enabled():
                    elem.click()
                    elem.clear()
                    elem.send_keys(email)
                    print(f"✅ Email ingresado usando: {email_field['xpath'][:50]}...")
                    break
            except:
                continue
        
        # Intentar con cada campo de password encontrado
        for password_field in elements_data['elements'].get('password_fields', []):
            try:
                elem = self.driver.find_element(By.XPATH, password_field['xpath'])
                if elem.is_displayed() and elem.is_enabled():
                    elem.click()
                    elem.clear()
                    elem.send_keys(password)
                    print(f"✅ Contraseña ingresada usando: {password_field['xpath'][:50]}...")
                    break
            except:
                continue
        
        # Intentar con cada botón encontrado
        for button in elements_data['elements'].get('submit_buttons', []):
            try:
                elem = self.driver.find_element(By.XPATH, button['xpath'])
                if elem.is_displayed() and elem.is_enabled():
                    elem.click()
                    print(f"✅ Botón clickeado usando: {button['xpath'][:50]}...")
                    break
            except:
                continue
        
        # Esperar y verificar login
        print("\n⏳ Esperando resultado del login...")
        time.sleep(10)
        
        # Verificar si el login fue exitoso
        current_url = self.driver.current_url
        if "login" not in current_url.lower():
            print("✅ Login exitoso!")
            print(f"🔗 Redirigido a: {current_url}")
            
            # Tomar screenshot como evidencia
            self.driver.save_screenshot("login_exitoso.png")
            print("📸 Screenshot guardado: login_exitoso.png")
            
            # Guardar cookies de sesión
            cookies = self.driver.get_cookies()
            with open('session_cookies.json', 'w') as f:
                json.dump(cookies, f, indent=2)
            print("🍪 Cookies guardadas: session_cookies.json")
            
            return True
        else:
            print("❌ Login fallido o aún en página de login")
            self.driver.save_screenshot("login_fallido.png")
            return False
    
    def run(self):
        """Ejecuta el proceso completo"""
        EMAIL = "karrotdev@outlook.com"
        PASSWORD = "P4sc4g4z42025#*"
        
        try:
            success = self.smart_login(EMAIL, PASSWORD)
            
            if success:
                print("🚀 Yendo al panel de administración...")
                try:
                    panel_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Ir al panel de administración')]"))
                    )
                    panel_button.click()

                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Panel de control')]"))
                    )
                    print("✅ Panel de control cargado")
                    time.sleep(3)
                except Exception as e:
                    print(f"⚠️ No se pudo navegar al panel de control: {e}")

                print("\n🎉 Proceso completado exitosamente!")
                print("Puedes continuar con otras automatizaciones...")
                
                # Mantener abierto para revisión
                print("\n⏳ Sesión activa por 60 segundos...")
                time.sleep(60)
            else:
                print("\n⚠️ El login podría haber fallado. Revisa los screenshots.")
                
        except Exception as e:
            print(f"❌ Error durante el proceso: {e}")
            self.driver.save_screenshot("error.png")
        
        finally:
            print("\n👋 Cerrando navegador...")
            self.driver.quit()

# Ejecutar directamente
if __name__ == "__main__":
    auto_login = AutoLoginWithExtractor()
    auto_login.run()