import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pages.base_page import BasePage

class SedesPage(BasePage):
    # Locators
    LOCATIONS_MENU = (By.XPATH, "//span[contains(text(), 'Ubicaciones')] | //div[contains(text(), 'Ubicaciones')] | //li[contains(., 'Ubicaciones')]")
    NAME_INPUT = (By.ID, "advanced_search_name")
    TYPE_DROPDOWN = (By.CSS_SELECTOR, "form#advanced_search div:nth-of-type(2) .ant-select-selector")
    DROPDOWN_OPTIONS = (By.CSS_SELECTOR, ".ant-select-dropdown .ant-select-item-option")
    ADDRESS_INPUT = (By.ID, "advanced_search_address")
    # Este XPath es muy frágil en el script original, pero lo mantenemos para conservar funcionalidad
    USER_DROPDOWN = (By.XPATH, "//*[@id='advanced_search']/div[2]/div/div[1]/div/div/div/div/div[1]/div/div[6]/div[1]/div[2]/div[1]/div/div/div/div")
    ADD_BUTTON = (By.XPATH, "//*[@id='advanced_search']/div[1]/div/div/div/button[2]")

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_add_location(self):
        """Navega a la pantalla de agregar ubicación"""
        # Método directo usado en TC012
        url_agregar = "https://devtwo.do5o1l1ov8f4a.amplifyapp.com/app/locations/add-locations"
        self.driver.get(url_agregar)
        time.sleep(5)

    def fill_location_form(self, nombre, direccion):
        """Llena el formulario para crear una sede"""
        # Nombre
        self.input_text(self.NAME_INPUT, nombre)

        # Tipo de Tienda (dropdown)
        tipo_tienda = self.wait_for_element(self.TYPE_DROPDOWN)
        tipo_tienda.click()
        time.sleep(2)
        
        opciones = self.wait.until(
            lambda d: d.find_elements(*self.DROPDOWN_OPTIONS)
        )
        for opcion in opciones:
            if opcion.text.strip() == "Tienda":
                opcion.click()
                break
        time.sleep(2)

        # Dirección
        self.input_text(self.ADDRESS_INPUT, direccion)
        ActionChains(self.driver).move_by_offset(0, 0).click().perform()
        time.sleep(3) # Reducido un poco del original 15s

        # Bajar scroll
        self.driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)

        # Asignar usuario (dropdown)
        tipo_usuario = self.wait_for_element(self.USER_DROPDOWN)
        tipo_usuario.click()
        time.sleep(3)
        
        opciones_usuarios = self.wait.until(
            lambda d: d.find_elements(*self.DROPDOWN_OPTIONS)
        )
        # Selecciona el primer usuario de la lista como en el script original
        if opciones_usuarios:
            opciones_usuarios[0].click()
        time.sleep(2)

    def submit_form(self):
        """Hace scroll al botón Añadir y lo clickea"""
        boton_anadir = self.wait_for_element(self.ADD_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_anadir)
        time.sleep(2)
        boton_anadir.click()
        time.sleep(8)
