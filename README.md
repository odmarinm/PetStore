# PetStore API Automation

Automated tests for the public [Swagger PetStore](https://petstore.swagger.io) API with Python + Behave (Gherkin) + Allure.

## Structure

```
features/                 .feature files (Gherkin), grouped by resource
  user/create_user.feature
  user/update_user.feature
  user/delete_user.feature
  steps/                  Steps: Given builds data, When sends and stores, Then validates
  environment.py          Behave hooks
src/
  config/settings.py      Reads the .env file
  enums/                  Endpoint, ContentType, ApiResponseType
  builders/               Build payloads (NEVER make HTTP calls)
  interactors/            Use cases called by the steps
  requests/               The ONLY layer that makes HTTP calls
  validators/             Response validations (no HTTP)
  schemas/                JSON Schemas of the responses
  utils/
```

Layer rule: `features → steps → interactors → requests`. Only `src/requests` makes HTTP calls.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # then fill in the values
```

## Run

```powershell
.\.venv\Scripts\behave                       # everything
.\.venv\Scripts\behave --tags=@create_user   # a single family
```

Allure results are stored in `reports/allure-results`. That folder is cleared
automatically at the start of each run (`features/environment.py`), so the report
only shows the latest execution. When the run finishes, if the Allure CLI is on the PATH,
the HTML report is regenerated automatically in `reports/allure-report`.

## View the Allure report

Requires Java and the Allure CLI:

```powershell
winget install --id EclipseAdoptium.Temurin.21.JDK --exact
# Allure CLI: download allure-<version>.zip from
# https://github.com/allure-framework/allure2/releases, unzip it and add its bin folder to the PATH
```

```powershell
allure open reports/allure-report      # opens the HTML of the latest run (generated automatically)
allure serve reports/allure-results    # alternative: builds a temporary report and opens it
```
