import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pages.base_page import BasePage

class RegistroPage(BasePage):
    # Selectores (Locators)
    COMPANY_NAME_INPUT = (By.ID, "register-form_companyName")
    NAME_INPUT = (By.ID, "register-form_name")
    LAST_NAME_INPUT = (By.ID, "register-form_lastName")
    COUNTRY_SELECTOR = (By.ID, "register-form_mainCountry")
    STORE_NUMBER_INPUT = (By.ID, "register-form_storeNumber")
    EMAIL_INPUT = (By.ID, "register-form_email")
    PHONE_NUMBER_INPUT = (By.ID, "register-form_phoneNumber")
    PASSWORD_INPUT = (By.ID, "register-form_password")

    def __init__(self, driver):
        super().__init__(driver)

    def go_to_registro(self, url="https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/register/es"):
        self.driver.get(url)

    def select_country(self, country_name="Colombia"):
        """Intenta seleccionar el país manejando el dropdown de Ant Design."""
        try:
            # Click para abrir el dropdown
            country_element = self.wait_for_element(self.COUNTRY_SELECTOR)
            country_element.click()
            time.sleep(2)
            
            # Seleccionar opción (Método 1 o 2 por xpath)
            try:
                option = self.driver.find_element(By.XPATH, f"//div[contains(@class, 'ant-select-item') and contains(., '{country_name}')]")
                option.click()
                return True
            except:
                option = self.driver.find_element(By.XPATH, f"//div[contains(@class, 'ant-select-item-option') and @title='{country_name}']")
                option.click()
                return True
        except Exception:
            # Fallback 1: Teclado
            try:
                country_element = self.driver.find_element(*self.COUNTRY_SELECTOR)
                country_element.clear()
                country_element.send_keys(country_name)
                time.sleep(1)
                country_element.send_keys(Keys.ENTER)
                return True
            except Exception:
                # Fallback 2: Javascript
                try:
                    self.driver.execute_script(f"""
                        var element = document.getElementById('register-form_mainCountry');
                        element.value = '{country_name}';
                        var event = new Event('change', {{ bubbles: true }});
                        element.dispatchEvent(event);
                    """)
                    return True
                except Exception as e:
                    raise Exception(f"No se pudo seleccionar el país: {str(e)}")

    def fill_registration_form(self, company, name, last_name, country, stores, email, phone, password):
        self.input_text(self.COMPANY_NAME_INPUT, company)
        self.input_text(self.NAME_INPUT, name)
        self.input_text(self.LAST_NAME_INPUT, last_name)
        
        self.select_country(country)
        
        self.input_text(self.STORE_NUMBER_INPUT, str(stores))
        self.input_text(self.EMAIL_INPUT, email)
        self.input_text(self.PHONE_NUMBER_INPUT, phone)
        self.input_text(self.PASSWORD_INPUT, password)
