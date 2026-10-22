import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage

class InventarioPage(BasePage):
    # Locators Menú
    CATALOGO_MENU = (By.XPATH, "//*[contains(text(), 'Catálogo') or normalize-space()='Catálogo']")
    PRODUCTOS_SUBMENU = (By.XPATH, "//*[contains(text(), 'Productos y Servicios') or normalize-space()='Productos y Servicios']")
    # Hacemos el locator de agregar más genérico buscando el botón por texto o ícono si es posible, 
    # pero mantenemos el original como fallback
    AGREGAR_ARTICULO_BTN = (By.XPATH, "//button[contains(., 'Agregar') or contains(., 'Añadir')] | //*[@id='root']/div/section/section/section/div/main/div[2]/div[2]/div/div/div/div[1]/div/button[1]")
    
    # Locators Formulario Producto
    NAME_INPUT = (By.ID, "advanced_search_name")
    CATEGORY_DROPDOWN = (By.ID, "advanced_search_category")
    UNIT_GROUP_DROPDOWN = (By.ID, "advanced_search_unitGroup")
    DESC_INPUT = (By.ID, "advanced_search_description")
    PERECEDERO_SWITCH = (By.XPATH, "//button[@role='switch' and contains(@class, 'ant-switch')]")
    SUBMIT_BTN = (By.XPATH, "//button[@type='submit' and contains(@class, 'ant-btn-primary')]")
    
    # Locators Búsqueda
    BUSCAR_POR_DROPDOWN = (By.XPATH, "//div[contains(@class, 'ant-select') and (span[contains(@title, 'Buscar por')] or .//span[contains(text(), 'Buscar por')])]")
    BUSCAR_POR_DROPDOWN_FALLBACK = (By.XPATH, "//div[contains(@class, 'ant-select') and .//input[@type='search']]")
    SEARCH_INPUT = (By.XPATH, "//input[@role='combobox' and @type='search' and contains(@class, 'ant-input')]")

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_add_product(self):
        """Navega desde el menú hasta el formulario de Agregar Artículo"""
        time.sleep(5)  # Esperar a que la animación del login/dashboard termine
        self.click_element(self.CATALOGO_MENU)
        time.sleep(2)
        self.click_element(self.PRODUCTOS_SUBMENU)
        time.sleep(5)
        self.click_element(self.AGREGAR_ARTICULO_BTN)
        time.sleep(3)

    def select_product_type(self, tipo_producto="Kit to stock"):
        """Selecciona la tarjeta del tipo de producto"""
        card_xpath = f"//div[@role='button' and .//div[text()='{tipo_producto}']]"
        card = self.wait_for_element((By.XPATH, card_xpath))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(0.5)
        card.click()

    def fill_basic_info(self, nombre, descripcion):
        """Llena los campos básicos del producto"""
        self.input_text(self.NAME_INPUT, nombre)
        
        # Categoría (Selecciona la primera disponible)
        cat_element = self.wait_for_element(self.CATEGORY_DROPDOWN)
        ActionChains(self.driver).move_to_element(cat_element).click().perform()
        time.sleep(1)
        opciones = self.wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//*[text()]"))
        for op in opciones:
            if op.text.strip():
                op.click()
                break
        
        # Grupo de Unidad (Selecciona Cantidad / Unidades)
        unit_group = self.wait_for_element(self.UNIT_GROUP_DROPDOWN)
        ActionChains(self.driver).move_to_element(unit_group).click().perform()
        time.sleep(1)
        opciones_unidad = self.wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-option-content')]"))
        for op in opciones_unidad:
            if op.text.strip() == "Cantidad / Unidades":
                op.click()
                break
        
        # Segunda unidad (Unidad (u))
        time.sleep(1)
        inputs = self.driver.find_elements(By.CLASS_NAME, "ant-select-selection-search-input")
        if inputs:
            index = 2 if len(inputs) > 2 else len(inputs) - 1
            inputs[index].click()
            time.sleep(1)
            opciones_unidad_2 = self.wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(@class, 'ant-select-dropdown')]//div[contains(@class, 'ant-select-item-option-content')]"))
            for op in opciones_unidad_2:
                if op.text.strip() == "Unidad (u)":
                    op.click()
                    break

        self.input_text(self.DESC_INPUT, descripcion)

    def set_perecedero(self, es_perecedero: bool):
        """Activa o desactiva el switch de producto perecedero"""
        switch_btn = self.wait_for_element(self.PERECEDERO_SWITCH)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch_btn)
        time.sleep(0.5)
        is_checked = switch_btn.get_attribute("aria-checked") == "true"
        if (es_perecedero and not is_checked) or (not es_perecedero and is_checked):
            switch_btn.click()

    def fill_single_variant(self, sku, barcode, cost, price):
        """Llena los campos para un producto sin atributos dinámicos"""
        self.input_text((By.ID, "advanced_search_undefinedsku"), sku)
        self.input_text((By.ID, "advanced_search_undefinedbarcode"), barcode)
        self.input_text((By.ID, "advanced_search_undefinedcost"), str(cost))
        self.input_text((By.ID, "advanced_search_undefinedprice"), str(price))

    def submit_product(self):
        """Hace clic en el botón añadir y espera que desaparezca cualquier toast"""
        btn = self.wait_for_element(self.SUBMIT_BTN)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(1)
        btn.click()
        # Esperar por el toast de éxito
        time.sleep(5)

    def search_by_barcode(self, barcode):
        """Busca el producto recién creado en la tabla usando su código de barras"""
        self.driver.refresh()
        time.sleep(5)
        
        try:
            select_element = self.wait_for_element(self.BUSCAR_POR_DROPDOWN)
        except TimeoutException:
            select_element = self.wait_for_element(self.BUSCAR_POR_DROPDOWN_FALLBACK)
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_element)
        self.driver.execute_script("arguments[0].click();", select_element)
        time.sleep(1)
        
        opciones_dropdown = self.wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(@class,'ant-select-dropdown') and not(contains(@class, 'ant-select-dropdown-hidden'))]//div[contains(@class,'ant-select-item-option-content')]"))
        for op in opciones_dropdown:
            if "código de barras" in op.text.strip().lower() or "codigo de barras" in op.text.strip().lower():
                op.click()
                break
        
        time.sleep(2)
        search_field = self.wait_for_element(self.SEARCH_INPUT)
        search_field.clear()
        search_field.send_keys(barcode)
        time.sleep(3) # Esperar a que la tabla filtre
