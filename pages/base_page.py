from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver, wait_timeout=40):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, wait_timeout)

    def wait_for_element(self, locator):
        """Espera a que un elemento esté presente en el DOM y lo retorna."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def click_element(self, locator):
        """Espera a que un elemento sea clickeable y hace clic en él."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def input_text(self, locator, text):
        """Espera a que un elemento esté presente y le envía texto."""
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)
