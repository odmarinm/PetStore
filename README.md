# PetStore API Automation

Automatización de la API pública [Swagger PetStore](https://petstore.swagger.io) con Python + Behave (Gherkin) + Allure.

## Estructura

```
features/                 Archivos .feature (Gherkin), agrupados por recurso
  user/create_user.feature
  user/update_user.feature
  user/delete_user.feature
  steps/                  Steps: Given arma datos, When ejecuta y guarda, Then valida
  environment.py          Hooks de Behave
src/
  config/settings.py      Lee el archivo .env
  enums/                  Endpoint, ContentType, ApiResponseType
  builders/               Construyen payloads (NUNCA hacen HTTP)
  interactors/            Casos de uso que usan los steps
  requests/               ÚNICA capa que hace llamadas HTTP
  validators/             Validaciones de responses (sin HTTP)
  schemas/                JSON Schemas de los responses
  utils/
```

Regla de capas: `features → steps → interactors → requests`. Solo `src/requests` hace HTTP.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # y completa los valores
```

## Ejecutar

```powershell
.\.venv\Scripts\behave                       # todo
.\.venv\Scripts\behave --tags=@create_user   # una familia
```

Los resultados de Allure quedan en `reports/allure-results`. Esa carpeta se vacía
automáticamente al inicio de cada corrida (`features/environment.py`), así el reporte
muestra solo la última ejecución. Al terminar, si el Allure CLI está en el PATH, el HTML se
regenera solo en `reports/allure-report`.

## Ver el reporte de Allure

Requiere Java y el Allure CLI:

```powershell
winget install --id EclipseAdoptium.Temurin.21.JDK --exact
# Allure CLI: descargar allure-<versión>.zip de
# https://github.com/allure-framework/allure2/releases, descomprimir y agregar su carpeta bin al PATH
```

```powershell
allure open reports/allure-report      # abre el HTML de la última ejecución (se genera solo)
allure serve reports/allure-results    # alternativa: genera un reporte temporal y lo abre
```
