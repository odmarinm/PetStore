import platform
import shutil
import sys
from pathlib import Path

# Permite importar el paquete "src" desde la raíz del proyecto.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.settings import get_settings  # noqa: E402

ALLURE_RESULTS_DIR = ROOT_DIR / "reports" / "allure-results"


def _clean_allure_results() -> None:
    """Vacía los resultados de corridas anteriores para que el reporte muestre solo esta ejecución.

    Se borra el contenido y no la carpeta, porque el formatter de Allure ya la creó y la está usando.
    """
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for item in ALLURE_RESULTS_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def _write_allure_environment(settings) -> None:
    """Datos que Allure muestra en el widget 'Environment' del reporte."""
    properties = {
        "Base.URL": settings.base_url,
        "Python": platform.python_version(),
        "OS": f"{platform.system()} {platform.release()}",
    }
    content = "\n".join(f"{key}={value}" for key, value in properties.items())
    (ALLURE_RESULTS_DIR / "environment.properties").write_text(content + "\n", encoding="utf-8")


def before_all(context):
    context.settings = get_settings()
    _clean_allure_results()
    _write_allure_environment(context.settings)


def before_scenario(context, scenario):
    context.payload = None
    context.response = None
