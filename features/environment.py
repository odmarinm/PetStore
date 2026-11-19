import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Allows importing the "src" package from the project root.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.settings import get_settings  # noqa: E402

ALLURE_RESULTS_DIR = ROOT_DIR / "reports" / "allure-results"
ALLURE_REPORT_DIR = ROOT_DIR / "reports" / "allure-report"


def _clean_allure_results() -> None:
    """Clear results from previous runs so the report only shows this execution.

    The contents are deleted, not the folder, because the Allure formatter already created it and is using it.
    """
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for item in ALLURE_RESULTS_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def _write_allure_environment(settings) -> None:
    """Data shown by Allure in the report's 'Environment' widget."""
    properties = {
        "Base.URL": settings.base_url,
        "Python": platform.python_version(),
        "OS": f"{platform.system()} {platform.release()}",
    }
    content = "\n".join(f"{key}={value}" for key, value in properties.items())
    (ALLURE_RESULTS_DIR / "environment.properties").write_text(content + "\n", encoding="utf-8")


def _console(message: str) -> None:
    """Print straight to the console: behave captures stdout inside hooks."""
    print(message, file=sys.__stdout__, flush=True)


def _allure_enabled(context) -> bool:
    """True when the Allure formatter is active (it is not when running e.g. with -f plain)."""
    return any("allure" in fmt.lower() for fmt in context.config.format or [])


def _generate_allure_report() -> None:
    """Regenerate the HTML report so `allure open` always shows the latest run.

    Allure writes each feature's results when the feature ends, so they are complete by after_all.
    Requires the Allure CLI on PATH; if it is missing, the run is not affected.
    """
    allure_cli = shutil.which("allure")
    if not allure_cli:
        _console("\nAllure CLI not found on PATH: HTML report not generated.")
        return
    result = subprocess.run(
        [allure_cli, "generate", str(ALLURE_RESULTS_DIR), "-o", str(ALLURE_REPORT_DIR), "--clean"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        _console(f"\nAllure report generated: {ALLURE_REPORT_DIR}")
    else:
        _console(f"\nAllure report could not be generated:\n{result.stdout}{result.stderr}")


def before_all(context):
    context.settings = get_settings()
    if _allure_enabled(context):
        _clean_allure_results()
        _write_allure_environment(context.settings)


def after_all(context):
    if _allure_enabled(context):
        _generate_allure_report()


def before_scenario(context, scenario):
    context.payload = None
    context.response = None
