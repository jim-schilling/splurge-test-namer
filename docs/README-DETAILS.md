# Details — splurge-test-namer

This document describes features, APIs, errors, and usage of the splurge-test-namer tool.

Features
--------
- Rename test modules based on module-level sentinel lists (default sentinel: `DOMAINS`).
- Optional import-following mode: when provided a `root_import` (e.g. `splurge_sql_tool`) and `repo_root`, the tool scans test files for imports that begin with the `root_import`, resolves those module names to files inside `repo_root`, reads their sentinel lists, aggregates them, and uses the aggregated set to form the test filename prefix.
- Deterministic naming and sequence assignment.
- Dry-run mode by default; `--apply` performs actual rename operations.
- `--verbose` flag enables debug logging.
 - `--prefix` and `--fallback` flags let you control the generated filename prefix and the fallback domain used when no sentinel is found.

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
  - New optional args: `prefix`, `fallback`, and `excludes` allow finer control of generated names and scanning behavior.

Errors and Logging
------------------
- Custom exceptions are defined in `splurge_test_namer.exceptions` (e.g., `FileReadError`, `FileRenameError`, `SentinelReadError`, `SplurgeTestNamerError`).
- Unresolvable imports or missing modules emit debug/info logs and do not abort the run.
- Use `--verbose` to enable debug logging.

CLI
---
-- `--test-root`: tests root to scan (default: `tests`)
- `--apply`: apply renames (default: dry-run)
- `--sentinel`: sentinel variable name (default: `DOMAINS`)
-- `--import-root`: import-root package to follow (optional)
- `--repo-root`: filesystem path to repository root for resolving imports (optional)
- `-v/--verbose`: enable verbose debug logging

Notes
-----
- The tool only resolves modules within `repo_root`. External packages (site-packages) are ignored.
Pre-commit hooks
---------------
The repository uses local, Python-based pre-commit hooks that instruct pre-commit to create isolated venvs and pip-install the required tools from PyPI. This avoids cloning remote mirror repos while keeping hooks reproducible. The hooks are pinned to these versions (also reflected in `requirements-dev.txt`):

- ruff==0.13.0
- mypy==1.10.0
- pytest==8.2.2
- pytest-cov==4.0.0
- pytest-mock==3.11.0

Recommended developer workflow:

1. Create and activate a virtual environment and install dev dependencies (optional if you rely solely on pre-commit-created venvs):

```bash
python -m venv .venv
source .venv/bin/activate   # or `& .venv\Scripts\Activate.ps1` on PowerShell
pip install -e ".[dev]"    # or `pip install -r requirements-dev.txt` to use pinned versions
```

2. Install pre-commit into your active environment and install the repository hooks (this step is optional if you rely on pre-commit's per-hook venv creation):

```bash
pip install pre-commit
pre-commit install
```

3. To validate hooks across the repository (this will create per-hook venvs and pip-install pinned packages):

```bash
pre-commit run --all-files
```

Notes:

- If you prefer to rely on the project's `.venv` (language: system hooks) instead of per-hook venvs, switch `language` to `system` in `.pre-commit-config.yaml` and ensure the dev tools are installed in that environment.
- The current `.pre-commit-config.yaml` uses `language: python` and `additional_dependencies` so pre-commit will install the pinned versions above into per-hook venvs.
- Sanitization and validation happen after token normalization: this ensures length checks reflect the actual characters that will appear in filenames.
- The `slug_sentinel_list` helper truncates aggregated slugs to 64 characters; `build_proposals` performs the final filename pattern and length validation.

Grouping and sequence assignment
--------------------------------
- Sequence numbers are assigned globally per `[PREFIX]_[SENTINEL-TOKENS]` across the provided `--test-root`. The implementation groups files by the base prefix (for example, `test_alpha`) and assigns an incrementing sequence to all files that share that base across the entire test-root.
- This means the base name `[PREFIX]_[SENTINEL-TOKENS]` must be unique across the `--test-root`. If two files in different directories would produce the same base, the resulting proposed filenames will collide unless you change the `--prefix`, the sentinel values, or exclude one of the directories via `--exclude`.
- If a file is not a child of the provided `--test-root`, its absolute parent directory is used for path resolution, but the sequence assignment is still global per prefix across the run.

Sanitization & token rules
--------------------------
- Allowed token characters: after sanitization tokens will contain only letters (A-Z, a-z), digits (0-9) and underscores. Any other characters are replaced with an underscore. Repeated underscores are collapsed to a single underscore and leading/trailing underscores are removed.
- Case preservation: token case is preserved (the tool does not lowercase tokens). Filenames are therefore case-sensitive and tokens are delimited with underscores.
- Prefix: use the `--prefix` CLI flag to set the leading filename prefix (default: `test`). The prefix must match the regex `^[A-Za-z][A-Za-z0-9_]*$` and may be up to 64 characters.

Rationale
---------
These limits are conservative and protect users from accidental platform-specific filename failures (long filenames, special characters). The sanitization rules keep tokens portable while preserving developer-intended casing. If you need configurable limits, we can expose these through CLI flags or a configuration file in a follow-up change.

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
python -m splurge_test_namer.cli --test-root tests --apply --force
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



