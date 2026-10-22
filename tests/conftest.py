import pytest
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Asegurar que la raíz del proyecto esté en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.google_sheets import GoogleSheetsClient
from utils.logger import Logger

# Cargar variables de entorno globalmente
load_dotenv()

@pytest.fixture(scope="session")
def gs_client():
    """Fixture de sesión para reutilizar la conexión a Google Sheets."""
    client = GoogleSheetsClient()
    yield client

@pytest.fixture(scope="function")
def driver():
    """Fixture de función para inicializar y cerrar el WebDriver por cada test."""
    chrome_options = Options()
    if os.getenv("JENKINS_URL") or os.getenv("CI") or os.getenv("HEADLESS") == "true":
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
    
    _driver = webdriver.Chrome(options=chrome_options)
    _driver.maximize_window()
    
    yield _driver
    
    # Teardown: cerrar el navegador después de que termine el test
    _driver.quit()

@pytest.fixture(autouse=True)
def setup_logging(request):
    """Fixture automático para configurar el logger por cada test."""
    test_name = request.node.name
    Logger.setup_logger(test_name)

# ==========================================
# CONFIGURACIÓN DEL REPORTE HTML DE PYTEST
# ==========================================
def pytest_html_report_title(report):
    """Cambia el título del reporte HTML."""
    report.title = "Karrot - Reporte de Automatización QA"

def pytest_html_results_summary(prefix, summary, postfix):
    """Agrega un encabezado personalizado al reporte."""
    prefix.extend([
        "<h2 style='color: #00e676;'>🚀 Plataforma impulsada por IA para Retail</h2>",
        "<p style='color: #e0e0e0;'>Reporte de ejecución de pruebas automatizadas E2E. Revisa los detalles de cada módulo a continuación.</p>"
    ])
