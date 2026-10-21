# ⚙️ Installation Guide

> Tested on **Python 3.11+** (recommended: 3.12).  
> Follow the steps below to set up, run, and test the project on any OS.

---

## 🧩 Setup

### 🪟 Windows (PowerShell)
```powershell
# 1️⃣ Clone the repository
git clone https://github.com/rdpatel2/Weeklies.git
cd Weeklies

# 2️⃣ Create and activate a virtual environment
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
# If activation is blocked:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3️⃣ Install dependencies
python -m pip install --upgrade pip
pip install -r proj2/requirements.txt
```

### 🐧 MacOS / Linux (Bash/Zsh)
```bash
# 1️⃣ Clone the repository
git clone https://github.com/rdpatel2/Weeklies.git
cd Weeklies

# 2️⃣ Create & activate a venv
python3 -m venv .venv
source .venv/bin/activate

# 3️⃣ Install packages
python -m pip install --upgrade pip
pip install -r proj2/requirements.txt
```

---

## 🚀 Usage

### Configuration
The app reads its settings from environment variables. `flask run` loads them from a `.env` file in the repo root, which git ignores:

```bash
cp .env.example .env
# then set WEEKLIES_SECRET_KEY in .env to the output of:
python -c "import secrets; print(secrets.token_hex(32))"
```

| Variable | Purpose | If unset |
|---|---|---|
| `WEEKLIES_SECRET_KEY` | Signs session cookies. Never commit a real value. | A random key is generated at startup, so logins reset whenever the server restarts. |
| `FLASK_DEBUG` | `1` enables auto-reload and the interactive debugger for local development. | Debug is off. |

When starting the app directly with `python -m proj2.Flask_app`, debug mode is off unless you pass `--debug`. Never enable it on a server others can reach: the debugger lets anyone who sees an error page run code on the machine.

### Running the Application
Once dependencies are installed and the virtual environment is activated, you can run the Flask server:

```bash
# Start the development server
flask run
```

The application will be available at `http://127.0.0.1:5000`.

> [!NOTE]
> If you have downloaded the repo locally and you're running into issues with
> `proj2.` errors when trying to run `Flask_app.py`, simply remove `proj2.`
> that is in front of any of the imports and try to run the application again.

---

## 🧪 Running Tests

### Python Tests (pytest)
Execute the test suite using pytest:
```bash
# Run all tests with verbose output
pytest -v

# Run with quiet output (dots for passes, F for failures)
pytest -q

# Run a specific test category
pytest proj2/tests/unit/ -v
pytest proj2/tests/integration/ -v
pytest proj2/tests/e2e/ -v
```

### Cypress E2E Tests
Cypress tests require Node.js (v18+) and a running Flask server:

```bash
# Install Cypress (one-time setup)
cd proj2
npm install

# Run Cypress tests headlessly
npx cypress run

# Open Cypress interactive runner
npx cypress open
```

> [!NOTE]
> Cypress tests expect the Flask server to be running on `http://127.0.0.1:5000`.
> Start the server in a separate terminal before running Cypress.

---

## 📚 Documentation

### _Documentation is generated using pdoc._
Documentation is automatically generated using pdoc and deployed to GitHub Pages whenever new changes are merged into the `main` branch.

### 🧩 Automated Docs
* CI/CD workflow (`docs.yml`) builds and publishes docs from `proj2/` to the `gh-pages` branch.
* Live documentation becomes available at the GitHub Pages link after each successful merge.
* Source code is hidden; only public functions, classes, and docstrings are shown.

### 🖥️ Build Docs Locally

#### 🪟 Windows (PowerShell)
```powershell
# Temporarily add current directory to Python path
$env:PYTHONPATH="." ;
pdoc proj2 --no-show-source --template-dir proj2\pdoc_templates -o proj2\site
python .\scripts\build_docs.py
# View the documentation in your default browser
start proj2\site\index.html
```

#### 🐧 MacOS / Linux (Bash/Zsh)
```bash
# Temporarily add current directory to Python path
export PYTHONPATH="."
pdoc proj2 --no-show-source --template-dir proj2/pdoc_templates -o proj2/site
python ./scripts/build_docs.py
# View the documentation in your default browser
open proj2/site/index.html
```

The generated HTML files will be available in the `proj2/site` directory.
