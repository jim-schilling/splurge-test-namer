# Details — splurge-test-namer

This document describes features, APIs, errors, and usage of the splurge-test-namer tool.

Features
--------
- Rename test modules based on module-level sentinel lists (default sentinel: `DOMAINS`).
- Optional import-following mode: when provided a `root_import` (e.g. `splurge_sql_tool`) and `repo_root`, the tool scans test files for imports that begin with the `root_import`, resolves those module names to files inside `repo_root`, reads their sentinel lists, aggregates them, and uses the aggregated set to form the test filename prefix.
- Deterministic naming and sequence assignment.
- Dry-run mode by default; `--apply` performs actual rename operations.
- `--verbose` flag enables debug logging.

APIs / Functions
----------------
- parser.find_imports_in_file(path: Path, root_import: str) -> set[str]
  - Parse AST for `Import` and `ImportFrom` nodes and return imports beginning with `root_import`.

- util_helpers.resolve_module_to_paths(module_name: str, repo_root: Path) -> list[Path]
  - Resolve dotted module names to candidate file paths (module.py and package/__init__.py) inside repo_root.

- parser.aggregate_sentinels_for_test(test_path: Path, root_import: str, repo_root: Path, sentinel_name: str = 'DOMAINS') -> list[str]
  - Aggregate sentinel lists from resolved modules imported by a test file and return a sorted unique list.

- namer.build_proposals(root: Path, sentinel: str = 'DOMAINS', root_import: str | None = None, repo_root: Path | None = None) -> list[tuple[Path, Path]]
  - Build rename proposals; use import-following aggregation when `root_import` and `repo_root` are provided.

Errors and Logging
------------------
- Custom exceptions are defined in `splurge_test_namer.exceptions` (e.g., `FileReadError`, `FileRenameError`, `SentinelReadError`, `SplurgeTestNamerError`).
- Unresolvable imports or missing modules emit debug/info logs and do not abort the run.
- Use `--verbose` to enable debug logging.

CLI
---
- `--root`: tests root to scan (default: `tests`)
- `--apply`: apply renames (default: dry-run)
- `--sentinel`: sentinel variable name (default: `DOMAINS`)
- `--root-import`: root import package to follow (optional)
- `--repo-root`: filesystem path to repository root for resolving imports (optional)
- `-v/--verbose`: enable verbose debug logging

Notes
-----
- The tool only resolves modules within `repo_root`. External packages (site-packages) are ignored.
- Dynamic or runtime imports are out-of-scope.

Developer setup
---------------
To set up a local development environment and enable pre-commit hooks, create and activate a virtual environment, install the project in editable mode with dev dependencies, then install pre-commit hooks. Use the commands below that match your shell/platform.

Windows (PowerShell):

```powershell
python -m venv .venv
# Activate the venv in PowerShell
& .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

Windows (Git Bash / bash) or WSL:

```bash
python -m venv .venv
# Activate the venv in bash-style shells on Windows (Git Bash) or in WSL
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

After this, commits will run configured checks (ruff, mypy, pytest) on changed files. You can run the full pre-commit suite locally with:

```bash
pre-commit run --all-files
```

If you prefer to install from the pinned `requirements-dev.txt` instead of extras, install it with:

```bash
pip install -r requirements-dev.txt
```

Force/overwrite behavior
------------------------
By default the renamer will not overwrite existing files when applying proposals. To allow overwrites (for example when you intentionally want to replace files), run with the `--force` flag together with `--apply`:

```bash
python -m splurge_test_namer.cli --root tests --apply --force
```
+

Pre-commit hooks
---------------
To install and verify pre-commit hooks (if not already installed by the editable install), run:

```bash
# Install pre-commit into the active environment
pip install pre-commit
+
# Install hooks into your Git repository
pre-commit install
+
# Optionally run the hooks against all files to validate configuration
pre-commit run --all-files
```
+



