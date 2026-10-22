from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    # Selectores (Locators)
    EMAIL_INPUT = (By.ID, "login-form_email")
    PASSWORD_INPUT = (By.ID, "login-form_password")
    LOGIN_BUTTON = (By.XPATH, "//*[@id='login-form']/div[3]/div/div/div/div/button")
    SUCCESS_MESSAGE = (By.XPATH, "//*[contains(text(), 'Panel de control')]")

    def __init__(self, driver):
        super().__init__(driver)

    def go_to_login(self, url="https://devtwo.do5o1l1ov8f4a.amplifyapp.com/auth/login"):
        self.driver.get(url)

    def login(self, email, password):
        self.input_text(self.EMAIL_INPUT, email)
        self.input_text(self.PASSWORD_INPUT, password)
        self.click_element(self.LOGIN_BUTTON)

    def verify_successful_login(self):
        """Verifica que aparezca el mensaje de éxito tras iniciar sesión."""
        return self.wait_for_element(self.SUCCESS_MESSAGE)
