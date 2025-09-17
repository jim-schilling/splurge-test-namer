# splurge-test-namer

A small tool to rename test modules based on module-level sentinel lists (e.g. `DOMAINS = ['core','utils']`).

<!-- Badges: Block 1 - version / pypi / license -->

[![package version](https://img.shields.io/badge/version-2025.1.0-blue.svg)](d:/repos/splurge-test-namer/pyproject.toml)
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

Note: This release adds `--prefix` and `--fallback` flags to the CLI to control generated filename prefixes and the fallback domain used when no sentinel is present.

See `docs/README-DETAILS.md` for full API and design notes.

Features
--------
- Rename test modules using in-file sentinel lists like `DOMAINS = ['core', 'utils']`.
- Support for dynamic import detection (string literals, simple f-strings and concatenations) so the tool can follow imports to locate sentinel-defining modules.
- Member-fallback resolution for imports that reference attributes (e.g. `from pkg import names` -> resolves `pkg.names`).
- CLI flags:
	- `--test-root` : directory containing test modules to analyze (default: `tests`).
	- `--import-root` / `--repo-root` : follow imports under a root package in your repository.
	- `--exclude` : file/directory patterns to ignore when searching for tests or imports.
	- `--apply` : actually rename files; omit to run a dry-run preview.
	- `--debug` : enable verbose debug logging to troubleshoot resolution and import-following behavior.

	Sentinel name (default)
	-----------------------
	By default the tool looks for a module-level sentinel list named `DOMAINS`. This default is configurable via the `--sentinel` CLI flag (see `tools/rename_tests_by_sentinels.py` for a small helper script that demonstrates this flag). The lookup behavior is:

	- Primary source: a `DOMAINS` list defined in the test module itself. If present, that list is used as the authoritative set of domain slugs for renaming.
	- Fallback: if the test module lacks a sentinel, the tool optionally walks the import chain (see "How renaming works") to find a `DOMAINS` list defined in imported modules. A sentinel discovered via import-walking is treated as a fallback source.

Quick start
-----------
1. Dry-run (preview what would be renamed):

```bash
python -m splurge_test_namer.cli --test-root tests
```

2. Apply renames for real:

```bash
python -m splurge_test_namer.cli --test-root tests --apply
```

3. To follow imports from a package in your repo (so sentinels defined in other modules are discovered):

```bash
python -m splurge_test_namer.cli --test-root tests --import-root my_package --repo-root /path/to/repo
```

Run the installed console script
-------------------------------
After installing the package (for example `pip install .` or `pip install splurge-test-namer`), the project installs a console script named `splurge-test-namer` (see `[project.scripts]` in `pyproject.toml`). You can run the same commands via that script:

```bash
# dry-run using installed script
splurge-test-namer --test-root tests

# apply renames
splurge-test-namer --test-root tests --apply

# follow imports from a package under your repo
splurge-test-namer --test-root tests --import-root my_package --repo-root /path/to/repo
```

Examples
--------
- Rename tests that declare `DOMAINS` at module level to include domain slugs in filenames.
- Exclude files or directories during analysis:

```bash
python -m splurge_test_namer.cli --test-root tests --exclude tests/e2e --exclude tools
```

Before / After example
-----------------------
Given a test module with no descriptive name:

Before:

```
tests/unit/test_0001.py
```

And the file contains a sentinel list at module-level like:

```python
# tests/unit/test_0001.py
DOMAINS = ['core', 'utils']
def test_feature():
		assert True
```

After running with `--apply`, the file will be renamed to follow the pattern:

```
tests/unit/test_core_utils_0001.py
```

Filename pattern
----------------
- Renamed test files follow the pattern: `test_[domains]_nnnn.py` where:
- `[domains]` is an underscore-separated (snake_case) list of domain slugs taken from the sentinel (order is preserved from the list).
- `nnnn` is the original numerical suffix retained to avoid breaking test discovery order (zero-padded as in the original name when present).

Sequence numbering behavior
---------------------------
- Sequence numbers are assigned per test sub-folder under the provided `--test-root`. That is, numbering resets for each directory relative to `--test-root` so you may have files with the same sequence in different sub-folders (for example, `tests/unit/test_cli_0001.py` and `tests/e2e/test_cli_0001.py`).
- If a file isn't located under the provided `--test-root` the sequence grouping falls back to the file's parent directory path.

Limits
------
To keep generated filenames predictable and safe across platforms, the tool enforces a few limits (these are conservative and intended to avoid cross-platform filename issues):

Sentinel & filename limits
--------------------------
The tool enforces conservative, portable limits and sanitization rules to keep generated filenames safe across platforms:

- Sentinel token length: each sentinel value (each item in `DOMAINS` or your configured sentinel list) must be at most 64 characters. Values longer than 64 characters will cause the tool to raise `SplurgeTestNamerError` with a message identifying the offending token.
- Fallback token length: the `--fallback` value (or the default fallback used when no sentinel is found) must also be at most 64 characters; an oversized fallback raises `SplurgeTestNamerError`.
- Proposed filename length: the resulting proposed filename (for example `<PREFIX>_[domains]_nnnn.py`) is validated to be at most 240 characters. If a proposed filename would exceed this limit a `SplurgeTestNamerError` is raised explaining the offending proposed name and the original path.

Sanitization details (summary):
- Allowed token characters after sanitization: ASCII letters, digits and underscore.
- Repeated underscores collapse to single underscore; leading/trailing underscores removed.
- Case is preserved (tokens are case-sensitive).

Sanitization and patterns
-------------------------
- Allowed token characters: after sanitization tokens will contain only letters (A-Z, a-z), digits (0-9) and underscores. Any other characters are replaced with an underscore. Repeated underscores are collapsed to a single underscore and leading/trailing underscores are removed.
- Case preservation: token case is preserved (the tool does not lowercase tokens). Filenames are therefore case-sensitive and tokens are delimited with underscores.
- Prefix: use the `--prefix` CLI flag to set the leading filename prefix (default: `test`). The prefix must match the regex `^[A-Za-z][A-Za-z0-9_]*$` and may be up to 64 characters.

Examples:

- Valid sentinel: `['Core', 'utils']` → domains slug `Core_utils` (OK, case preserved)
- Too-long sentinel: `['this_is_a_very_long_sentinel_value_exceeding_sixty_four_characters_...']` → error

These limits are conservative and help avoid platform-specific filename failures. If you need different limits, consider pre-processing sentinel values before invoking the tool or open an issue to discuss configurability.

How renaming works (import-chain walking)
----------------------------------------
1. Parse test modules to find a module-level sentinel (by default `DOMAINS`, but the parser can be adapted).
2. If a sentinel is present in the test module, use it directly to compute the new filename.
3. If a sentinel is not present, the tool optionally follows imports from the test module to locate sentinel definitions:
	 - The tool performs conservative static analysis on imports using the AST. It resolves:
		 - Static imports (e.g. `from pkg import names`, `import pkg.module`).
		 - Simple dynamic import expressions where the module name is a string literal, a constant NAME (simple assignment), a small concatenation (BinOp with strings), or a simple f-string / JoinedStr that resolves to a literal at parse time.
	 - When the import references a member (e.g. `from pkg import names`), the tool attempts a member-fallback resolution (look for `pkg.names` as a module or an attribute in `pkg`).
	 - The resolver maps import names to file paths under the provided `--repo-root` and `--import-root` boundaries. It avoids following external packages (only repo-scoped modules are searched).
4. If multiple sentinel sources are found while walking imports, the tool aggregates them (the first found per module chain is used by default; aggregation behavior can be configured in advanced options).

Edge cases & assumptions
------------------------
- The import-walking is conservative: it intentionally avoids executing project code and only considers static patterns that can be resolved safely.
- Complex runtime constructions (e.g. names built from environment variables, network calls, or loops) are not evaluated.
- If no sentinel is found after import-walking, the default behavior is to rename the test using a misc fallback: the domain portion becomes `misc` and the file is renamed to `test_misc_nnnn.py`. This keeps naming consistent for tests that lack sentinel metadata. You can change this behavior via configuration or by providing a custom sentinel name with `--sentinel`.


Links
-----
- CHANGELOG: see `CHANGELOG.md` for release notes and history.
- Full documentation: `docs/README-DETAILS.md` (design notes, API, internals)

