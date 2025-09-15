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
- Dry run: `python -m splurge_test_namer.cli --root tests`
- Apply renames: `python -m splurge_test_namer.cli --root tests --apply`
- Follow imports under a root package: `python -m splurge_test_namer.cli --root tests --root-import splurge_sql_tool --repo-root /path/to/repo`

New in 2025.0.0
---------------
- Import-following mode: aggregate sentinels from imported modules under a root package when proposing test filenames.
- CLI flags: `--root-import`, `--repo-root`, `--verbose`.

See `docs/README-DETAILS.md` for full API and design notes.
