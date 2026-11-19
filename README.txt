# PetStore API Automation

Automated tests for the public [Swagger PetStore](https://petstore.swagger.io) API with Python + Behave (Gherkin) + Allure.

## Prerequisites

- **Python 3.11 or newer** (check with `python --version`; on Windows you can also use `py --version`).
- **Git**, to clone the repository.
- **Internet access** to `https://petstore.swagger.io`. It is a public, shared server: it can occasionally
  be slow or fail even when the code is correct.
- **Optional:** Java and the Allure CLI, only needed to view the HTML report (see
  [View the Allure report](#view-the-allure-report)). The tests run without them.

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

### 1. Clone the repository

```bash
git clone https://github.com/odmarinm/PetStore.git
cd PetStore
```

### 2. Create the virtual environment and install the dependencies

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Create the `.env` file

Windows (PowerShell):

```powershell
copy .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

The default values work as they are, so nothing needs to be changed:

| Variable          | Required | Description                                                     |
|-------------------|----------|-----------------------------------------------------------------|
| `BASE_URL`        | Yes      | API base URL (default: `https://petstore.swagger.io/v2`)        |
| `API_KEY`         | No       | Value of the `api_key` header. Not needed for the `/user` tests |
| `REQUEST_TIMEOUT` | No       | Timeout for each request, in seconds (default: `30`)            |

## Run

Always run the commands from the project root folder (where `behave.ini` is).

Windows (PowerShell):

```powershell
.\.venv\Scripts\behave                       # everything
.\.venv\Scripts\behave --tags=@create_user   # a single family
```

macOS / Linux:

```bash
.venv/bin/behave                             # everything
.venv/bin/behave --tags=@create_user         # a single family
```

Available tags:

| Tag            | Runs                                       |
|----------------|--------------------------------------------|
| `@user`        | All the user features                      |
| `@create_user` | Create a user (`POST /user`)               |
| `@update_user` | Update a user (`PUT /user/{username}`)     |
| `@delete_user` | Delete a user (`DELETE /user/{username}`)  |

Allure results are stored in `reports/allure-results`. That folder is cleared
automatically at the start of each run (`features/environment.py`), so the report
only shows the latest execution. When the run finishes, if the Allure CLI is on the PATH,
the HTML report is regenerated automatically in `reports/allure-report`. If it is not
installed, the tests still run and only a notice is printed.

## View the Allure report

Requires Java (8 or newer) and the Allure CLI (2.x).

Windows:

```powershell
winget install --id EclipseAdoptium.Temurin.21.JDK --exact
scoop install allure        # requires Scoop: https://scoop.sh
```

macOS:

```bash
brew install allure         # also installs Java
```

Linux, or without a package manager: download `allure-<version>.zip` from
https://github.com/allure-framework/allure2/releases, unzip it and add its `bin` folder to the PATH.

Check the installation with `allure --version` (open a new terminal after installing). Then:

```bash
allure open reports/allure-report      # opens the HTML of the latest run (generated automatically)
allure serve reports/allure-results    # alternative: builds a temporary report and opens it
```
