# splurge-test-namer

A small tool to rename test modules based on module-level sentinel lists (e.g. `DOMAINS = ['core','utils']`).

<!-- Badges: Block 1 - version / pypi / license -->

[![package version](https://img.shields.io/badge/version-2025.0.0-blue.svg)](d:/repos/splurge-test-namer/pyproject.toml)
[![PyPI version](https://img.shields.io/pypi/v/splurge-test-namer.svg)](https://pypi.org/project/splurge-test-namer)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<!-- Badges: Block 2 - python versions / CI pass-fail / coverage -->

[![Python 3.10](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.10.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.10.yml) [![Python 3.11](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.11.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.11.yml)
[![Python 3.12](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.12.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.12.yml) [![Python 3.13](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.13.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.13.yml)
[![CI status](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/python-ci.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/python-ci.yml) [![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/jim-schilling/splurge-test-namer/main/.github/badges/coverage.json)](https://github.com/jim-schilling/splurge-test-namer/actions)

<!-- Badges: Block 3 - linters -->

[![ruff](https://img.shields.io/badge/ruff-passed-brightgreen.svg)](https://github.com/jim-schilling/splurge-test-namer/actions)
[![mypy](https://img.shields.io/badge/mypy-passed-brightgreen.svg)](https://github.com/jim-schilling/splurge-test-namer/actions)

Usage
-----
-- Dry run: `python -m splurge_test_namer.cli --test-root tests`
-- Apply renames: `python -m splurge_test_namer.cli --test-root tests --apply`
-- Follow imports under a root package: `python -m splurge_test_namer.cli --test-root tests --import-root splurge_sql_tool --repo-root /path/to/repo`

Force/overwrite behavior
------------------------
By default the tool will not overwrite existing files. To allow overwriting targets when applying proposals, pass `--force` together with `--apply`:

```bash
python -m splurge_test_namer.cli --test-root tests --apply --force
```
+

Running tests locally
---------------------
The test suite expects the package to be importable. The recommended workflow is to create and activate a virtual environment, install the package in editable mode with development dependencies, then run pytest. Example commands for common shells on Windows and Unix-like systems:

Windows (PowerShell):

```powershell
python -m venv .venv
# Activate the venv in PowerShell
+& .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest -q
```

Windows (Git Bash / bash or WSL):

```bash
python -m venv .venv
# Activate the venv in bash-style shells
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest -q
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest -q
```

Notes:
- Use the PowerShell activation in PowerShell. Use the `source .venv/Scripts/activate` command in Git Bash on Windows. On macOS/Linux the activation script lives at `.venv/bin/activate`.
- If you prefer not to install the package, you can run tests with `PYTHONPATH=. pytest -q` as a short-term workaround, though installing in editable mode is recommended.

Pre-commit hooks
---------------
We use `pre-commit` to run linters and checks on each commit. After installing dev dependencies, install the hooks and verify them with the commands below:

```bash
# Install pre-commit if not already installed (inside the venv)
pip install pre-commit
+
# Install hooks into your Git hooks
pre-commit install
+
# Run hooks against all files to verify configuration
pre-commit run --all-files
```
+
+
New in 2025.0.0
---------------
- Import-following mode: aggregate sentinels from imported modules under a root package when proposing test filenames.
-- CLI flags: `--import-root`, `--repo-root`, `--verbose`.
+
See `docs/README-DETAILS.md` for full API and design notes.
