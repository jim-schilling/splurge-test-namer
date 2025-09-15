# splurge-test-namer

A small tool to rename test modules based on module-level sentinel lists (e.g. `DOMAINS = ['core','utils']`).

[![3.10](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.10.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.10.yml)
[![3.11](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.11.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.11.yml)
[![3.12](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.12.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.12.yml)
[![3.13](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.13.yml/badge.svg)](https://github.com/jim-schilling/splurge-test-namer/actions/workflows/ci-py-3.13.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ruff](https://img.shields.io/badge/ruff-checks-green.svg)](https://github.com/jim-schilling/splurge-test-namer/actions)
[![mypy](https://img.shields.io/badge/mypy-passed-brightgreen.svg)](https://github.com/jim-schilling/splurge-test-namer/actions)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/jim-schilling/splurge-test-namer/main/.github/badges/coverage.json)](https://github.com/jim-schilling/splurge-test-namer/actions)
[![PyPI version](https://img.shields.io/pypi/v/splurge-test-namer.svg)](https://pypi.org/project/splurge-test-namer)

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
